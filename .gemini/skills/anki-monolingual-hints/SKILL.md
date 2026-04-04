---
name: anki-monolingual-hints
description: Transform Anki cloze deletion hints from your target language to monolingual cues (definitions, synonyms, or grammar cues) in the target language. Use this to help users "think" in the target language by removing crutches.
---

# Anki Monolingual Hints

This skill automates the conversion of target language hints in Anki cloze deletions (e.g., `{{c1::French::TargetLang}}`) into cues in the target language, following a specific hierarchy of "thinking" strategies.

## Strategy

When transforming a cloze hint, replace the original hint with a **concise** monolingual cue and **keep the original translation (translated to the `--target-language` if different) at the end in parentheses** (e.g., `{{c1::Target::TL_Cue (TargetLang)}}`).

**Rules:**
- **Keep it small:** Both the TL cue and the target language part should be as short as possible. **Encourage common abbreviations** (e.g., `p.c.` for `passé composé`, `f.` for `féminin`, `m.` for `masculin`) to keep the total length minimal.
- **Single Strategy:** Do not combine priorities (e.g., don't use both a synonym and a grammar cue). Pick the best one from the list below.
- **No Self-Reference:** The cue must not contain the target word itself or its clearly recognizable root.

Apply the following priority for the TL cue:

1.  **Zero Hint:** Use only the target language hint in parentheses if the sentence context makes the answer obvious (e.g., `{{c1::de::(de)}}`).
2.  **Definition (TL):** Provide a simple definition in the Target Language (e.g., `{{c1::voiture::moyen de transport (coche)}}`).
3.  **Synonym/Antonym (TL):** Use `=` for synonyms or `≠` for antonyms (e.g., `{{c1::triste::≠ content (triste)}}`).
4.  **Grammar Cue:** Use a short label for conjugation or rules (e.g., `{{c1::suis::être, présent (soy)}}`).

## Parameters

- `--deck`: (Required) The Anki Deck Name to process.
- `--target-language`: (Optional) The language to use for the parenthetical translation. Defaults to English.
- `--target-field`: (Optional) The name of the field containing the cloze deletions. Defaults to `Expression`.
- `--limit`: (Optional) Maximum number of notes to process in one run. Defaults to 5.
- `--dry-run`: (Optional) Show the proposed changes without applying them.
- `--interactive` / `-i`: (Optional) If enabled, process notes interactively, prompting the user to review and accept each transformation before updating.

## Workflow

### Step 1: Fetch Notes
Query AnkiConnect at `http://localhost:8765`.
1. Use `findNotes` with `deck:"<deck-name>"` and a query that targets notes with hints (e.g., `{{c1::*::*}}`).
2. Use `notesInfo` to fetch the field data for the identified notes.
3. Sort the notes numerically by Frequency if available (descending) or by their creation ID.
4. Limit the list to the number specified in `--limit`.

### Step 2: Analyze and Transform
For each note, identify the cloze deletions in the `--target-field`. For each deletion:
1. Extract the **Target Word** and the **Original Hint**.
2. Use your AI capabilities to evaluate the sentence context, the Target Word, and the `--target-language`.
3. Select the best strategy (Zero Hint, Definition, Synonym, or Grammar Cue) to replace the original hint.
4. Construct the new cloze deletion (e.g., `{{c1::word::new_hint}}` or `{{c1::word}}`). Ensure the parenthetical translation is in the `--target-language`.
5. If `--interactive` (or `-i`) is enabled, present the transformation to the user for approval. Provide options: accept (y), reject (n), skip remaining (s), or quit (q).

### Step 3: Apply Updates
1. If `--dry-run` is NOT specified, update Anki using the `multi` action to bundle multiple `updateNoteFields` and `addTags` requests into a single network call.
2. For each note, save the modified field and add a tag `monolingual_conversion` and the current date (YYYY-MM-DD).

## Requirements
- **Anki** must be running with **AnkiConnect** installed.
- Access to the local network to communicate with `http://localhost:8765`.