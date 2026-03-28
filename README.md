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
3. **Set your API key**:
   ```bash
   export GEMINI_API_KEY="your_key_here" # or OPENAI_API_KEY, etc.
   ```
4. **Make sure [AnkiConnect](https://ankiweb.net/shared/info/2055492159) is installed** and Anki is running.

---

## `augment_notes.py`

This script scans your deck for empty fields and fills them using an LLM. It uses [LiteLLM](https://docs.litellm.ai/docs/providers), so it works with Gemini, OpenAI, Anthropic, or local models via Ollama.

### Examples

#### 1. Explain French Sentences
Takes a Cloze deletion like `Sur ça, tu touches un point {{c1::assez juste}}` and adds a detailed explanation to the "Notes" field.

| Before | After |
| --- | --- |
| ![before](./resources/french-explain-before.png) | ![after](./resources/french-explain-after.png) |

```bash
python augment_notes.py \
  --deck "Language French::My french words and phrases" \
  --target-field "Notes" \
  --prompt-file "./french_explain_prompt.txt"
```

#### 2. Generate Kanji Mnemonics
Uses the Kanji and its meaning to create a story that helps you remember the shape and sound.

| Card |
| --- |
| ![after](./resources/kanji-mnemonic-after.png) |

```bash
python augment_notes.py \
  --deck "Language Japanese::Mining" \
  --target-field "Notes" \
  --prompt-file "./kanji_mnemonic_prompt.txt"
```

### Features
- **Smart Fill**: Only touches cards where the target field is empty.
- **Interactive Mode (`-i`)**: Review every AI response before it hits your deck.
- **Dynamic Prompts**: Use `{FieldName}` in your prompt files to pull data from your cards.
- **Auto-tagging**: Adds a date tag so you know exactly which cards were AI-augmented.

### Parameters
- `--deck`: The Anki Deck Name to process. Note type is inferred automatically.
- `--target-field`: The field you want to fill (e.g., "Notes").
- `--prompt-file`: Path to your prompt template. Use `{FieldName}` placeholders to pull data from your cards. See the bundled [French](./french_explain_prompt.txt) and [Kanji](./kanji_mnemonic_prompt.txt) templates for examples.
- `--model`: Defaults to `gemini/gemini-2.0-flash`. Use any LiteLLM string.
- `--dry-run`: See what would happen without changing anything.

---

## `augment_sentences.py`

This script performs **batched i+1 augmentation**. It takes a list of target words and generates example sentences that only use vocabulary you've already learned. Perfect for reinforcing new words in a familiar context.

### Example

Generates sentences for your Japanese mining deck based on your known vocabulary.

```bash
python augment_sentences.py \
  --deck "Japanese::Mining" \
  --total-notes 20 \
  --batch-size 5 \
  --prompt-file "./kanji_augment_sentences.txt"
```

### Features
- **Batched Processing**: Sends multiple words in a single AI prompt to save on API calls and maintain consistency.
- **i+1 Logic**: Replaces `{LEARNED_WORDS}` in your prompt with your actual progress to ensure sentences stay readable.
- **Frequency Sorting**: Automatically prioritizes more common words by sorting by `FreqSort`.

### Parameters
- `--deck`: The Anki Deck Name to process (e.g., "Japanese::Mining"). Note type is inferred automatically.
- `--total-notes`: Maximum number of notes to process in one run.
- `--batch-size`: Number of words to include in each AI prompt.
- `--prompt-file`: Template file. Use `{TARGET_WORDS}` and `{LEARNED_WORDS}` placeholders.
- `--interactive (-i)`: Review each batch before it's saved.
- `--dry-run`: List the words that would be processed without calling the AI.

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
