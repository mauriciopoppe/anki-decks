# Anki Add Notes Skill Implementation Plan

## Objective
Create a new Gemini CLI skill named `anki-add-notes` that replicates the functionality of the `augment_notes.py` script. The skill will provide plain English instructions, allowing Gemini CLI to natively orchestrate the AI augmentation of Anki notes via AnkiConnect without relying on the python script.

## Context
The python script currently fetches empty notes from Anki, reads a prompt from a file, populates the prompt with note fields, generates a response using an LLM, and writes back the generated response as HTML to Anki. The new skill will proceduralize these steps for the agent.

Crucially, the skill will retain the exact same parameters as the Python script (excluding the `model` flag, which is inherently handled by the agent), and it will enforce reading the prompt dynamically from a provided file path (rather than hardcoding the prompt in the skill).

## Implementation Steps

1. **Initialize Skill Structure:**
   - Create a new skill directory: `.gemini/skills/anki-add-notes`.
   - Create the core file: `.gemini/skills/anki-add-notes/SKILL.md`.

2. **Define Skill Frontmatter:**
   - Define `name: anki-add-notes`.
   - Define a concise description to trigger the skill when the user wants to augment Anki notes using a prompt template.

3. **Define Parameters in `SKILL.md`:**
   Ensure the following parameters are explicitly documented and respected by the agent:
   - `--deck`: (Required) Anki Deck Name.
   - `--target-field`: (Required) The field to fill (e.g., 'Notes', 'Mnemonic').
   - `--prompt-file`: (Required) Path to a text file containing the prompt template.
   - `--dry-run`: (Optional) Identify and list notes without processing.
   - `--interactive` / `-i`: (Optional) Process notes interactively, reviewing each response.
   - `--total-notes`: (Optional) Total number of notes to process.
   - `--sort-field`: (Optional) Field to sort by. Defaults to `Frequency`.

4. **Define Workflow Instructions in `SKILL.md`:**
   Instruct the agent to follow these steps in plain English:
   - **Step 1: Read the Prompt Template:** Use `read_file` to read the contents of the file specified in `--prompt-file`. Identify all required fields by looking for placeholders in the format `{FieldName}`.
   - **Step 2: Fetch and Sort Notes:** Query AnkiConnect `http://localhost:8765` using `findNotes` for the specified `--deck`. Use `notesInfo` to fetch details. Sort the resulting notes numerically by the `--sort-field` (defaulting to 999999 for missing values).
   - **Step 3: Filter Notes:** Verify that `--target-field` and all required fields exist on the note type. Keep only notes where the `--target-field` is empty. Limit the results to `--total-notes` if specified.
   - **Step 4: Handle Dry Run:** If `--dry-run` is active, print a preview of the notes to be updated and terminate the workflow.
   - **Step 5: Generate Content:** For each filtered note:
     - Substitute the `{FieldName}` placeholders in the prompt template with the note's actual field values.
     - You (Gemini CLI) will act as the model and directly generate the response using the filled prompt.
     - If `--interactive` is true, present the generated text to the user for approval (y/n/s/q).
     - Convert the Markdown response to HTML, specifically replacing `<strong>` tags with `<b>` tags.
   - **Step 6: Apply Updates:** Update Anki via AnkiConnect's `updateNoteFields` and add tags (`anki_deck_augment` and the current date).

## Verification
- Validate the YAML frontmatter.
- Review the `SKILL.md` file to ensure the prompt is read dynamically.
- Run `gemini skills package` (or equivalent `package_skill.cjs` script) if necessary to validate the skill structure.
