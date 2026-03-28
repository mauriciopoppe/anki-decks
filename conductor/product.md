# Initial Concept
A collection of AI Workspace Skills to automate and enhance Anki deck management.

## Target Audience
The primary users of these tools are **language learners** who use Anki for vocabulary and grammar retention. They typically manage large decks and need efficient ways to enrich their cards with high-quality study aids without manual effort.

## Core Goals
- **Automate high-quality study materials:** Focus on generating mnemonics and explanations that aid memory and understanding.
- **Save time through automation:** Enable users to bulk-populate empty fields in their Anki cards using an AI agent, reducing manual research and entry.
- **Provide context-aware learning:** Ensure that all generated content is deeply relevant to the specific word, sentence, or context provided in the card's existing fields.

## Learning Methodology: The "Kaishi 1.5k" Approach

Based on an analysis of the "Kaishi 1.5k" Japanese deck, the following principles define the preferred method for effective card creation and reinforcement:

### 1. "i+1" Sentence Design
The deck follows a strict **"i+1" (one new piece of information)** philosophy. Each card introduces a single new **target word**, but the example sentence surrounding it is composed almost entirely of words already learned in previous cards.
*   **Example:** When learning the word **私 (I)**, the sentence is `私はアンです` (I am Ann). Later, when learning **好き (like)**, the sentence `私はワインが好きです` (I like wine) reuses the `私は...です` structure and the word `私` already known.

### 2. Sentence Sharing across Multiple Notes
Unlike many decks where every word has a unique sentence, this approach frequently **shares the exact same sentence** across 2 or 3 different target words.
*   **Target Word A:** あなた (You) → Sentence: `あなたはトムさんですか।`
*   **Target Word B:** さん (San) → Sentence: `あなたはトムさんですか।`
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
- **`anki-add-notes` Workspace Skill:** Orchestrates the AI augmentation of Anki notes via AnkiConnect using configurable prompt templates.
- **`anki-add-sentence` Workspace Skill:** A batched i+1 augmentation tool that generates natural example sentences based on a user's learned vocabulary (extracted via `extract_learned_vocab.py`).
- **`anki-add-translation` Workspace Skill:** A procedural workflow that automatically translates Anki note fields into English, handling normalization and batched processing.
- **`anki-add-frequency` Workspace Skill:** Estimates conversational commonality (1-1000) for learning targets, helping prioritize vocabulary.
- **Interactive Review Mode:** Review and approve AI-generated changes note-by-note (or batch-by-batch) to ensure quality and control before updating the deck.
- **AnkiConnect Integration:** Seamlessly update a running Anki instance, allowing for immediate feedback and iterative deck improvement.
- **Smart Filtering:** Automatically targets only the cards where the destination field is empty, avoiding redundant API calls and data overwrites.
- **French Frequency Dictionary Generator:** A tool to create Yomitan-compatible frequency dictionaries from OpenSubtitles data, utilizing Lexique 3 for accurate lemmatization.

## Card Templates & Synchronization

HTML and CSS templates for various note types are version-controlled in the `note-types-templates/` directory.

### How to Synchronize Templates to Anki

To synchronize local files with Anki, use the **Anki-Connect** API. The general one-liner for synchronization reads the local HTML/CSS files and updates the model templates and styling in a single command.

#### 1. Japanese::Mining (Lapis Model)
- **Path:** `note-types-templates/mining/`
- **Anki Model:** `Lapis`
- **Template Name:** `Mining`

```bash
curl -s -X POST http://localhost:8765 -d "$(jq -n \
  --arg f "$(cat note-types-templates/mining/front.html)" \
  --arg b "$(cat note-types-templates/mining/back.html)" \
  '{action: "updateModelTemplates", version: 6, params: {model: {name: "Lapis", templates: {Mining: {Front: $f, Back: $b}}}}}')" && \
  curl -s -X POST http://localhost:8765 -d "$(jq -n \
  --arg s "$(cat note-types-templates/mining/styling.css)" \
  '{action: "updateModelStyling", version: 6, params: {model: {name: "Lapis", css: $s}}}')"
```

#### 2. My Cloze Model
- **Path:** `note-types-templates/my-cloze/`
- **Anki Model:** `My Cloze`
- **Template Name:** `Cloze`

```bash
curl -s -X POST http://localhost:8765 -d "$(jq -n \
  --arg f "$(cat note-types-templates/my-cloze/front.html)" \
  --arg b "$(cat note-types-templates/my-cloze/back.html)" \
  '{action: "updateModelTemplates", version: 6, params: {model: {name: "My Cloze", templates: {Cloze: {Front: $f, Back: $b}}}}}')" && \
  curl -s -X POST http://localhost:8765 -d "$(jq -n \
  --arg s "$(cat note-types-templates/my-cloze/styling.css)" \
  '{action: "updateModelStyling", version: 6, params: {model: {name: "My Cloze", css: $s}}}')"
```

*Note: You must ensure that the model names and template names match your actual Anki setup.*
