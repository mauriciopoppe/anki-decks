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
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Configuration
EXTRACT_DIR = "temp_augment"
DEFAULT_NOTE_TYPE = "Cloze"
FIELD_INDEX_TEXT = 0
FIELD_INDEX_NOTES = 2

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
    Falls back to 'col' table 'models' column if 'notetypes' does not exist.
    """
    cursor = conn.cursor()
    
    # Check if 'notetypes' table exists (Newer Anki versions)
    try:
        cursor.execute("SELECT id, name FROM notetypes")
        all_types = cursor.fetchall()
        for nid, name in all_types:
            if name == model_name:
                return nid
    except sqlite3.OperationalError:
        pass # Table might not exist, fall back to legacy check

    # Legacy check: 'models' column in 'col' table
    cursor.execute("SELECT models FROM col")
    row = cursor.fetchone()
    if not row or not row[0]:
        return None
    
    models_raw = row[0]
    if isinstance(models_raw, bytes):
        models_json = models_raw.decode('utf-8')
    else:
        models_json = models_raw
        
    try:
        models = json.loads(models_json)
        for mid, mdata in models.items():
            if mdata['name'] == model_name:
                return int(mid)
    except json.JSONDecodeError:
        return None
        
    return None


def generate_notes(client, text):
    prompt = f"""
    Analyze the following French sentence/phrase found in an Anki card:
    "{text}"

    Provide a concise but helpful explanation suitable for the "Notes" field.
    1. Explain the meaning of the key vocabulary or the whole sentence.
    2. If there is a Cloze deletion ({{c1::...}}), focus on explaining the missing part.
    3. Point out any interesting grammar or usage.
    4. Keep it brief (under 50 words) and clear.
    5. Output ONLY the note content, no "Here is the note:" prefix.
    6. Use standard Markdown formatting (bold key terms, etc.).
    """
    try:
        response = client.models.generate_content(
            model='gemini-3-flash-preview', contents=prompt
        )
        text_content = response.text.strip()
        # Convert Markdown to HTML
        html_content = markdown.markdown(text_content)
        return html_content
    except Exception as e:
        print(f"Error generating content for '{text[:20]}...': {e}")
        return ""


def process_note_file(client, nid, flds):
    parts = flds.split("\x1f")

    # Ensure we have enough fields
    while len(parts) <= FIELD_INDEX_NOTES:
        parts.append("")

    current_note = parts[FIELD_INDEX_NOTES]

    # Only fill if empty
    if not current_note.strip():
        text = parts[FIELD_INDEX_TEXT]
        generated_note = generate_notes(client, text)
        if generated_note:
            parts[FIELD_INDEX_NOTES] = generated_note
            new_flds = "\x1f".join(parts)
            return (new_flds, int(time.time()), nid)

    return None


def process_deck_file(apkg_file, output_file, model_name, dry_run=False):
    working_db = setup_environment(apkg_file)
    conn = sqlite3.connect(working_db)
    
    resolved_mid = get_model_id_from_name(conn, model_name)
    if not resolved_mid:
        print(f"Error: Could not find model with name '{model_name}' in the database.")
        conn.close()
        sys.exit(1)
    print(f"Resolved model name '{model_name}' to ID {resolved_mid}")

    cursor = conn.cursor()
    print(f"Querying notes for Model ID {resolved_mid}...")
    cursor.execute("SELECT id, flds FROM notes WHERE mid=?", (resolved_mid,))
    notes = cursor.fetchall()

    print(f"Found {len(notes)} total notes.")

    notes_to_process = []
    for nid, flds in notes:
        parts = flds.split("\x1f")
        if len(parts) <= FIELD_INDEX_NOTES or not parts[FIELD_INDEX_NOTES].strip():
            notes_to_process.append((nid, flds))

    print(f"Found {len(notes_to_process)} notes that require augmentation.")

    if dry_run:
        print("\n--- Dry Run: Notes to be updated ---")
        for nid, flds in notes_to_process:
            parts = flds.split("\x1f")
            text = parts[FIELD_INDEX_TEXT] if len(parts) > FIELD_INDEX_TEXT else "[No Text]"
            display_text = text.replace('\n', ' ')[:80]
            print(f"ID: {nid} | Text: {display_text}...")
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
                executor.submit(process_note_file, client, nid, flds)
                for nid, flds in notes_to_process
            ]

            for future in tqdm(as_completed(futures), total=len(notes_to_process), desc="Augmenting Notes"):
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
    with open(working_db, "rb") as ifh, open(os.path.join(EXTRACT_DIR, "collection.anki21b"), "wb") as ofh:
        cctx.copy_stream(ifh, ofh)

    print(f"Creating {output_file}...")
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(EXTRACT_DIR):
            for file in files:
                if file in ["collection_working.db", "collection_legacy.anki2", "collection_new.anki2"]:
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, EXTRACT_DIR)
                zipf.write(file_path, arcname)

    print(f"Done! Created {output_file}")


# --- AnkiConnect Integration ---

def invoke_anki(action, **params):
    try:
        request_json = json.dumps({"action": action, "version": 6, "params": params})
        response = requests.post('http://localhost:8765', data=request_json).json()
        if len(response) != 2:
            raise Exception('response has an unexpected number of fields')
        if response['error'] is not None:
            raise Exception(response['error'])
        return response['result']
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to AnkiConnect. Is Anki running and AnkiConnect installed?")
        sys.exit(1)
    except Exception as e:
        print(f"AnkiConnect Error: {e}")
        sys.exit(1)

def process_note_live(client, nid, current_text):
    generated_note = generate_notes(client, current_text)
    if generated_note:
        return (nid, generated_note)
    return None

def process_deck_ankiconnect(model_name, dry_run=False):
    print(f"Querying Anki for Model Name: '{model_name}'...")
    query = f'note:"{model_name}"'
    note_ids = invoke_anki("findNotes", query=query)
    
    if not note_ids:
        print("No notes found for this query.")
        return

    print(f"Found {len(note_ids)} notes. Fetching details...")
    
    batch_size = 500
    notes_to_process = []
    
    field_name_text = None
    field_name_notes = None
    
    for i in range(0, len(note_ids), batch_size):
        batch = note_ids[i:i + batch_size]
        infos = invoke_anki("notesInfo", notes=batch)
        
        for info in infos:
            if field_name_text is None:
                fields = info['fields']
                for fname, fval in fields.items():
                    if fval['order'] == FIELD_INDEX_TEXT:
                        field_name_text = fname
                    elif fval['order'] == FIELD_INDEX_NOTES:
                        field_name_notes = fname
                
                if not field_name_text or not field_name_notes:
                    print(f"Error: Could not map field indices to names. Text: {field_name_text}, Notes: {field_name_notes}")
                    sys.exit(1)
                print(f"Mapped fields: Text='{field_name_text}', Notes='{field_name_notes}'")

            note_content = info['fields'][field_name_notes]['value']
            if not note_content.strip():
                text_content = info['fields'][field_name_text]['value']
                notes_to_process.append({
                    "id": info['noteId'],
                    "text": text_content
                })

    print(f"Found {len(notes_to_process)} notes that require augmentation.")
    
    if dry_run:
        print("\n--- Dry Run: Notes to be updated via AnkiConnect ---")
        for n in notes_to_process:
            display_text = n['text'].replace('\n', ' ')[:80]
            print(f"ID: {n['id']} | Text: {display_text}...")
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
            executor.submit(process_note_live, client, n['id'], n['text'])
            for n in notes_to_process
        ]

        for future in tqdm(as_completed(futures), total=len(notes_to_process), desc="Augmenting Notes"):
            result = future.result()
            if result:
                updates.append(result)

    if updates:
        print(f"Updating {len(updates)} notes via AnkiConnect...")
        for nid, new_content in tqdm(updates, desc="Sending updates to Anki"):
            invoke_anki("updateNoteFields", note={"id": nid, "fields": {field_name_notes: new_content}})
        print("Done!")
    else:
        print("No notes generated.")
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Augment Anki deck with AI-generated notes.")
    
    parser.add_argument("--anki-connect", action="store_true", help="Use AnkiConnect to update running Anki instance")
    parser.add_argument("--note-type", default=DEFAULT_NOTE_TYPE, help=f"Anki Model (Note Type) Name (default: '{DEFAULT_NOTE_TYPE}')")
    parser.add_argument("--input", help="Input .apkg file path")
    parser.add_argument("--output", help="Output .apkg file path")
    parser.add_argument("--dry-run", action="store_true", help="Identify and list notes without processing")
    
    args = parser.parse_args()

    if args.anki_connect:
        process_deck_ankiconnect(model_name=args.model_name, dry_run=args.dry_run)
    else:
        if not args.input or not args.output:
            print("Error: --input and --output are required when not using --anki-connect.")
            sys.exit(1)
        if not os.path.exists(args.input):
            print(f"Error: Input file '{args.input}' not found.")
            sys.exit(1)

        process_deck_file(args.input, args.output, model_name=args.model_name, dry_run=args.dry_run)
