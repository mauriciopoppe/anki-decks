---
name: anki-monolingual-hints
description: Transform Anki cloze deletion hints from English to monolingual cues (definitions, synonyms, or grammar cues) in the target language. Use this to help users "think" in the target language by removing English crutches.
---

# Anki Monolingual Hints

This skill automates the conversion of English hints in Anki cloze deletions (e.g., `{{c1::French::English}}`) into cues in the target language, following a specific hierarchy of "thinking" strategies.

## Strategy

When transforming a cloze hint, apply the following priority:

1.  **Zero Hint:** Remove the hint entirely if the sentence context makes the answer obvious (e.g., `{{c1::de}}`).
2.  **Definition (TL):** Provide a simple definition in the Target Language (e.g., `{{c1::voiture::moyen de transport}}`).
3.  **Synonym/Antonym (TL):** Use `=` for synonyms or `≠` for antonyms (e.g., `{{c1::triste::≠ content}}`).
4.  **Grammar Cue:** Use a short label for conjugation or rules (e.g., `{{c1::suis::être, présent}}`).

## Parameters

- `--deck`: (Required) The Anki Deck Name to process.
- `--target-field`: (Optional) The name of the field containing the cloze deletions. Defaults to `Expression`.
- `--total-notes`: (Optional) Maximum number of notes to process in one run. Defaults to 5.
- `--dry-run`: (Optional) Show the proposed changes without applying them.
- `--interactive` / `-i`: (Optional) If enabled, process notes interactively, prompting the user to review and accept each transformation before updating.

## Workflow

### Step 1: Fetch Notes
Query AnkiConnect at `http://localhost:8765`.
1. Use `findNotes` with `deck:"<deck-name>"` and a query that targets notes with English hints (e.g., `{{c1::*::*}}`).
2. Use `notesInfo` to fetch the field data for the identified notes.
3. Sort the notes numerically by Frequency if available (descending) or by their creation ID.
4. Limit the list to the number specified in `--total-notes`.

### Step 2: Analyze and Transform
For each note, identify the cloze deletions in the `--target-field`. For each deletion:
1. Extract the **Target Word** and the **English Hint**.
2. Use your AI capabilities to evaluate the sentence context and the Target Word.
3. Select the best strategy (Zero Hint, Definition, Synonym, or Grammar Cue) to replace the English hint.
4. Construct the new cloze deletion (e.g., `{{c1::word::new_hint}}` or `{{c1::word}}`).
5. If `--interactive` (or `-i`) is enabled, present the transformation to the user for approval. Provide options: accept (y), reject (n), skip remaining (s), or quit (q).

### Step 3: Apply Updates
1. If `--dry-run` is NOT specified, use `updateNoteFields` to save the modified field back to Anki.
2. Add a tag `monolingual_conversion` and the current date (YYYY-MM-DD) to the note using `addTags`.

## Requirements
- **Anki** must be running with **AnkiConnect** installed.
- Access to the local network to communicate with `http://localhost:8765`.
