import os
import sys
import markdown
import argparse
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from google import genai

# Configuration
DEFAULT_MODEL_NAME = "Lapis"
SOURCE_FIELD_NAME = "Expression"
TARGET_FIELD_NAME = "Mnemonic"
READING_FIELD_NAME = "ExpressionReading"

# Gemini Setup
api_key = os.environ.get("GEMINI_API_KEY")


def setup_gemini():
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        sys.exit(1)
    return genai.Client(api_key=api_key)


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
            "Error: Could not connect to AnkiConnect. "
            "Is Anki running and AnkiConnect installed?"
        )
        sys.exit(1)
    except Exception as e:
        print(f"AnkiConnect Error: {e}")
        sys.exit(1)


def generate_mnemonic(client, expression, reading):
    prompt = f"""
    Generate a creative and memorable mnemonic for the Japanese word:
    "{expression}" (Reading: "{reading}").

    Follow this exact format:
    The Mnemonic: "[Title]"

    Meaning: [Brief Meaning] ({expression}).

    Shape: [Visual connection to the kanji strokes, components, or overall shape]

    Sound: [Sound mnemonic, pun, or story connecting the reading to the meaning]
    ({reading}).

    Example for お皿 (Plate):
    The Mnemonic: "The Broken Heirloom"
    Meaning: A plate (お皿).
    Shape: It breaks into 5 pieces (matching the 5 strokes of 皿).
    Sound: You gasp, "Oh... Sarah!" (おさら).
    """
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview", contents=prompt
        )
        text_content = response.text.strip()
        # Convert Markdown to HTML to ensure it renders nicely in Anki
        html_content = markdown.markdown(text_content)
        return html_content
    except Exception as e:
        print(f"Error generating content for '{expression}': {e}")
        return ""


def process_note_live(client, nid, source_text, reading_text):
    mnemonic = generate_mnemonic(client, source_text, reading_text)
    if mnemonic:
        return (nid, mnemonic)
    return None


def process_deck_ankiconnect(model_name, dry_run=False):
    print(f"Querying Anki for Note Type: '{model_name}'...")
    query = f'note:"{model_name}"'
    note_ids = invoke_anki("findNotes", query=query)

    if not note_ids:
        print("No notes found for this query.")
        return

    print(f"Found {len(note_ids)} notes. Fetching details...")

    batch_size = 500
    notes_to_process = []

    # Field check
    first_batch = invoke_anki("notesInfo", notes=note_ids[:1])
    if not first_batch:
        print("Error: Could not retrieve note info.")
        return

    fields = first_batch[0]["fields"]
    if SOURCE_FIELD_NAME not in fields:
        print(
            f"Error: Source field '{SOURCE_FIELD_NAME}' "
            f"not found in note type '{model_name}'."
        )
        return
    if TARGET_FIELD_NAME not in fields:
        print(
            f"Error: Target field '{TARGET_FIELD_NAME}' "
            f"not found in note type '{model_name}'."
        )
        return
    if READING_FIELD_NAME not in fields:
        print(
            f"Error: Reading field '{READING_FIELD_NAME}' "
            f"not found in note type '{model_name}'."
        )
        return

    print(
        f"Verified fields: Source='{SOURCE_FIELD_NAME}', "
        f"Reading='{READING_FIELD_NAME}', Target='{TARGET_FIELD_NAME}'"
    )

    for i in range(0, len(note_ids), batch_size):
        batch = note_ids[i : i + batch_size]
        infos = invoke_anki("notesInfo", notes=batch)

        for info in infos:
            target_value = info["fields"][TARGET_FIELD_NAME]["value"]

            # Check if target is empty
            if not target_value.strip():
                source_value = info["fields"][SOURCE_FIELD_NAME]["value"]
                reading_value = info["fields"][READING_FIELD_NAME]["value"]
                # Clean source value (remove HTML if any)
                # Simple check to avoid processing empty source
                if source_value.strip():
                    notes_to_process.append(
                        {
                            "id": info["noteId"],
                            "text": source_value,
                            "reading": reading_value,
                        }
                    )

    print(f"Found {len(notes_to_process)} notes that require augmentation.")

    if dry_run:
        print("\n--- Dry Run: Notes to be updated ---")
        for n in notes_to_process:
            display_text = n["text"].replace("\n", " ")[:80]
            display_reading = n["reading"].replace("\n", " ")[:80]
            print(
                f"ID: {n['id']} | Expression: {display_text} | "
                f"Reading: {display_reading}..."
            )
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
            executor.submit(process_note_live, client, n["id"], n["text"], n["reading"])
            for n in notes_to_process
        ]

        for future in tqdm(
            as_completed(futures),
            total=len(notes_to_process),
            desc="Generating Mnemonics",
        ):
            result = future.result()
            if result:
                updates.append(result)

    if updates:
        print(f"Updating {len(updates)} notes via AnkiConnect...")
        for nid, new_content in tqdm(updates, desc="Sending updates to Anki"):
            invoke_anki(
                "updateNoteFields",
                note={"id": nid, "fields": {TARGET_FIELD_NAME: new_content}},
            )
        print("Done!")
    else:
        print("No notes generated.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Augment Anki 'Lapis' deck with AI-generated mnemonics."
    )

    parser.add_argument(
        "--model-name",
        default=DEFAULT_MODEL_NAME,
        help=f"Anki Note Type Name (default: '{DEFAULT_MODEL_NAME}')",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Identify and list notes without processing",
    )

    args = parser.parse_args()

    process_deck_ankiconnect(model_name=args.model_name, dry_run=args.dry_run)
