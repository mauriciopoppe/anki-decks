# Anki Decks Skills

An ecosystem of **AI Workspace Skills** for Anki that automates the creation of high-quality study materials. These tools enable AI agents to enrich your decks with mnemonics, i+1 example sentences, conversational frequency data, and monolingual hints directly through AnkiConnect.

## How it Works

These skills are stored in the `skills/` directory. They follow the [Agent Skills](https://github.com/vercel-labs/skills) specification, making them portable and easy to install in any project.

## Installation

You can install these skills using the `npx skills` CLI. This tool supports over 50 agents (Gemini CLI, Claude Code, Cursor, Windsurf, etc.) and will automatically detect your agent and install the skills in the appropriate directory.

To install all skills from this repository:

```bash
npx skills add mauriciopoppe/anki-decks
```

If you are already inside this repository and want to load them:

```bash
npx skills add .
```

---

## Workspace Skill: `anki-add-notes`

This skill orchestrates the AI augmentation of Anki notes. It scans your deck for empty fields and fills them using a prompt template read from a local file.

### Examples

#### 1. Explain Sentences
Takes a Cloze deletion like `Sur ça, tu touches un point {{c1::assez juste}}` and adds a detailed explanation to the "Notes" field.

| Before | After |
| --- | --- |
| ![before](./resources/french-explain-before.png) | ![after](./resources/french-explain-after.png) |

**Prompt:**
> Use anki-add-notes for deck "Language French::My french words and phrases", target field "Notes", and prompt file "./explain_prompt.txt".

#### 2. Generate Kanji Mnemonics
Uses the Kanji and its meaning to create a story that helps you remember the shape and sound.

| Card |
| --- |
| ![after](./resources/kanji-mnemonic-after.png) |

**Prompt:**
> Use anki-add-notes for deck "Language Japanese::Mining", target field "Notes", and prompt file "./kanji_mnemonic_prompt.txt".

#### 3. Translate Sentences
Translates a field (like "Expression") into your target language, automatically cleaning Anki cloze markers.

**Prompt:**
> Use anki-add-notes for deck "Language Hindi::My hindi words and phrases", target field "ExpressionEnglish", and prompt file "./translate_prompt.txt".

### Parameters
- `--deck`: (Required) The Anki Deck Name to process.
- `--target-field`: (Required) The field you want to fill (e.g., "Notes").
- `--prompt-file`: (Required) Path to your prompt template. Use `{FieldName}` placeholders to pull data from your cards. See the bundled [Explanation](./explain_prompt.txt), [Kanji](./kanji_mnemonic_prompt.txt), [Translation in English](./translate_prompt.txt), [Translation in Japanese (furigana)](./translate_ja_prompt.txt) templates for examples.
- `--limit`: (Optional) Limit the number of notes processed. Defaults to `20`.
- `--sort-field`: (Optional) The field to use for sorting notes. Defaults to `Frequency`.
- `--interactive` / `-i`: (Optional) Review every AI response before it hits your deck.
- `--dry-run`: (Optional) List the notes that would be processed without calling the AI.

---

## Workspace Skill: `anki-monolingual-hints`

Transform Anki cloze deletion hints from a source language (like English) to concise monolingual cues (definitions, synonyms, or grammar cues) in the target language, while preserving a translation in the specified `--target-language` (defaults to English) in parentheses. Use this to help users "think" in the target language.

### Example

**Prompt:**
> Use anki-monolingual-hints for deck "Language French::My french words and phrases" with target language "Spanish".

### Strategy Priority (with target language hint in parentheses)
1. **Zero Hint:** Only the target language hint (e.g., `{{c1::de::(de)}}`).
2. **Definition (TL):** Simple definition + target language (e.g., `{{c1::voiture::véhicule (coche)}}`).
3. **Synonym/Antonym (TL):** `=` or `≠` + target language (e.g., `{{c1::triste::≠ content (triste)}}`).
4. **Grammar Cue:** Conjugation or rule label + target language (e.g., `{{c1::suis::présent (soy)}}`).

**Rules:**
- **Encourage Abbreviations:** Use short forms (e.g., `p.c.` for `passé composé`, `f.` for `féminin`) to keep the hint as small as possible.
- **No Self-Reference:** Cues never contain the target word or its root.
- **Conciseness:** Hints are kept as short as possible.

### Parameters
- `--deck`: (Required) The Anki Deck Name to process.
- `--target-language`: (Optional) The language to use for the parenthetical translation. Defaults to English.
- `--target-field`: (Optional) Field with the cloze deletions. Defaults to `Expression`.
- `--limit`: (Optional) Limit processing. Defaults to `5`.
- `--interactive` / `-i`: (Optional) Review every transformation.
- `--dry-run`: (Optional) Preview results only.

---

## Workspace Skill: `anki-add-sentence`

Generates **i+1 example sentences** for learning targets. It ensures sentences only use vocabulary you've already learned (by automatically running `extract_learned_vocab.py`) plus the single target word.

### Example

**Prompt:**
> Use anki-add-sentence for deck "Language Japanese::Mining". Process 5 notes.

### Parameters
- `--deck`: (Required) The Anki Deck Name to process.
- `--source-field`: (Optional) Field with the target word. Defaults to `Expression`.
- `--target-field`: (Optional) Field for the generated sentence. Defaults to `Sentence`.
- `--target-field-english`: (Optional) Field for the English translation. Defaults to `SentenceEnglish`.
- `--limit`: (Optional) Limit processing. Defaults to `20`.
- `--batch-size`: (Optional) Notes per AI request. Defaults to `5`.
- `--dry-run`: (Optional) Preview words to be processed.

---

## Workspace Skill: `anki-add-frequency`

Estimates how common a word or phrase is in a conversational setting (scale 1-1000) and fills an Anki field. 1 is very common, 1000 is rare.

### Example

**Prompt:**
> Use anki-add-frequency for deck "Language Hindi::My hindi words and phrases". Process 10 notes.

### Parameters
- `--deck`: (Required) The Anki Deck Name to process.
- `--target-field`: (Optional) Field for the frequency number. Defaults to `Frequency`.
- `--limit`: (Optional) Limit processing. Defaults to `20`.
- `--batch-size`: (Optional) Notes per AI request. Defaults to `5`.
- `--dry-run`: (Optional) Preview results only.

---

## Workspace Skill: `anki-backup-deck`

Backup an Anki deck to a single `.apkg` binary file. Use this before making significant changes to your deck.

### Example

**Prompt:**
> Use anki-backup-deck to backup the "Language French::My french words and phrases" deck to anki_backups/.

---

## Meta Prompts

Meta prompts combine multiple skills into a single powerful workflow. These are useful for processing large batches of new notes across multiple dimensions (frequency, explanations, and translations).

### French Deck Monolingualization
Full augmentation for new French notes, adding frequency data, detailed explanations, and converting English cloze hints into concise monolingual cues.

**Prompt:**
```text
In the deck "Language French::My french words and phrases":
- use the skill anki-add-frequency.
- use the skill anki-add-notes with the target field "Notes" and the prompt file "./explain_es_prompt.txt".
- use the skill anki-add-notes with the target field "ExpressionSpanish" and the prompt file "./translate_es_prompt.txt".
- use the skill anki-monolingual-hints.

Process a limit of 200 notes with a batch size of 50. Parallelize where possible. Prefer atomic changes.
```

### Japanese Mining Deck Augmentation
Comprehensive augmentation for Japanese mining notes, adding frequency, mnemonics, monolingual hints, and i+1 sentences.

**Prompt:**
```text
In the deck "Language Japanese::Mining":
- use the skill anki-add-frequency.
- use the skill anki-add-notes with the target field "Notes", and prompt file "./kanji_mnemonic_prompt.txt".
- use the skill anki-add-sentence.

Process a limit of 200 notes with a batch size of 50. Parallelize where possible. Prefer atomic changes.
```

### Hindi Deck Augmentation
Full augmentation for new Hindi notes, adding frequency data, detailed grammar/cultural notes, and English translations.

**Prompt:**
```text
In the deck "Language Hindi::My hindi words and phrases":
- use the skill anki-add-frequency.
- use the skill anki-add-notes with the target field "Notes" and the prompt file "./explain_prompt.txt".
- use the skill anki-add-notes with the target field "ExpressionFurigana" and the prompt file "./translate_ja_prompt.txt".
- use the skill anki-add-notes with the target field "ExpressionEnglish" and the prompt file "./translate_prompt.txt".

Process a limit of 200 notes with a batch size of 50. Parallelize where possible. Prefer atomic changes.
```

---

## Important Notes

- **Back up your deck** using `anki-backup-deck` before running skills that modify your database.
- **AnkiConnect** must be configured to allow your AI agent to talk to Anki.
- Check your agent's documentation to verify that all workspace skills are properly loaded.

License: MIT
