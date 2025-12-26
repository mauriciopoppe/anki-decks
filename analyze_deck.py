import zipfile
import sqlite3
import json
import os
import shutil
import zstandard as zstd

apkg_file = "French__My french words and phrases.apkg"
extract_dir = "temp_extraction"

# Clean up previous runs
if os.path.exists(extract_dir):
    shutil.rmtree(extract_dir)
os.makedirs(extract_dir)

print(f"Extracting {apkg_file}...")
try:
    with zipfile.ZipFile(apkg_file, "r") as zip_ref:
        zip_ref.extractall(extract_dir)
except zipfile.BadZipFile:
    print("Error: The .apkg file is not a valid zip file.")
    exit(1)

legacy_db_path = os.path.join(extract_dir, "collection.anki2")
# Rename extracted legacy file to avoid confusion/overwriting
if os.path.exists(legacy_db_path):
    os.rename(legacy_db_path, os.path.join(extract_dir, "collection_legacy.anki2"))
    legacy_db_path = os.path.join(extract_dir, "collection_legacy.anki2")

new_db_source = os.path.join(extract_dir, "collection.anki21b")
new_db_path = os.path.join(extract_dir, "collection_new.anki2")

if os.path.exists(new_db_source):
    print("Found collection.anki21b. Decompressing...")
    dctx = zstd.ZstdDecompressor()
    with open(new_db_source, "rb") as ifh, open(new_db_path, "wb") as ofh:
        dctx.copy_stream(ifh, ofh)
else:
    print("No new format found, using legacy as main.")
    shutil.copy(legacy_db_path, new_db_path)

# 1. Try to get models from NEW DB
conn_new = sqlite3.connect(new_db_path)
cursor_new = conn_new.cursor()

print("\n--- Reading Note Types from 'notetypes' table ---")
try:
    cursor_new.execute("SELECT id, name FROM notetypes")
    notetypes = cursor_new.fetchall()
    if notetypes:
        for nid, name in notetypes:
            print(f"ID: {nid}, Name: {name}")
    else:
        print("No entries found in 'notetypes' table.")
except sqlite3.OperationalError:
    print("'notetypes' table does not exist (might be an older Anki version).")

print("\n--- Notes Table Schema ---")
cursor_new.execute("PRAGMA table_info(notes)")
for info in cursor_new.fetchall():
    print(info)

print("\n--- All Tables and Schemas ---")
cursor_new.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor_new.fetchall()
for table_name in tables:
    table = table_name[0]
    print(f"\nTable: {table}")
    cursor_new.execute(f"PRAGMA table_info({table})")
    for column in cursor_new.fetchall():
        print(f"  {column}")


print("\n--- Reading Models from NEW DB ---")
models_map = {}  # ID -> {name, fields[]}
try:
    cursor_new.execute("SELECT models FROM col")
    models_row = cursor_new.fetchone()
    if models_row:
        models_raw = models_row[0]
        print(f'"{models_raw}"')
        # models_json might be bytes in new DB?
        if isinstance(models_raw, bytes):
            models_json = models_raw.decode("utf-8")
        else:
            models_json = models_raw

        print(models_json)
        models = json.loads(models_json)

        for model_id, model in models.items():
            field_names = [f["name"] for f in model["flds"]]
            models_map[model_id] = {"name": model["name"], "fields": field_names}
            print(f"Model ID: {model_id}")
            print(f"  Name: {model['name']}")
            print(f"  Fields: {field_names}")
            print("-" * 20)
    else:
        print("No models found in 'col' table.")
except Exception as e:
    print(f"Error reading models from NEW DB: {e}")

# 2. Read Notes from New DB
print("\n--- Reading Notes from New DB ---")

# Get a sample for each unique mid found in notes
cursor_new.execute("SELECT DISTINCT mid FROM notes")
mids = [row[0] for row in cursor_new.fetchall()]

for mid in mids:
    mid_str = str(mid)
    model_info = models_map.get(mid_str, {"name": "Unknown", "fields": []})

    print(f"\nSampling Notes for Model: {model_info['name']} (ID: {mid})")

    cursor_new.execute("SELECT flds FROM notes WHERE mid=? LIMIT 10", (mid,))
    rows = cursor_new.fetchall()

    found_non_empty = [False] * 20  # Arbitrary max fields
    example_values = [""] * 20

    max_fields = 0

    for (flds,) in rows:
        parts = flds.split("\x1f")
        max_fields = max(max_fields, len(parts))

        for i, p in enumerate(parts):
            if p and p.strip():
                found_non_empty[i] = True
                if not example_values[i]:
                    example_values[i] = p[:50].replace("\n", " ")

    print(f"  Max Fields found: {max_fields}")
    for i in range(max_fields):
        fname = (
            model_info["fields"][i] if i < len(model_info["fields"]) else f"Field {i}"
        )
        status = "[HAS CONTENT]" if found_non_empty[i] else "[ALWAYS EMPTY]"
        print(f"    [{i}] {fname}: {status} - Example: {example_values[i]}")

conn_new.close()
