# Anki Deck Augmenter

This tool automatically augments Anki decks by generating helpful explanations for cards that have an empty "Notes" field. It uses Google's Gemini AI to analyze the card's content and provide concise definitions, grammar points, or context.

## Features

- **AI-Powered Explanations:** Uses Gemini 3 Flash Preview to generate context-aware notes.
- **Two Modes of Operation:**
    - **File Mode:** Directly modifies `.apkg` files.
    - **AnkiConnect Mode:** Updates a running Anki instance via the AnkiConnect add-on.
- **Parallel Processing:** Processes multiple notes concurrently for fast execution.
- **Smart Augmentation:** Only targets notes where the "Notes" field is empty, preserving your existing manual notes.
- **Dry Run Support:** Preview which notes will be updated before making any changes.
- **Markdown Support:** Generates notes with Markdown formatting and converts them to HTML for Anki compatibility.

| Before | After |
| --- | --- |
| ![before](./resources/before.png) | ![after](./resources/after.png) |

## Prerequisites

- Python 3.9+
- A Google Gemini API Key
- The target Anki deck MUST have a "Notes" field located at exactly the index 2.
- (Optional) Anki with the [AnkiConnect](https://ankiweb.net/shared/info/2055492159) add-on installed.

## Installation

1.  **Clone the repository** (or download the script).

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up your API Key:**

    Set the `GEMINI_API_KEY` environment variable with your Google Gemini API key.

    **Mac/Linux:**
    ```bash
    export GEMINI_API_KEY="your_api_key_here"
    ```

    **Windows (PowerShell):**
    ```powershell
    $env:GEMINI_API_KEY="your_api_key_here"
    ```

## Usage

### Mode 1: AnkiConnect (Recommended for live decks)

Ensure Anki is open and AnkiConnect is installed.

```bash
# Basic usage (uses default model name "Cloze")
python augment_deck.py --anki-connect

# Specify a custom model name and perform a dry run
python augment_deck.py --anki-connect --model-name "My French Model" --dry-run
```

### Mode 2: File Mode

Processes a standalone `.apkg` file and creates a new augmented version.

```bash
python augment_deck.py --input "MyDeck.apkg" --output "MyDeck_Augmented.apkg"
```

### Command Line Arguments

- `--anki-connect`: Use AnkiConnect to update a running Anki instance.
- `--model-name`: (Optional) The name of the Note Type to augment. Defaults to "Cloze".
- `--input`: (Required in File Mode) Path to the source `.apkg` file.
- `--output`: (Required in File Mode) Path where the augmented `.apkg` file will be saved.
- `--dry-run`: Identify and list notes that would be updated without making any changes or API calls.

## How It Works

1.  **Discovery:** The script identifies notes belonging to the specified Model Name.
2.  **Filtering:** It scans for cards where the "Notes" field (mapped via index) is empty.
3.  **Generation:** It sends the card's text to the Gemini API to generate a helpful explanation using the `gemini-3-flash-preview` model.
4.  **Update:**
    - In **AnkiConnect mode**, it pushes the update directly to Anki.
    - In **File mode**, it extracts the `.apkg`, updates the internal SQLite database, and repackages it.

## Disclaimer

**Important:** This script was generated with the assistance of Large Language Models (LLMs). While it has been tested, the automated modification of Anki databases carries inherent risks. Always **back up your original Anki decks** or use Anki's built-in backup before using this tool. The authors and contributors are not responsible for any data loss, corruption, or other damages caused by the use of this software.
