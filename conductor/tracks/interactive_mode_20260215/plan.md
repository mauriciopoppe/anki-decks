# Plan: Interactive Mode for `augment_notes.py`

## Phase 1: Environment and CLI Setup
- [x] Task: Update `augment_notes.py` to accept `--interactive` / `-i` flag.
- [x] Task: Print the model name at startup.
- [x] Task: Create a utility function or class for handling user interaction (input loop).

## Phase 2: Core Logic Implementation
- [x] Task: Modify the main loop in `augment_notes.py` to check for the interactive flag.
- [x] Task: Implement the "Review Summary" display showing original fields and AI response.
- [x] Task: Implement the decision logic (Accept, Skip, Skip Remaining, Quit).
    - [x] Handle 'y' (Accept): Proceed with AnkiConnect update.
    - [x] Handle 'n' (Skip): Continue to next iteration without updating.
    - [x] Handle 's' (Skip remaining): Stop processing further notes but proceed to finish.
    - [x] Handle 'q' (Quit): Exit the loop and script.

## Phase 3: Verification and Refinement
- [x] Task: Manual verification of interactive mode with a small set of notes. (Verified via unit tests with mocked input)
- [x] Task: Verify that non-interactive mode (default) still works as expected. (Verified via existing tests passing)
- [x] Task: Run existing tests to ensure no regressions.
- [x] Task: Conductor - User Manual Verification 'Interactive Mode' (Protocol in workflow.md)
