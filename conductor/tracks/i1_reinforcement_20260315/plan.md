# Implementation Plan: i+1 Sentence Reinforcement

## Phase 1: Preparation & Data Extraction
- [x] Task: Create a Python script to extract "learned" vocabulary from Anki.
    - [x] Connect to AnkiConnect.
    - [x] Query `Japanese::Kaishi 1.5k` and `Japanese::Mining` for cards with `Interval > 0`.
    - [x] Export the list of unique "Expression" values to a local file (e.g., `learned_words.txt`).
- [x] Task: Verify the extracted "learned" word list.
    - [x] Inspect the output to ensure it correctly reflects learned words.

## Phase 2: i+1 Logic & AI Prompting
- [x] Task: Develop the AI prompt for "i+1" sentence generation.
    - [x] Create a prompt that includes the "learned" word list as context.
    - [x] Specify constraints: exactly one new word (the target), "Daily Life" context, and "Dynamic" grammar.
    - [x] Request output in a structured format: Raw Sentence, Furigana (Anki format), and English Translation.
- [x] Task: Test the prompt with sample words from the Mining deck.
    - [x] Run test generations for 3-5 words.
    - [x] Verify that the "i+1" constraint is met.

## Phase 3: Bulk Processing & Deck Update
- [x] Task: Implement the bulk update script.
    - [x] Read the `Japanese::Mining` deck and sort words by `FreqSort`.
    - [x] For each word with empty `Sentence` fields, call the AI to generate content.
    - [x] Use `augment_notes.py` (or a specialized extension) to update Anki.
- [x] Task: Run the bulk update for the first batch of words.
    - [x] Start with a small batch (e.g., 10-20 words) to verify performance and accuracy.
- [x] Task: Complete the update for all words in the Mining deck.
