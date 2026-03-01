# Specification: Cleanup Offline Deck Mode

## Overview
The goal of this track is to remove the "offline" mode (processing .apkg files) from `augment_notes.py` and its associated tests. This will simplify the codebase, focusing the tool solely on its AnkiConnect integration.

## Functional Requirements
- **`augment_notes.py` Cleanup:**
  - Remove all logic related to loading and extracting `.apkg` files.
  - Remove command-line arguments specific to offline mode (e.g., `--deck`).
  - Ensure the script defaults to or only supports AnkiConnect mode.
- **Dependency Removal:**
  - Remove `zstandard` from `requirements.txt` if it is no longer used by any other core scripts.
- **File & Directory Cleanup:**
  - Remove `analyze_deck.py` as it is an offline-only analysis tool.
  - Remove `temp_extraction/` directory if it exists and is only used for temporary deck processing.
- **Test Cleanup:**
  - Remove or update `test_augment_notes.py` to eliminate offline mode test cases while maintaining coverage for AnkiConnect-related logic.

## Non-Functional Requirements
- **Codebase Simplicity:** Reduction in total lines of code and complexity.
- **Maintainability:** Easier to maintain a single mode of operation.

## Acceptance Criteria
- [ ] `augment_notes.py` no longer contains offline deck processing logic.
- [ ] `analyze_deck.py` is deleted.
- [ ] `zstandard` is removed from `requirements.txt`.
- [ ] Existing tests for AnkiConnect functionality pass.
- [ ] No regressions in core `augment_notes.py` (AnkiConnect mode).

## Out of Scope
- Migrating `augment_notes.py` to a different framework.
- Adding new features during this cleanup.
