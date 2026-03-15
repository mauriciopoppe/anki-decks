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
  --note-type "My French" \
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
  --note-type "Lapis" \
  --target-field "Notes" \
  --prompt-file "./kanji_mnemonic_prompt.txt"
```

### Features
- **Smart Fill**: Only touches cards where the target field is empty.
- **Interactive Mode (`-i`)**: Review every AI response before it hits your deck.
- **Dynamic Prompts**: Use `{FieldName}` in your prompt files to pull data from your cards.
- **Auto-tagging**: Adds a date tag so you know exactly which cards were AI-augmented.

### Parameters
- `--note-type`: The Anki Note Type to process.
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
  --note-type "Japanese::Mining" \
  --total-notes 20 \
  --batch-size 5 \
  --prompt-file "./kanji_augment_sentences.txt"
```

### Features
- **Batched Processing**: Sends multiple words in a single AI prompt to save on API calls and maintain consistency.
- **i+1 Logic**: Replaces `{LEARNED_WORDS}` in your prompt with your actual progress to ensure sentences stay readable.
- **Frequency Sorting**: Automatically prioritizes more common words by sorting by `FreqSort`.

### Parameters
- `--note-type`: The Anki Note Type to process (e.g., "Japanese::Mining").
- `--total-notes`: Maximum number of notes to process in one run.
- `--batch-size`: Number of words to include in each AI prompt.
- `--prompt-file`: Template file. Use `{TARGET_WORDS}` and `{LEARNED_WORDS}` placeholders.
- `--interactive (-i)`: Review each batch before it's saved.
- `--dry-run`: List the words that would be processed without calling the AI.

---

## Important Notes

- **Back up your deck** before running scripts that modify your database.
- **Watch your API costs**. If you're processing thousands of cards, consider using a local model with Ollama.
- **AnkiConnect** must be configured to allow the script to talk to Anki (usually works out of the box).

License: MIT
