---
name: anki-backup-deck
description: Backup an Anki deck to a single .apkg binary file. Use when the user wants to ensure they have a restorable state of their deck before making significant changes.
---

# Anki Backup Deck

This skill automates the process of backing up an Anki deck using the AnkiConnect API. It ensures a deterministic and reliable backup as a single binary `.apkg` file.

## Usage

When triggered, this skill uses a Python script to communicate with a running Anki instance via AnkiConnect.

1.  **Identify the deck**: Ask for the name of the deck to backup if not provided.
2.  **Run the backup script**: Execute the `anki_backup.py` script with the deck name and a target output path.
3.  **Default Output Path**: If the user doesn't specify an output path, use the project root with the format `<deck_name>_<date>.apkg`.

### Script Execution

```bash
python3 scripts/anki_backup.py "<deck_name>" "<output_path>"
```

## Requirements

- **Anki** must be running.
- **AnkiConnect** add-on must be installed and configured.
- **Requests** library must be available in the Python environment.
