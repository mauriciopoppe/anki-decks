import sqlite3
import os
import zipfile
import shutil
import zstandard as zstd
import google.generativeai as genai
import time
import sys
import markdown
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Configuration
EXTRACT_DIR = "temp_augment"
# Target the 4-field model: Text, Frequency, Notes, Image
MODEL_ID = 1707079291580
FIELD_INDEX_TEXT = 0
FIELD_INDEX_NOTES = 2

# Gemini Setup
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY environment variable not set.")
    sys.exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-3-flash-preview")


def setup_environment(apkg_file):
    if os.path.exists(EXTRACT_DIR):
        shutil.rmtree(EXTRACT_DIR)
    os.makedirs(EXTRACT_DIR)

    print(f"Extracting {apkg_file}...")
    with zipfile.ZipFile(apkg_file, "r") as zip_ref:
        zip_ref.extractall(EXTRACT_DIR)

    # We will work on a single database file and then replicate it
    # Prefer decompressing 21b if it exists, otherwise use 2
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


def generate_notes(text):
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
        response = model.generate_content(prompt)
        text_content = response.text.strip()
        # Convert Markdown to HTML
        html_content = markdown.markdown(text_content)
        return html_content
    except Exception as e:
        # Simple retry logic or just logging
        print(f"Error generating content for '{text[:20]}...': {e}")
        return ""


def process_note(nid, flds):
    parts = flds.split("\x1f")

    # Ensure we have enough fields
    while len(parts) <= FIELD_INDEX_NOTES:
        parts.append("")

    current_note = parts[FIELD_INDEX_NOTES]

    # Only fill if empty
    if not current_note.strip():
        text = parts[FIELD_INDEX_TEXT]
        generated_note = generate_notes(text)
        if generated_note:
            parts[FIELD_INDEX_NOTES] = generated_note
            new_flds = "\x1f".join(parts)
            return (new_flds, int(time.time()), nid)

    return None


def process_deck(apkg_file, output_file):
    working_db = setup_environment(apkg_file)
    conn = sqlite3.connect(working_db)
    cursor = conn.cursor()

    print(f"Querying notes for Model {MODEL_ID}...")
    cursor.execute("SELECT id, flds FROM notes WHERE mid=?", (MODEL_ID,))
    notes = cursor.fetchall()

    print(f"Found {len(notes)} total notes.")

    # Identify notes that actually need processing
    notes_to_process = []
    for nid, flds in notes:
        parts = flds.split("\x1f")
        if len(parts) <= FIELD_INDEX_NOTES or not parts[FIELD_INDEX_NOTES].strip():
            notes_to_process.append((nid, flds))

    print(f"Found {len(notes_to_process)} notes that require augmentation.")

    updates = []

    if notes_to_process:
        # 500 RPM / 60s ~ 8.3 requests/sec.
        # With 15 workers we can hit higher if latency is low, but usually safe.
        max_workers = 15
        print(f"Starting parallel processing with {max_workers} workers...")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(process_note, nid, flds)
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

    # 1. Update collection.anki2
    shutil.copy(working_db, os.path.join(EXTRACT_DIR, "collection.anki2"))

    # 2. Compress to collection.anki21b
    print("Compressing to collection.anki21b...")
    cctx = zstd.ZstdCompressor()
    with (
        open(working_db, "rb") as ifh,
        open(os.path.join(EXTRACT_DIR, "collection.anki21b"), "wb") as ofh,
    ):
        cctx.copy_stream(ifh, ofh)

    # 3. Zip it all
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Augment Anki deck with AI-generated notes."
    )
    parser.add_argument("--input", required=True, help="Input .apkg file path")
    parser.add_argument("--output", required=True, help="Output .apkg file path")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1)

    process_deck(args.input, args.output)

