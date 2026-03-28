# Anki Decks & Tools

A set of scripts to make Anki smarter using AI. I use these to automatically fill in details like mnemonics, grammar explanations, or example sentences so I can focus on actually learning.

## Quick Start

1. **Set up a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Make sure [AnkiConnect](https://ankiweb.net/shared/info/2055492159) is installed** and Anki is running.

---

## Workspace Skill: `anki-add-notes`

This skill provides a procedural workflow to orchestrate the AI augmentation of Anki notes via AnkiConnect. It scans your deck for empty fields and fills them using a prompt template read from a file.

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

### Parameters
- `--deck`: (Required) The Anki Deck Name to process.
- `--target-field`: (Required) The field you want to fill (e.g., "Notes").
- `--prompt-file`: (Required) Path to your prompt template. Use `{FieldName}` placeholders to pull data from your cards. See the bundled [Explanation](./explain_prompt.txt) and [Kanji](./kanji_mnemonic_prompt.txt) templates for examples.
- `--total-notes`: (Optional) Limit the number of notes processed.
- `--sort-field`: (Optional) The field to use for sorting notes. Defaults to `FreqSort`.
- `--interactive` / `-i`: (Optional) Review every AI response before it hits your deck.
- `--dry-run`: (Optional) List the notes that would be processed without calling the AI.

---

## Workspace Skill: `anki-add-sentence`

Generates **i+1 example sentences** for Anki learning targets. Ensures sentences only use words you've already learned (from `learned_words.txt`) plus the target word.

### Example

**Prompt:**
> Use anki-add-sentence for deck "Japanese::Mining". Process 5 notes.

### Parameters
- `--deck`: (Required) The Anki Deck Name to process.
- `--source-field`: (Optional) Field with the target word. Defaults to `Expression`.
- `--target-field`: (Optional) Field for the generated sentence. Defaults to `Sentence`.
- `--target-field-english`: (Optional) Field for the English translation. Defaults to `SentenceEnglish`.
- `--total-notes`: (Optional) Limit processing. Defaults to `20`.
- `--batch-size`: (Optional) Notes per AI request. Defaults to `5`.
- `--dry-run`: (Optional) Preview words to be processed.

---

## Workspace Skill: `anki-add-frequency`

Estimates how common a word or phrase is in a conversational setting (1-1000) and fills an Anki field. 1 is very common, 1000 is rare.

### Example

**Prompt:**
> Use anki-add-frequency for deck "Japanese::Mining". Process 10 notes.

### Parameters
- `--deck`: (Required) The Anki Deck Name to process.
- `--target-field`: (Optional) Field for the frequency number. Defaults to `Frequency`.
- `--total-notes`: (Optional) Limit processing. Defaults to `20`.
- `--batch-size`: (Optional) Notes per AI request. Defaults to `5`.
- `--dry-run`: (Optional) Preview results only.

---

## Workspace Skill: `anki-add-translation`

This workspace skill provides a procedural workflow to automatically translate Anki note fields into English using Gemini. It handles Anki cloze formatting, deduplicates sentences for efficiency, and updates your deck in batches.

### Examples

#### 1. Basic Translation
Translate Japanese sentences in your mining deck to English.

**Prompt:**
> Use the skill anki-add-translation with the deck "Japanese::Mining", source field "Sentence", target field "SentenceEnglish".

#### 2. Specific Scope
Translate only a few notes from a Hindi deck.

**Prompt:**
> Use anki-add-translation for deck "Language Hindi::My hindi words and phrases", source "Expression", target "ExpressionEnglish". Process only 5 notes.

### Parameters
- `--deck`: (Required) The Anki Deck Name to process.
- `--target-field`: (Optional) The field where the translation will be stored. Defaults to `ExpressionEnglish`.
- `--source-field`: (Optional) The field containing the text to translate. Defaults to `Expression`.
- `--total-notes`: (Optional) Limit the number of notes processed. Defaults to `20`.
- `--batch-size`: (Optional) Number of strings per translation request. Defaults to `5`.
- `--dry-run`: (Optional) Preview translations without updating Anki.

---

## Important Notes

- **Back up your deck** before running scripts that modify your database.
- **Watch your API costs**. If you're processing thousands of cards, consider using a local model with Ollama.
- **AnkiConnect** must be configured to allow the script to talk to Anki (usually works out of the box).

License: MIT
