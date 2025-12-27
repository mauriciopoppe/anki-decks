# Specification - French Frequency Dictionary for Yomitan

## Overview
This track involves creating a tool to generate a French frequency dictionary compatible with Yomitan, using data from the OpenSubtitles (LREC) corpus. The tool will handle the entire pipeline from data acquisition to the final Yomitan-ready zip file.

## Functional Requirements
- **Data Acquisition:** Automatically download or provide instructions for acquiring the OpenSubtitles (LREC) French frequency data.
- **Lemmatization:** Process the raw subtitle data to aggregate frequencies based on the dictionary form (lemma) of words.
- **Yomitan Format Generation:** Convert the processed frequency data into the specific JSON schema required by Yomitan for frequency dictionaries.
- **Packaging:** Create a zipped dictionary file (`.zip`) that can be directly imported into Yomitan.
- **CLI Interface:** Provide a Python script to trigger the generation process.

## Non-Functional Requirements
- **Efficiency:** The script should handle large frequency datasets (tens of thousands of words) in a reasonable timeframe.
- **Correctness:** The output must strictly adhere to the Yomitan dictionary specification to ensure compatibility.
- **Dependency Management:** All necessary Python libraries (e.g., for lemmatization or file processing) must be added to `requirements.txt`.

## Acceptance Criteria
- [ ] A script exists that can process French frequency data.
- [ ] The output is a `.zip` file containing valid Yomitan JSON files (`index.json` and frequency data JSONs).
- [ ] The dictionary can be successfully imported into Yomitan.
- [ ] Word frequencies are correctly aggregated by lemma.
- [ ] The dictionary correctly displays the rank of French words when scanned in Yomitan.

## Out of Scope
- Creating a general-purpose dictionary (definitions, audio, etc.). This track is strictly for **frequency data**.
- Processing corpora other than French subtitles for now.
- Building a GUI; this will be a CLI-based tool.
