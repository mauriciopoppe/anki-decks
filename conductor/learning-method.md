# Preferred Learning Method: The "Kaishi 1.5k" Approach

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

## Current Deck Structure: Japanese::Mining (Model: Lapis)

The following fields define the current structure of the **Japanese::Mining** deck (using the **Lapis** note type):

1.  **Expression:** The target word or phrase in Japanese.
2.  **ExpressionFurigana:** Furigana for the expression.
3.  **ExpressionReading:** Reading of the expression.
4.  **ExpressionAudio:** Audio for the expression.
5.  **SelectionText:** Contextual text from which the expression was selected.
6.  **MainDefinition:** The primary dictionary definition.
7.  **DefinitionPicture:** An image associated with the definition.
8.  **Sentence:** The example sentence containing the target word (typically bolded).
9.  **SentenceFurigana:** The example sentence with Furigana.
10. **SentenceEnglish:** The English translation of the sentence.
11. **SentenceAudio:** Audio for the example sentence.
12. **Picture:** An image illustrating the example sentence.
13. **Glossary:** Additional dictionary/lookup information.
14. **Hint:** A hint for the card.
15. **IsWordAndSentenceCard:** Flag for creating word+sentence cards.
16. **IsClickCard:** Flag for interactive cards.
17. **IsSentenceCard:** Flag for dedicated sentence cards.
18. **IsAudioCard:** Flag for dedicated audio cards.
19. **PitchPosition:** Numeric pitch accent information.
20. **PitchCategories:** Descriptive pitch accent categories.
21. **Frequency:** Raw frequency data.
22. **FreqSort:** Numerical frequency field used for sorting.
23. **MiscInfo:** Sources or additional metadata.
24. **Notes:** Any additional user notes.

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
