# Plan: Interactive Mode for `augment_notes.py`

## Phase 1: Environment and CLI Setup
- [ ] Task: Update `augment_notes.py` to accept `--interactive` / `-i` flag.
- [ ] Task: Create a utility function or class for handling user interaction (input loop).

## Phase 2: Core Logic Implementation
- [ ] Task: Modify the main loop in `augment_notes.py` to check for the interactive flag.
- [ ] Task: Implement the "Review Summary" display showing original fields and AI response.
- [ ] Task: Implement the decision logic (Accept, Skip, Quit).
    - [ ] Handle 'y' (Accept): Proceed with AnkiConnect update.
    - [ ] Handle 'n' (Skip): Continue to next iteration without updating.
    - [ ] Handle 'q' (Quit): Exit the loop and script.

## Phase 3: Verification and Refinement
- [ ] Task: Manual verification of interactive mode with a small set of notes.
- [ ] Task: Verify that non-interactive mode (default) still works as expected.
- [ ] Task: Run existing tests to ensure no regressions.
- [ ] Task: Conductor - User Manual Verification 'Interactive Mode' (Protocol in workflow.md)
