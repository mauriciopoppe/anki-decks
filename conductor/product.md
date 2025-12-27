# Initial Concept
A collection of AI-powered scripts to automate and enhance Anki deck management using Google's Gemini AI.

## Target Audience
The primary users of these tools are **language learners** who use Anki for vocabulary and grammar retention. They typically manage large decks and need efficient ways to enrich their cards with high-quality study aids without manual effort.

## Core Goals
- **Automate high-quality study materials:** Focus on generating mnemonics and explanations that aid memory and understanding.
- **Save time through automation:** Enable users to bulk-populate empty fields in their Anki cards using AI, reducing manual research and entry.
- **Provide context-aware learning:** Ensure that all generated content is deeply relevant to the specific word, sentence, or context provided in the card's existing fields.

## Key Features
- **`augment_notes.py` Script:** A versatile tool that uses configurable AI prompts to extract data from card fields and populate target fields with generated content.
- **AnkiConnect Integration:** Seamlessly update a running Anki instance, allowing for immediate feedback and iterative deck improvement.
- **Configurable Prompt Templates:** Support for `{FieldName}` placeholders to dynamically insert card data into AI instructions.
- **Smart Filtering:** Automatically targets only the cards where the destination field is empty, avoiding redundant API calls and data overwrites.
- **French Frequency Dictionary Generator:** A tool to create Yomitan-compatible frequency dictionaries from OpenSubtitles data, utilizing Lexique 3 for accurate lemmatization.
