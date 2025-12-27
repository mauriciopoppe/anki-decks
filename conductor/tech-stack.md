# Tech Stack - Anki Automation Tools

## Core Technologies
- **Python 3.9+:** The primary programming language for all automation scripts.
- **LiteLLM:** Used as a unified interface to interact with various LLM providers (Gemini, Ollama, etc.), ensuring flexibility in model selection.
- **AnkiConnect:** The bridge for interacting with a running Anki instance via its RESTful API.

## Data and File Handling
- **zstandard (zstd):** Required for compressing and decompressing modern Anki `.apkg` and `.colpkg` files.
- **requests:** Used for making HTTP requests to the AnkiConnect API.
- **tqdm:** Used for displaying progress bars during long-running operations like data downloads.
- **Lexique 3:** Used as the primary linguistic database for French lemmatization.

## Development and Quality
- **Ruff:** Fast Python linter and code formatter to ensure code quality and consistency.
- **Pytest:** (Inferred) Testing framework for verifying script logic and API integrations.

## Environment Management
- **Pip:** Standard package installer for Python dependencies listed in `requirements.txt`.
