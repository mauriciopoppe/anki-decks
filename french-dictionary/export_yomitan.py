import csv
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
INPUT_FILE = os.path.join(DATA_DIR, "french_lemma_frequency.csv")
BUILD_DIR = os.path.join(os.path.dirname(__file__), "yomitan_build")

def generate_yomitan_files():
    if not os.path.exists(BUILD_DIR):
        os.makedirs(BUILD_DIR)
        
    # 1. index.json
    index = {
        "title": "French Frequency (OpenSubtitles 2018)",
        "format": 3,
        "revision": "2025.12.27",
        "sequenced": False,
        "author": "Conductor",
        "description": "Frequency dictionary based on OpenSubtitles 2018 data, lemmatized using Lexique 3."
    }
    
    with open(os.path.join(BUILD_DIR, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
        
    # 2. term_meta_bank_1.json
    term_meta_bank = []
    
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader) # skip header
        
        rank = 1
        for row in reader:
            if not row: continue
            term = row[0]
            # row[1] is count, we use rank
            
            # Entry: [term, "freq", rank]
            term_meta_bank.append([term, "freq", rank])
            rank += 1
            
    with open(os.path.join(BUILD_DIR, "term_meta_bank_1.json"), "w", encoding="utf-8") as f:
        json.dump(term_meta_bank, f, ensure_ascii=False, separators=(',', ':'))
        
    print(f"Generated Yomitan files in {BUILD_DIR}")
    print(f"Total entries: {len(term_meta_bank)}")

if __name__ == "__main__":
    generate_yomitan_files()
