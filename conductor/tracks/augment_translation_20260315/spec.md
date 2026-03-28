# Specification: `augment_translation.py`

## Overview
Create a new script, `augment_translation.py`, designed to automatically translate Anki note fields into English and update a target field. Unlike other augmentation scripts, it uses a dedicated translation library (`googletrans`) rather than LLM prompts.

## Functional Requirements
1.  **Command-Line Interface:**
    *   `--deck`: (Required) The Anki Deck Name to process.
    *   `--target-field`: (Required) The name of the field to update with the translation.
    *   `--source-field`: (Optional) The name of the field containing the text to translate. Defaults to "Expression".
    *   `--dry-run`: (Optional) Flag to preview changes without updating Anki.
2.  **AnkiConnect Integration:**
    *   Fetch notes from the specified `--deck`.
    *   Infer the note type (model) from the first fetched note.
    *   Verify that both the source and target fields exist in the inferred note type.
    *   Filter notes to process only those where the `--target-field` is empty.
    *   Update Anki notes with the generated translations.
3.  **Data Normalization:**
    *   Extract the value from the `--source-field`.
    *   Clean Anki cloze formatting from the text using regex (e.g., converting `{{c1::word::hint}}` to just `word`).
4.  **Translation:**
    *   Translate the normalized text to English using the `googletrans` library (or an equivalent free API wrapper). Fallback to using `litellm` with the `GEMINI_API_KEY` if the free library fails or if preferred.

## Non-Functional Requirements
*   **Dependency Management:** Add `googletrans` (or the chosen translation library) to `requirements.txt`.
*   **Error Handling:** Handle API errors gracefully (both AnkiConnect and the translation API).
*   **Performance:** Consider batching or rate-limiting translation requests if necessary to avoid API bans.

## Out of Scope
*   Using complex custom prompts for this specific script; simple translation is the goal.
*   Translating to languages other than English (for this iteration).