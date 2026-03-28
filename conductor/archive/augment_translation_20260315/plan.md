# Implementation Plan: `augment_translation.py`

## Phase 1: Setup and Infrastructure
- [x] Task: Add `googletrans` (or a suitable alternative like `deep-translator` if `googletrans` has stability issues) to `requirements.txt`.
- [x] Task: Create `augment_translation.py` file with basic argparse setup for `--deck`, `--target-field`, `--source-field` (default: "Expression"), and `--dry-run`.
- [x] Task: Copy basic AnkiConnect wrapper functions (`invoke_anki`) from existing scripts.

## Phase 2: Logic Implementation
- [x] Task: Implement the Anki data fetching logic: query by deck, infer model, and extract note fields.
- [x] Task: Implement the cloze normalization function using regex (e.g., `re.sub(r'\{\{c\d+::(.*?)(::.*?)?\}\}', r'\1', text)`).
- [x] Task: Implement the translation function using the chosen library to translate the normalized text to English. *Note: Ensure fallback/alternative using `GEMINI_API_KEY` via `litellm` if `googletrans` is problematic.*
- [x] Task: Implement the main processing loop: iterate through notes, skip if target field is not empty, normalize, translate, and update via AnkiConnect (or print if `--dry-run`).

## Phase 3: Testing and Documentation
- [x] Task: Create `test_augment_translation.py` and write unit tests for the cloze normalization function.
- [x] Task: Update the `README.md` to include a section on how to use `augment_translation.py`.
- [x] Task: Update the `conductor/product.md` to list `augment_translation.py` under Key Features.
- [x] Task: Conductor - User Manual Verification 'Testing and Documentation' (Protocol in workflow.md)