---
name: anki-add-notes
description: Procedural workflow to orchestrate the AI augmentation of Anki notes via AnkiConnect. Use this when the user wants to augment Anki notes using a prompt template, reading the template from a file and generating content based on it.
---

# Anki Add Notes

## Overview

This skill provides a procedural workflow for augmenting Anki note fields by taking existing note data, formatting it into a prompt template read from a file, and using your AI capabilities to generate content to populate a specific target field. **It strictly targets notes where the target field is currently empty**, preventing redundant work and data overwrites.

## Parameters

When this skill is triggered, respect the following parameters (usually provided as flags or in the request):

- `--deck`: (Required) The Anki Deck Name to process.
- `--target-field`: (Required) The name of the field where the generated text will be stored (e.g., 'Notes', 'Mnemonic').
- `--prompt-file`: (Required) Path to a text file containing the prompt template. The template should use `{FieldName}` placeholders.
- `--dry-run`: (Optional) If enabled, identify and list the notes to be updated without actually processing or modifying them.
- `--interactive` / `-i`: (Optional) If enabled, process notes interactively, prompting the user to review and accept each generated response before updating.
- `--limit`: (Optional) Maximum number of notes to process in one run.
- `--sort-field`: (Optional) The field to use for sorting notes prior to processing. Defaults to `Frequency`.

## Workflow

To augment Anki notes using these parameters, follow these steps exactly:

### Step 1: Read the Prompt Template
Use your available file-reading tools to read the contents of the file specified in `--prompt-file`. Identify all required fields by finding placeholders in the format `{FieldName}` within the template.

### Step 2: Fetch and Sort Notes
Query AnkiConnect locally at `http://localhost:8765`.

1. Use the `findNotes` action with the query `deck:"<deck-name>"`.
2. Fetch the details of the returned notes using the `notesInfo` action.
3. Sort the resulting list of notes numerically by the value in the `--sort-field` (if the note lacks this field or it is empty, treat its value as `999999` for sorting purposes).

### Step 3: Filter Notes
Iterate through the sorted notes to filter them:
1. Verify that the `--target-field` and all required fields (identified in Step 1) exist on the note type. If they do not exist, report an error and stop.
2. Keep only the notes where the `--target-field` is **empty** (or contains only whitespace).
3. If `--limit` is specified, limit the final list of filtered notes to this number.

### Step 4: Handle Dry Run
If `--dry-run` is active, print a clear preview list of the filtered notes that would be updated (including their IDs and a preview of their relevant source fields), and then **terminate** the workflow without modifying any notes.

### Step 5: Generate Content
For each filtered note:
1. Extract the actual field values from the note's fields.
2. Substitute the `{FieldName}` placeholders in the prompt template with these actual values to create the final prompt.
3. Generate the response directly using the filled prompt.
4. If `--interactive` (or `-i`) is enabled, present the generated text to the user for approval. Provide options: accept (y), reject (n), skip remaining (s), or quit (q). Respect their choice.
5. Convert the Markdown response to HTML. Specifically, replace any `<strong>` tags with `<b>` tags and `</strong>` with `</b>`.

### Step 6: Apply Updates
Map the generated HTML content back to the original Note IDs. Update Anki by making requests to AnkiConnect:
1. Use the `multi` action to bundle multiple `updateNoteFields` and `addTags` requests into a single network call. 
2. Set the `--target-field` with the new HTML content and add the tags `anki_deck_augment` and the current date (in `YYYY-MM-DD` format).

## Guidelines
- **Strictly Empty Targets**: **NEVER** process notes that already have content in the `--target-field`. This is the primary filtering rule.
- **Cost/Context Awareness**: Processing large numbers of notes sequentially can consume large amounts of context. Always summarize the number of notes to be processed and pause to confirm if the count is large (>10 notes) before starting the generation loop, unless it's a dry run.
