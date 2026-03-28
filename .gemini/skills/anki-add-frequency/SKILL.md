---
name: anki-add-frequency
description: Evaluate conversational frequency of Anki learning targets. Use when Gemini CLI needs to estimate how common a word or phrase is in a conversational setting (scale 1-1000) and populate an Anki field with this frequency data.
---

# Anki Add Frequency

## Overview

This skill provides a procedural workflow for evaluating the conversational frequency of words or phrases within Anki notes. **It specifically targets notes where the frequency field is currently empty**. It extracts the learning target from Anki cloze formatting and maps its commonality to a number between 1 (very common) and 1000 (rare).

## Parameters

When this skill is triggered, respect the following parameters (usually provided as flags or in the request):

- `--deck`: (Required) The Anki Deck Name to process.
- `--target-field`: (Optional) The name of the field where the frequency number will be stored. Defaults to `Frequency`.
- `--total-notes`: (Optional) Maximum number of notes to process in one run. Defaults to `20`.
- `--batch-size`: (Optional) The number of strings to evaluate in a single subagent/LLM request. Defaults to `5`.
- `--dry-run`: (Optional) If enabled, show a preview of extracted words and evaluated frequencies but do NOT update Anki.

## Workflow

To evaluate and add frequency to an Anki deck using these parameters, follow these steps:

### 1. Fetch and Filter Notes (Strictly Empty Target)
Query AnkiConnect for notes in the specified `--deck` where the `--target-field` is **unset (empty)**.

**AnkiConnect Query Example:**
```bash
curl -s -X POST http://localhost:8765 -d '{
  "action": "findNotes",
  "version": 6,
  "params": {
    "query": "deck:\"'"$DECK"'\" \"'"$TARGET_FIELD"':\""
  }
}'
```

1. Fetch note details using `notesInfo` for the resulting IDs.
2. Infer the primary language of the deck from the deck name or first note content.
3. Limit the list to `--total-notes`.

### 2. Extract Learning Targets
Identify the specific word or words the user is learning from the `Expression` field (or the first field if multiple).
1. Look for Anki cloze markers: `{{c1::target::hint}}` or `{{c1::target}}`.
2. **Extract**: Use regex to get just the `target` part.
   - **Regex**: `re.search(r"\{\{c\d+::(.*?)(::.*?)?\}\}", text).group(1)`
3. **Deduplicate**: Identify unique strings to minimize evaluation costs.

### 3. Evaluate Frequency (Subagent Delegation)
Delegate the frequency evaluation of unique strings to a subagent (e.g., `generalist`).

**Instruction for Subagent:**
> "Evaluate how often the following strings appear in a conversational setting in [Language]. Map each to a number between 1 and 1000, where 1 represents a word used very often (e.g., pronouns, basic verbs) and 1000 represents a word that is rarely used. Provide the result as a JSON object mapping the original string to its frequency number."

### 4. Apply Updates
Map the evaluated frequencies back to the original Note IDs.

- **If `--dry-run`**: Print a table of `ID | Extracted Target | Frequency` and stop.
- **Otherwise**: Update Anki in batches using `updateNoteFields`.

## Guidelines

- **Smart Fill Rule**: **NEVER** process notes that already have content in the `--target-field`.
- **Scale Consistency**: Ensure 1 is most frequent, 1000 is least frequent.
- **Batching**: Respect the `--batch-size` when sending strings to the subagent.
- **Cost Awareness**: Summarize the number of evaluations to be performed before starting.
