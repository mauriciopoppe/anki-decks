# Implementation Plan: i+1 Sentence Reinforcement

## Phase 1: Preparation & Data Extraction
- [ ] Task: Create a Python script to extract "learned" vocabulary from Anki.
    - [ ] Connect to AnkiConnect.
    - [ ] Query `Japanese::Kaishi 1.5k` and `Japanese::Mining` for cards with `Interval > 0`.
    - [ ] Export the list of unique "Expression" values to a local file (e.g., `learned_words.txt`).
- [ ] Task: Verify the extracted "learned" word list.
    - [ ] Inspect the output to ensure it correctly reflects learned words.

## Phase 2: i+1 Logic & AI Prompting
- [ ] Task: Develop the AI prompt for "i+1" sentence generation.
    - [ ] Create a prompt that includes the "learned" word list as context.
    - [ ] Specify constraints: exactly one new word (the target), "Daily Life" context, and "Dynamic" grammar.
    - [ ] Request output in a structured format: Raw Sentence, Furigana (Anki format), and English Translation.
- [ ] Task: Test the prompt with sample words from the Mining deck.
    - [ ] Run test generations for 3-5 words.
    - [ ] Verify that the "i+1" constraint is met.

## Phase 3: Bulk Processing & Deck Update
- [ ] Task: Implement the bulk update script.
    - [ ] Read the `Japanese::Mining` deck and sort words by `FreqSort`.
    - [ ] For each word with empty `Sentence` fields, call the AI to generate content.
    - [ ] Use `augment_notes.py` (or a specialized extension) to update Anki.
- [ ] Task: Run the bulk update for the first batch of words.
    - [ ] Start with a small batch (e.g., 10-20 words) to verify performance and accuracy.
- [ ] Task: Complete the update for all words in the Mining deck.
