# Anki Decks

`augment_deck.py` This tool automatically augments Anki decks (`.apkg` files) by generating helpful explanations for cards that have an empty "Notes" field. It uses Google's Gemini AI to analyze the content of the card and provide concise definitions, grammar points, or context.

## Disclaimer

**Important:** This script was generated with the assistance of Large Language Models (LLMs). While it has been tested, the automated modification of Anki databases carries inherent risks. Always **back up your original Anki decks** before using this tool. The authors and contributors are not responsible for any data loss, corruption, or other damages caused by the use of this software.

## Features

- **AI-Powered Explanations:** Uses Gemini Flash to generate context-aware notes for French vocabulary and phrases (customizable in code).
- **Parallel Processing:** Processes multiple notes concurrently for fast execution.
- **Smart Augmentation:** Only targets notes where the specific "Notes" field is empty, preserving your existing manual notes.
- **Markdown Support:** Generates notes with Markdown formatting and converts them to HTML for Anki compatibility.

## Prerequisites

- Python 3.9+
- A Google Gemini API Key
- An Anki deck that has the following fields: `Text,Frequency,Notes,Image`. The deck must have those fields and in that order.

## Installation

1.  **Clone the repository** (or download the script).

2.  **Install dependencies:**

    ```bash
    pip install google-generativeai zstandard markdown tqdm
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

Run the script from the command line, specifying the input Anki deck and the desired output filename.

```bash
python augment_deck.py --input "MyDeck.apkg" --output "MyDeck_Augmented.apkg"
```

### Arguments

- `--input`: (Required) Path to the source `.apkg` file.
- `--output`: (Required) Path where the augmented `.apkg` file will be saved.

## How It Works

1.  **Extraction:** Unzips the `.apkg` file and extracts the SQLite database (`collection.anki21b` or `collection.anki2`).
2.  **Analysis:** Scans the database for notes belonging to a specific Model ID (currently hardcoded for a specific French deck format, can be modified in the script).
3.  **Generation:** Identifies cards with empty "Notes" fields. It sends the card's text to the Gemini API to generate a helpful explanation.
4.  **Update:** Updates the database with the generated HTML content.
5.  **Repackaging:** Compresses the database using Zstandard and zips everything back into a valid `.apkg` file ready for import into Anki.

## Configuration

The script currently targets a specific Anki Model ID and field structure. You may need to adjust the constants at the top of `augment_deck.py` to match your specific deck's structure:

- `MODEL_ID`: The ID of the Note Type you want to augment.
- `FIELD_INDEX_TEXT`: The index of the field containing the source text (0-based).
- `FIELD_INDEX_NOTES`: The index of the field where the generated note should be stored.

