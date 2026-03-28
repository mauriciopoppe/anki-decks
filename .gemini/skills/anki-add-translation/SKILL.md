---
name: anki-add-translation
description: Procedural workflow to translate Anki note fields into English. Use when Gemini CLI needs to enrich Anki decks with English translations using direct LLM calls or subagents. Supports parameters for deck selection, field mapping, and batch control.
---

# Anki Add Translation

## Overview

This skill provides a procedural workflow for translating Anki note fields into English. **It specifically targets notes where the target field is currently empty**, preventing redundant translations and data overwrites. It supports configurable parameters for deck selection, source/target fields, and batch processing limits.

## Parameters

When this skill is triggered, respect the following parameters (usually provided as flags or in the request):

- `--deck`: (Required) The Anki Deck Name to process.
- `--target-field`: (Optional) The name of the field where the English translation will be stored. Defaults to `ExpressionEnglish`.
- `--source-field`: (Optional) The field containing the text to translate. Defaults to `Expression`.
- `--total-notes`: (Optional) Maximum number of notes to process in one run. Defaults to `20`.
- `--batch-size`: (Optional) The number of unique sentences to translate in a single subagent/LLM request. Defaults to `5`.
- `--dry-run`: (Optional) If enabled, show a preview of normalized text and translations but do NOT update Anki.

## Workflow

To translate a field in an Anki deck using these parameters, follow these steps:

### 1. Fetch and Filter Notes (Strictly Empty Target)
Query AnkiConnect for notes in the specified `--deck` where the `--target-field` is **unset (empty)**.

**AnkiConnect Query Example:**
```bash
curl -s -X POST http://localhost:8765 -d '{
  "action": "findNotes",
  "version": 6,
  "params": {
    "query": "deck:\"'"$DECK"'\" \"'"$TARGET_FIELD"':\""
  }
}'
```

1. Fetch note details using `notesInfo` for the resulting IDs.
2. If multiple note types exist, infer the primary model from the first note.
3. Sort notes by `FreqSort` or `Frequency` (if available) to prioritize common words.
4. Limit the list to `--total-notes`.

### 2. Normalize and Deduplicate
Prepare the source text for translation:
1. Extract the text from `--source-field`.
2. **Normalize**: Remove Anki cloze markers using regex: `re.sub(r"\{\{c\d+::(.*?)(::.*?)?\}\}", r"\1", text)`.
3. **Deduplicate**: Identify unique normalized strings to minimize translation costs.

### 3. Translate (Subagent Delegation)
Delegate the translation of unique strings to a subagent (e.g., `generalist`).

**Instruction for Subagent:**
> "Translate the following list of strings into English. Maintain the exact order and provide ONLY the translations as a JSON list of strings."

### 4. Apply Updates
Map the translations back to the original Note IDs.

- **If `--dry-run`**: Print a table of `ID | Source | Normalized | Translation` and stop.
- **Otherwise**: Update Anki in batches using `updateNoteFields`.

## Guidelines

- **Smart Fill Rule**: **NEVER** process notes that already have content in the `--target-field`. This is the primary filtering mechanism.
- **Validation**: Ensure both `--source-field` and `--target-field` exist in the note type before starting.
- **Batching**: Respect the `--batch-size` when sending strings to the subagent.
- **Cost Awareness**: Always summarize the number of notes and unique strings to be processed before starting, unless `--dry-run` is active.
