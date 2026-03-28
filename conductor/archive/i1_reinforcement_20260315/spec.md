# Specification: i+1 Sentence Reinforcement for Japanese::Mining

## Overview
This track aims to enrich the `Japanese::Mining` Anki deck by populating the `Sentence`, `SentenceFurigana`, and `SentenceEnglish` fields with high-quality "i+1" sentences. These sentences will be specifically designed to reinforce vocabulary you have already learned in both the `Japanese::Kaishi 1.5k` and `Japanese::Mining` decks.

## Functional Requirements
1. **Vocabulary Extraction:**
   - Identify "learned" words from both the `Japanese::Kaishi 1.5k` and `Japanese::Mining` decks. 
   - A word is considered "learned" if its card interval is greater than 0 (`Interval > 0`).
2. **Target Prioritization:**
   - Process target words in the `Japanese::Mining` deck sorted by the `Frequency` field.
3. **Sentence Generation (i+1):**
   - For each target word, generate a sentence where the target word is the only "new" piece of vocabulary.
   - All other vocabulary in the sentence must be from the "learned" word list.
   - Grammar should be "Dynamic," matching the approximate level of the learned vocabulary.
   - The context should focus on "Daily Life" situations.
4. **Field Population:**
   - **Sentence:** The raw Japanese sentence with the target word highlighted (e.g., in bold).
   - **SentenceFurigana:** The sentence using Anki's standard furigana format (`漢字[ふりがな]`).
   - **SentenceEnglish:** A clear English translation of the generated sentence.
5. **Automation:**
   - Utilize AI (Gemini) to generate the sentences and translations based on the provided "learned" context.

## Non-Functional Requirements
- **Consistency:** Maintain the tone and style of existing high-quality Japanese decks.
- **Accuracy:** Ensure Furigana accurately reflects the readings within the specific sentence context.

## Acceptance Criteria
- [ ] A script or mechanism exists to extract the "learned" vocabulary list from Anki.
- [ ] Target words in the `Japanese::Mining` deck are updated with new sentences.
- [ ] Generated sentences contain exactly one new word (the target) relative to the learned list.
- [ ] `SentenceFurigana` and `SentenceEnglish` fields are correctly populated.

## Out of Scope
- Generating audio for the new sentences.
- Modifying the underlying note types or card styling.
