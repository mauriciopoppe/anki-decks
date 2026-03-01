# Implementation Plan: Cleanup Offline Deck Mode

## Phase 1: Preparation & Cleanup
- [x] Task: Remove `analyze_deck.py` and its dependencies.
- [x] Task: Remove `zstandard` from `requirements.txt`.
- [x] Task: Remove `temp_extraction/` if it exists.
- [x] Task: Update `tech-stack.md` to remove `zstandard` as a required technology.

## Phase 2: Refactor `augment_notes.py`
- [x] Task: Remove `zstandard` import and offline processing logic in `augment_notes.py`.
- [x] Task: Remove command-line arguments and configuration for offline mode.
- [x] Task: Refactor the `main` entry point to only support AnkiConnect.

## Phase 3: Test Cleanup & Final Verification
- [x] Task: Update `test_augment_notes.py` to remove offline-mode test cases.
- [x] Task: Run remaining tests to ensure AnkiConnect functionality is preserved.
- [x] Task: Verify that `augment_notes.py` still works with AnkiConnect manually (if possible).
