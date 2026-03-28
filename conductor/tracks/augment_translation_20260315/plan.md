# Implementation Plan: `augment_translation.py`

## Phase 1: Setup and Infrastructure
- [ ] Task: Add `googletrans` (or a suitable alternative like `deep-translator` if `googletrans` has stability issues) to `requirements.txt`.
- [ ] Task: Create `augment_translation.py` file with basic argparse setup for `--deck`, `--target-field`, `--source-field` (default: "Expression"), and `--dry-run`.
- [ ] Task: Copy basic AnkiConnect wrapper functions (`invoke_anki`) from existing scripts.

## Phase 2: Logic Implementation
- [ ] Task: Implement the Anki data fetching logic: query by deck, infer model, and extract note fields.
- [ ] Task: Implement the cloze normalization function using regex (e.g., `re.sub(r'\{\{c\d+::(.*?)(::.*?)?\}\}', r'\1', text)`).
- [ ] Task: Implement the translation function using the chosen library to translate the normalized text to English. *Note: Ensure fallback/alternative using `GEMINI_API_KEY` via `litellm` if `googletrans` is problematic.*
- [ ] Task: Implement the main processing loop: iterate through notes, skip if target field is not empty, normalize, translate, and update via AnkiConnect (or print if `--dry-run`).

## Phase 3: Testing and Documentation
- [ ] Task: Create `test_augment_translation.py` and write unit tests for the cloze normalization function.
- [ ] Task: Update the `README.md` to include a section on how to use `augment_translation.py`.
- [ ] Task: Update the `conductor/product.md` to list `augment_translation.py` under Key Features.
- [ ] Task: Conductor - User Manual Verification 'Testing and Documentation' (Protocol in workflow.md)