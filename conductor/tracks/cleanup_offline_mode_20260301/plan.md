# Implementation Plan: Cleanup Offline Deck Mode

## Phase 1: Preparation & Cleanup
- [ ] Task: Remove `analyze_deck.py` and its dependencies.
- [ ] Task: Remove `zstandard` from `requirements.txt`.
- [ ] Task: Remove `temp_extraction/` if it exists.
- [ ] Task: Update `tech-stack.md` to remove `zstandard` as a required technology.

## Phase 2: Refactor `augment_notes.py`
- [ ] Task: Remove `zstandard` import and offline processing logic in `augment_notes.py`.
- [ ] Task: Remove command-line arguments and configuration for offline mode.
- [ ] Task: Refactor the `main` entry point to only support AnkiConnect.

## Phase 3: Test Cleanup & Final Verification
- [ ] Task: Update `test_augment_notes.py` to remove offline-mode test cases.
- [ ] Task: Run remaining tests to ensure AnkiConnect functionality is preserved.
- [ ] Task: Verify that `augment_notes.py` still works with AnkiConnect manually (if possible).
