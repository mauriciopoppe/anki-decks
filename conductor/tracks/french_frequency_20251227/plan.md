# Plan - French Frequency Dictionary for Yomitan

## Phase 1: Environment and Data Acquisition
- [x] Task: Add necessary dependencies to `requirements.txt` (spacy, fr_core_news_sm, etc.)
- [ ] Task: Write failing tests for the data acquisition/loading module
- [ ] Task: Implement the data acquisition/loading module for OpenSubtitles LREC data
- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Processing and Lemmatization
- [ ] Task: Write failing tests for the lemmatization and frequency aggregation logic
- [ ] Task: Implement French lemmatization and frequency ranking logic
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Yomitan Export and Packaging
- [ ] Task: Write failing tests for Yomitan JSON generation and zipping
- [ ] Task: Implement Yomitan JSON schema generation (index.json, term_meta)
- [ ] Task: Implement zip packaging logic
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)
