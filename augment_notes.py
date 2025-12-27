import sqlite3
import os
import zipfile
import shutil
import zstandard as zstd
from google import genai
import time
import sys
import markdown
import argparse
import requests
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Configuration
EXTRACT_DIR = "temp_augment"

# Gemini Setup
api_key = os.environ.get("GEMINI_API_KEY")


def setup_gemini():
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        sys.exit(1)
    return genai.Client(api_key=api_key)


def setup_environment(apkg_file):
    if os.path.exists(EXTRACT_DIR):
        shutil.rmtree(EXTRACT_DIR)
    os.makedirs(EXTRACT_DIR)

    print(f"Extracting {apkg_file}...")
    with zipfile.ZipFile(apkg_file, "r") as zip_ref:
        zip_ref.extractall(EXTRACT_DIR)

    # We will work on a single database file and then replicate it
    db_path_21b = os.path.join(EXTRACT_DIR, "collection.anki21b")
    db_path_2 = os.path.join(EXTRACT_DIR, "collection.anki2")

    working_db_path = os.path.join(EXTRACT_DIR, "collection_working.db")

    if os.path.exists(db_path_21b):
        print("Decompressing collection.anki21b to use as working DB...")
        dctx = zstd.ZstdDecompressor()
        with open(db_path_21b, "rb") as ifh, open(working_db_path, "wb") as ofh:
            dctx.copy_stream(ifh, ofh)
    else:
        print("Using collection.anki2 as working DB...")
        shutil.copy(db_path_2, working_db_path)

    return working_db_path


def get_model_id_from_name(conn, model_name):
    """
    Resolves a model name to an ID by querying the 'notetypes' table.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM notetypes")
    all_types = cursor.fetchall()
    for nid, name in all_types:
        if name == model_name:
            return nid
    return None


def get_field_map(conn, ntid):
    """
    Retrieves a mapping of field name to index for the given note type ID.
    Returns: { "FieldName": index, ... }
    """
    cursor = conn.cursor()
    cursor.execute("SELECT name, ord FROM fields WHERE ntid=?", (ntid,))
    fields = cursor.fetchall()
    return {name: ord_val for name, ord_val in fields}


def extract_required_fields(prompt_template):
    """
    Extracts field names required by the prompt (e.g. "{Text}" -> ["Text"]).
    """
    return re.findall(r'\{(\w+)\}', prompt_template)


def generate_content(client, prompt):
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview", contents=prompt
        )
        text_content = response.text.strip()
        # Convert Markdown to HTML
        html_content = markdown.markdown(text_content)
        return html_content
    except Exception as e:
        print(f"Error generating content: {e}")
        return ""

def process_note_file(client, nid, flds, field_map, target_field, prompt_template, required_fields):
    parts = flds.split("\x1f")
    
    # Check if target field exists in the map
    if target_field not in field_map:
        return None
    
    target_idx = field_map[target_field]

    # Ensure we have enough fields
    max_idx = max(field_map.values())
    while len(parts) <= max_idx:
        parts.append("")

    current_val = parts[target_idx]

    # Only fill if empty
    if not current_val.strip():
        # Build context for prompt
        context = {}
        missing_field = False
        for field in required_fields:
            if field in field_map:
                context[field] = parts[field_map[field]]
            else:
                # Required field not found in note type
                missing_field = True
                break
        
        if missing_field:
            return None

        try:
            filled_prompt = prompt_template.format(**context)
            generated_content = generate_content(client, filled_prompt)
            if generated_content:
                parts[target_idx] = generated_content
                new_flds = "\x1f".join(parts)
                return (new_flds, int(time.time()), nid)
        except KeyError as e:
            print(f"Error formatting prompt for note {nid}: Missing field {e}")
            return None

    return None

def process_deck_file(apkg_file, output_file, note_type, target_field, prompt_template, dry_run=False):
    working_db = setup_environment(apkg_file)
    conn = sqlite3.connect(working_db)

    resolved_mid = get_model_id_from_name(conn, note_type)
    if not resolved_mid:
        print(f"Error: Could not find model with name '{note_type}' in the database.")
        conn.close()
        sys.exit(1)
    print(f"Resolved model name '{note_type}' to ID {resolved_mid}")

    field_map = get_field_map(conn, resolved_mid)
    
    if target_field not in field_map:
        print(f"Error: Target field '{target_field}' not found in model '{note_type}'.")
        print(f"Available fields: {list(field_map.keys())}")
        conn.close()
        sys.exit(1)

    required_fields = extract_required_fields(prompt_template)
    for field in required_fields:
        if field not in field_map:
            print(f"Error: Required field '{field}' (from prompt) not found in model '{note_type}'.")
            print(f"Available fields: {list(field_map.keys())}")
            conn.close()
            sys.exit(1)

    print(f"Target Field: {target_field} (Index {field_map[target_field]})")
    print(f"Required Source Fields: {required_fields}")

    cursor = conn.cursor()
    print(f"Querying notes for Model ID {resolved_mid}...")
    cursor.execute("SELECT id, flds FROM notes WHERE mid=?", (resolved_mid,))
    notes = cursor.fetchall()

    print(f"Found {len(notes)} total notes.")

    target_idx = field_map[target_field]
    notes_to_process = []
    for nid, flds in notes:
        parts = flds.split("\x1f")
        if len(parts) <= target_idx or not parts[target_idx].strip():
            notes_to_process.append((nid, flds))

    print(f"Found {len(notes_to_process)} notes that require augmentation.")

    if dry_run:
        print("\n--- Dry Run: Notes to be updated ---")
        for nid, flds in notes_to_process:
            parts = flds.split("\x1f")
            # Show the first required field as a preview
            preview_field = required_fields[0] if required_fields else target_field
            preview_idx = field_map.get(preview_field, 0)
            text = parts[preview_idx] if len(parts) > preview_idx else "[Empty]"
            display_text = text.replace("\n", " ")[:80]
            print(f"ID: {nid} | {preview_field}: {display_text}...")
        print("\nDry run complete. No changes made.")
        conn.close()
        return

    updates = []
    if notes_to_process:
        client = setup_gemini()
        max_workers = 15
        print(f"Starting parallel processing with {max_workers} workers...")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(process_note_file, client, nid, flds, field_map, target_field, prompt_template, required_fields)
                for nid, flds in notes_to_process
            ]

            for future in tqdm(
                as_completed(futures),
                total=len(notes_to_process),
                desc="Augmenting Notes",
            ):
                result = future.result()
                if result:
                    updates.append(result)

    if updates:
        print(f"Updating {len(updates)} notes in database...")
        cursor.executemany("UPDATE notes SET flds=?, mod=? WHERE id=?", updates)
        conn.commit()
    else:
        print("No updates needed.")

    conn.close()

    # Repackaging
    print("Preparing output files...")
    shutil.copy(working_db, os.path.join(EXTRACT_DIR, "collection.anki2"))
    print("Compressing to collection.anki21b...")
    cctx = zstd.ZstdCompressor()
    with (
        open(working_db, "rb") as ifh,
        open(os.path.join(EXTRACT_DIR, "collection.anki21b"), "wb") as ofh,
    ):
        cctx.copy_stream(ifh, ofh)

    print(f"Creating {output_file}...")
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(EXTRACT_DIR):
            for file in files:
                if file in [
                    "collection_working.db",
                    "collection_legacy.anki2",
                    "collection_new.anki2",
                ]:
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, EXTRACT_DIR)
                zipf.write(file_path, arcname)

    print(f"Done! Created {output_file}")


# --- AnkiConnect Integration ---


def invoke_anki(action, **params):
    try:
        request_json = json.dumps({"action": action, "version": 6, "params": params})
        response = requests.post("http://localhost:8765", data=request_json).json()
        if len(response) != 2:
            raise Exception("response has an unexpected number of fields")
        if response["error"] is not None:
            raise Exception(response["error"])
        return response["result"]
    except requests.exceptions.ConnectionError:
        print(
            "Error: Could not connect to AnkiConnect. Is Anki running and AnkiConnect installed?"
        )
        sys.exit(1)
    except Exception as e:
        print(f"AnkiConnect Error: {e}")
        sys.exit(1)


def process_note_live(client, nid, note_fields, target_field, prompt_template, required_fields):
    # note_fields is a dict: { "FieldName": "Value", ... }
    
    # Check if target is empty
    if note_fields.get(target_field, "").strip():
        return None

    # Build context
    context = {}
    for field in required_fields:
        if field in note_fields:
            context[field] = note_fields[field]
        else:
            return None # Should have been caught earlier, but safe check

    try:
        filled_prompt = prompt_template.format(**context)
        generated_content = generate_content(client, filled_prompt)
        if generated_content:
            return (nid, generated_content)
    except KeyError as e:
        print(f"Error formatting prompt for note {nid}: Missing field {e}")
        return None
    
    return None

def process_deck_ankiconnect(note_type, target_field, prompt_template, dry_run=False):
    print(f"Querying Anki for Note Type: '{note_type}'...")
    query = f'note:"{note_type}"'
    note_ids = invoke_anki("findNotes", query=query)

    if not note_ids:
        print("No notes found for this query.")
        return

    print(f"Found {len(note_ids)} notes. Fetching details...")

    batch_size = 500
    notes_to_process = []
    
    required_fields = extract_required_fields(prompt_template)

    # Check first note to verify fields exist
    if note_ids:
        first_info = invoke_anki("notesInfo", notes=note_ids[:1])[0]
        fields = first_info["fields"]
        
        if target_field not in fields:
            print(f"Error: Target field '{target_field}' not found in note type '{note_type}'.")
            return
            
        for rf in required_fields:
            if rf not in fields:
                print(f"Error: Required field '{rf}' (from prompt) not found in note type '{note_type}'.")
                return
        
        print(f"Verified fields: Target='{target_field}', Source={required_fields}")

    for i in range(0, len(note_ids), batch_size):
        batch = note_ids[i : i + batch_size]
        infos = invoke_anki("notesInfo", notes=batch)

        for info in infos:
            # We construct a simple dict { "FieldName": "Value" }
            note_fields = {k: v["value"] for k, v in info["fields"].items()}
            
            # Filter logic: if target is empty
            if not note_fields.get(target_field, "").strip():
                # We store the whole note_fields because we might need multiple source fields
                notes_to_process.append({"id": info["noteId"], "fields": note_fields})

    print(f"Found {len(notes_to_process)} notes that require augmentation.")

    if dry_run:
        print("\n--- Dry Run: Notes to be updated via AnkiConnect ---")
        for n in notes_to_process:
            # Preview using first required field
            preview_field = required_fields[0] if required_fields else target_field
            preview_text = n["fields"].get(preview_field, "[Missing]")
            display_text = preview_text.replace("\n", " ")[:80]
            print(f"ID: {n['id']} | {preview_field}: {display_text}...")
        print("\nDry run complete. No changes made.")
        return

    if not notes_to_process:
        print("No updates needed.")
        return

    client = setup_gemini()
    max_workers = 15
    print(f"Starting parallel processing with {max_workers} workers...")

    updates = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(process_note_live, client, n["id"], n["fields"], target_field, prompt_template, required_fields)
            for n in notes_to_process
        ]

        for future in tqdm(
            as_completed(futures), total=len(notes_to_process), desc="Augmenting Notes"
        ):
            result = future.result()
            if result:
                updates.append(result)

    if updates:
        print(f"Updating {len(updates)} notes via AnkiConnect...")
        for nid, new_content in tqdm(updates, desc="Sending updates to Anki"):
            invoke_anki(
                "updateNoteFields",
                note={"id": nid, "fields": {target_field: new_content}},
            )
        print("Done!")
    else:
        print("No notes generated.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Augment Anki deck with AI-generated content."
    )

    parser.add_argument(
        "--anki-connect",
        action="store_true",
        help="Use AnkiConnect to update running Anki instance",
    )
    parser.add_argument(
        "--note-type",
        required=True,
        help="Anki Model (Note Type) Name",
    )
    parser.add_argument("--input", help="Input .apkg file path")
    parser.add_argument("--output", help="Output .apkg file path")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Identify and list notes without processing",
    )
    parser.add_argument(
        "--target-field",
        required=True,
        help="The field to fill (e.g. 'Notes', 'Mnemonic')",
    )
    parser.add_argument(
        "--prompt-file",
        required=True,
        help="Path to a text file containing the prompt template. Use {FieldName} for placeholders.",
    )

    args = parser.parse_args()
    
    if os.path.exists(args.prompt_file):
        with open(args.prompt_file, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
    else:
        print(f"Error: Prompt file '{args.prompt_file}' not found.")
        sys.exit(1)

    if args.anki_connect:
        process_deck_ankiconnect(
            note_type=args.note_type,
            target_field=args.target_field,
            prompt_template=prompt_template,
            dry_run=args.dry_run
        )
    else:
        if not args.input or not args.output:
            print(
                "Error: --input and --output are required when not using --anki-connect."
            )
            sys.exit(1)
        if not os.path.exists(args.input):
            print(f"Error: Input file '{args.input}' not found.")
            sys.exit(1)

        process_deck_file(
            args.input,
            args.output,
            note_type=args.note_type,
            target_field=args.target_field,
            prompt_template=prompt_template,
            dry_run=args.dry_run
        )
