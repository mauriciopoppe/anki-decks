import os
import sys
import argparse
import requests
import json
import re
from tqdm import tqdm
from deep_translator import GoogleTranslator

def invoke_anki(action, **params):
    try:
        request_json = json.dumps({"action": action, "version": 6, "params": params})
        response = requests.post("http://localhost:8765", data=request_json).json()
        if response["error"] is not None:
            raise Exception(response["error"])
        return response["result"]
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to AnkiConnect. Is Anki running and AnkiConnect installed?")
        sys.exit(1)
    except Exception as e:
        print(f"AnkiConnect Error: {e}")
        sys.exit(1)

def normalize_cloze(text):
    """
    Removes Anki cloze formatting: {{c1::word::hint}} -> word
    """
    # Pattern: {{c\d+::content(::hint)?}}
    # \1 is the first group: content
    return re.sub(r"\{\{c\d+::(.*?)(::.*?)?\}\}", r"\1", text)

def translate_batch(texts):
    """
    Translates a list of strings to English using GoogleTranslator.
    """
    if not texts:
        return []
    try:
        # Attempt GoogleTranslator batch translation
        return GoogleTranslator(source='auto', target='en').translate_batch(texts)
    except Exception as e:
        print(f"GoogleTranslator Batch Error: {e}")
        return [None] * len(texts)

def check_and_warn_costs(num_notes):
    """
    Warns the user about potential impacts and asks for confirmation.
    """
    if num_notes == 0:
        return True

    print("\n" + "!" * 60)
    print("WARNING: You are about to process translations.")
    print(f"You are about to process {num_notes} notes.")
    print("This will make multiple requests to Google Translate.")
    print("!" * 60 + "\n")

    try:
        choice = input(f"Do you want to continue processing {num_notes} notes? (y/n): ").strip().lower()
        return choice in ["y", "yes"]
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        return False

def main():
    parser = argparse.ArgumentParser(description="Augment Anki deck with translations to English.")
    parser.add_argument("--deck", required=True, help="Anki Deck Name")
    parser.add_argument("--target-field", required=True, help="Field to store the translation")
    parser.add_argument("--source-field", default="Expression", help="Field containing text to translate (default: Expression)")
    parser.add_argument("--total-notes", type=int, default=20, help="Total number of notes to process")
    parser.add_argument("--batch-size", type=int, default=5, help="Translation batch size")
    parser.add_argument("--dry-run", action="store_true", help="Preview translations without updating Anki")
    
    args = parser.parse_args()
    
    print(f"Querying Anki for Deck: '{args.deck}'...")
    query = f'deck:"{args.deck}"'
    note_ids = invoke_anki("findNotes", query=query)
    
    if not note_ids:
        print(f"No notes found in deck '{args.deck}'.")
        return

    notes_info = invoke_anki("notesInfo", notes=note_ids)

    # Sort notes by FreqSort immediately
    print("Sorting notes by 'FreqSort'...")
    notes_info.sort(key=lambda x: int(x['fields'].get('FreqSort', {}).get('value', '999999') or '999999'))

    # Infer note type from first note
    note_type = notes_info[0]["modelName"]
    print(f"Inferred Note Type: '{note_type}' from first note.")

    print(f"Filtering notes that need translation...")
    
    notes_to_process = []
    for info in notes_info:
        fields = {k: v['value'] for k, v in info['fields'].items()}
        
        # Check if source field exists
        if args.source_field not in fields:
            continue
            
        # Filter: only if target field is empty
        if not fields.get(args.target_field, "").strip():
            notes_to_process.append({
                "id": info['noteId'],
                "source_text": fields[args.source_field]
            })

    # Limit to total-notes
    notes_to_process = notes_to_process[:args.total_notes]

    if not notes_to_process:
        print("No notes need translation.")
        return

    print(f"\nNotes to be processed ({len(notes_to_process)} total):")
    for n in notes_to_process:
        print(f"ID: {n['id']} | Source: {n['source_text'].replace('\n', ' ')[:80]}...")

    if args.dry_run:
        print("\nDry run complete. No changes made.")
        return

    if not check_and_warn_costs(len(notes_to_process)):
        print("Aborting.")
        return

    print(f"Processing {len(notes_to_process)} notes in batches of {args.batch_size}...")
    
    all_updates = []
    translation_cache = {}
    
    # 1. Normalize and identify unique texts to translate
    for note in notes_to_process:
        note['normalized'] = normalize_cloze(note['source_text'])

    unique_to_translate = list(set(n['normalized'] for n in notes_to_process))
    
    # 2. Translate unique texts in batches
    for i in tqdm(range(0, len(unique_to_translate), args.batch_size), desc="Translating batches"):
        batch_texts = unique_to_translate[i:i + args.batch_size]
        translated_batch = translate_batch(batch_texts)
        for original, translated in zip(batch_texts, translated_batch):
            if translated:
                translation_cache[original] = translated

    # 3. Map translations back to note IDs
    for note in notes_to_process:
        translated = translation_cache.get(note['normalized'])
        if translated:
            all_updates.append((note['id'], translated))

    if all_updates:
        print(f"Updating {len(all_updates)} notes in Anki...")
        for nid, translation in tqdm(all_updates, desc="Syncing to Anki"):
            invoke_anki("updateNoteFields", note={
                "id": nid,
                "fields": {
                    args.target_field: translation
                }
            })
        print("Done!")
    else:
        print("No updates generated.")

if __name__ == "__main__":
    main()
