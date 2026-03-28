# Initial Concept
A collection of AI-powered scripts to automate and enhance Anki deck management using Google's Gemini AI.

## Target Audience
The primary users of these tools are **language learners** who use Anki for vocabulary and grammar retention. They typically manage large decks and need efficient ways to enrich their cards with high-quality study aids without manual effort.

## Core Goals
- **Automate high-quality study materials:** Focus on generating mnemonics and explanations that aid memory and understanding.
- **Save time through automation:** Enable users to bulk-populate empty fields in their Anki cards using AI, reducing manual research and entry.
- **Provide context-aware learning:** Ensure that all generated content is deeply relevant to the specific word, sentence, or context provided in the card's existing fields.

## Learning Methodology: The "Kaishi 1.5k" Approach

Based on an analysis of the "Kaishi 1.5k" Japanese deck, the following principles define the preferred method for effective card creation and reinforcement:

### 1. "i+1" Sentence Design
The deck follows a strict **"i+1" (one new piece of information)** philosophy. Each card introduces a single new **target word**, but the example sentence surrounding it is composed almost entirely of words already learned in previous cards.
*   **Example:** When learning the word **私 (I)**, the sentence is `私はアンです` (I am Ann). Later, when learning **好き (like)**, the sentence `私はワインが好きです` (I like wine) reuses the `私は...です` structure and the word `私` already known.

### 2. Sentence Sharing across Multiple Notes
Unlike many decks where every word has a unique sentence, this approach frequently **shares the exact same sentence** across 2 or 3 different target words.
*   **Target Word A:** あなた (You) → Sentence: `あなたはトムさんですか。`
*   **Target Word B:** さん (San) → Sentence: `あなたはトムさんですか。`
This ensures that when moving from Word A to Word B, the word is seen in a familiar "habitat," which reduces cognitive load and reinforces the grammar and vocabulary of the shared sentence.

### 3. Gradual Structural Expansion
The method reuses **grammatical frameworks** to provide scaffolding.
*   Early cards establish basic patterns like `[A] は [B] です` (A is B).
*   Subsequent cards slowly swap in new subjects, objects, or verbs into those established patterns.
*   By the time complex sentences are reached, the "scaffolding" (particles, pronouns, and common verbs) is already second nature.

### 4. Visual and Auditory Consistency
*   **Consistency:** The same audio and images are often used for shared sentences, creating a strong mental link between the sound, the context, and the words.
*   **Focus:** The target word is typically **bolded** in the `Sentence` field on the front of the card, making it clear what the new "variable" is in the familiar sentence.

### Summary of the Logic
This approach works like a **ladder**: each new word is a new rung, but the side rails (the sentences) stay the same for several rungs, providing a stable grip as you climb. Words are not learned in isolation; they are learned by how they "slot" into understood sentences.

## Key Features
- **`augment_notes.py` Script:** A versatile tool that uses configurable AI prompts and AnkiConnect to extract data from card fields and populate target fields with generated content.
- **`augment_sentences.py` Script:** A batched i+1 augmentation tool that generates example sentences based on a user's learned vocabulary, reinforcing new words in a familiar context.
- **`augment_translation.py` Script:** Automatically translates Anki note fields into English using Google Translate (via deep-translator).
- **Interactive Review Mode:** Review and approve AI-generated changes note-by-note (or batch-by-batch) to ensure quality and control before updating the deck.
- **AnkiConnect Integration:** Seamlessly update a running Anki instance, allowing for immediate feedback and iterative deck improvement.
- **Configurable Prompt Templates:** Support for `{FieldName}` placeholders to dynamically insert card data into AI instructions.
- **Smart Filtering:** Automatically targets only the cards where the destination field is empty, avoiding redundant API calls and data overwrites.
- **French Frequency Dictionary Generator:** A tool to create Yomitan-compatible frequency dictionaries from OpenSubtitles data, utilizing Lexique 3 for accurate lemmatization.

## Card Templates & Synchronization

The HTML and CSS templates for the **Japanese::Mining** (Lapis model) deck are version-controlled in this repository:
*   **Front:** `note-types-templates/mining/front.html`
*   **Back:** `note-types-templates/mining/back.html`
*   **Styling:** `note-types-templates/mining/styling.css`

### How to Synchronize Templates to Anki

To synchronize these local files with Anki, you can use the **Anki-Connect** API. Here is the general workflow:

1.  **Read the local files:** Read the contents of the `front.html`, `back.html`, and `styling.css` files.
2.  **Use `updateModelTemplates`:** Call the `updateModelTemplates` action via Anki-Connect to update the Front and Back HTML for the "Lapis" model.
    ```bash
    curl -X POST http://localhost:8765 -d '{
        "action": "updateModelTemplates",
        "version": 6,
        "params": {
            "model": {
                "name": "Lapis",
                "templates": {
                    "Card 1": {
                        "Front": "...",
                        "Back": "..."
                    }
                }
            }
        }
    }'
    ```
3.  **Use `updateModelStyling`:** Call the `updateModelStyling` action to update the CSS.
    ```bash
    curl -X POST http://localhost:8765 -d '{
        "action": "updateModelStyling",
        "version": 6,
        "params": {
            "model": {
                "name": "Lapis",
                "css": "..."
            }
        }
    }'
    ```

The user uses this one liner to update the settings on their own:

```bash
curl -s -X POST http://localhost:8765 -d "$(jq -n \
  --arg f "$(cat note-types-templates/mining/front.html)" \
  --arg b "$(cat note-types-templates/mining/back.html)" \
  '{action: "updateModelTemplates", version: 6, params: {model: {name: "Lapis", templates: {Mining: {Front: $f, Back: $b}}}}}')" && \
  curl -s -X POST http://localhost:8765 -d "$(jq -n \
  --arg s "$(cat note-types-templates/mining/styling.css)" \
  '{action: "updateModelStyling", version: 6, params: {model: {name: "Lapis", css: $s}}}')"
```

*Note: You must ensure that the "Lapis" model exists in Anki and that the template name ("Card 1") matches your actual setup.*
