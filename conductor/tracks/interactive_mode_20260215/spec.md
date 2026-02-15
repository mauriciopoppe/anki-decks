# Specification: Interactive Mode for `augment_notes.py`

## Overview
Add an interactive mode to the `augment_notes.py` script. This mode allows users to review and approve AI-generated content for each Anki note before it is saved back to the Anki database via AnkiConnect.

## Functional Requirements
- **CLI Trigger:** Introduce a `--interactive` (or `-i`) command-line flag to enable the interactive session.
- **Note-by-Note Processing:** The script will halt after generating content for each individual note.
- **Review Summary:** Display a summary to the user including:
    - The original field values used in the prompt.
    - The generated response from the LLM.
- **User Actions:**
    - `y` (Accept): Save the change to Anki and proceed to the next note.
    - `n` (Skip): Discard the change and proceed to the next note.
    - `q` (Quit): Stop the script entirely.
- **Strict Interaction:** No "bulk apply" or "bulk skip" options; each note requires an individual decision.

## Non-Functional Requirements
- **Console Readability:** Use clear formatting (e.g., separators or basic colors if supported) to distinguish between notes and summaries in the terminal.
- **Graceful Termination:** Ensure that quitting the interactive mode handles any necessary cleanup (though current script architecture is mostly stateless per note).

## Acceptance Criteria
- [ ] Running `python augment_notes.py --interactive` enters the interactive loop.
- [ ] The prompt correctly displays original field data and the AI's proposed output.
- [ ] Selecting 'y' results in the note being updated in Anki.
- [ ] Selecting 'n' results in no change to Anki for that note.
- [ ] Selecting 'q' terminates the process immediately.
