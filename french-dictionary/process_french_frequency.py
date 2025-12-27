import csv
import os
from collections import defaultdict

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
FREQ_FILE = os.path.join(DATA_DIR, "fr_50k.txt")
LEXIQUE_FILE = os.path.join(DATA_DIR, "Lexique383.tsv")
OUTPUT_FILE = os.path.join(DATA_DIR, "french_lemma_frequency.csv")

def load_lexique(lexique_path):
    """
    Loads Lexique383 and returns a dict mapping word -> lemma.
    Resolves ambiguities by choosing the entry with highest film frequency.
    """
    print(f"Loading Lexique from {lexique_path}...")
    word_to_lemma = {}
    word_max_freq = {} # To track the max freq seen for a word to resolve conflicts

    with open(lexique_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        header = next(reader)
        # ortho=0, lemme=2, freqfilms2=8
        
        for row in reader:
            if len(row) < 9:
                continue
                
            word = row[0]
            lemma = row[2]
            try:
                freq = float(row[8])
            except ValueError:
                freq = 0.0
            
            # If word seen, keep the one with higher frequency
            if word in word_max_freq:
                if freq > word_max_freq[word]:
                    word_max_freq[word] = freq
                    word_to_lemma[word] = lemma
            else:
                word_max_freq[word] = freq
                word_to_lemma[word] = lemma
                
    print(f"Loaded {len(word_to_lemma)} words from Lexique.")
    return word_to_lemma

def process_frequency(freq_file, word_to_lemma):
    """
    Reads frequency list, lemmatizes words, aggregates counts.
    """
    print(f"Processing frequency list from {freq_file}...")
    lemma_counts = defaultdict(int)
    total_processed = 0
    lemmatized_count = 0
    
    with open(freq_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(' ')
            if len(parts) != 2:
                continue
            
            word, count_str = parts
            try:
                count = int(count_str)
            except ValueError:
                continue
            
            total_processed += 1
            
            # Try to lemmatize
            # Lexique is case-sensitive usually, but mostly lowercase.
            # fr_50k.txt seems to be lowercase based on 'head' output (de, je, est...)
            
            lemma = word_to_lemma.get(word)
            if not lemma:
                # Try lowercase if not found
                lemma = word_to_lemma.get(word.lower(), word)
            
            if lemma != word:
                lemmatized_count += 1
                
            lemma_counts[lemma] += count

    print(f"Processed {total_processed} words.")
    print(f"Lemmatized {lemmatized_count} words.")
    return lemma_counts

def save_counts(lemma_counts, output_path):
    print(f"Saving results to {output_path}...")
    # Sort by count desc
    sorted_items = sorted(lemma_counts.items(), key=lambda x: x[1], reverse=True)
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["lemma", "count"])
        for lemma, count in sorted_items:
            writer.writerow([lemma, count])
            
    print("Done.")

if __name__ == "__main__":
    if not os.path.exists(LEXIQUE_FILE):
        print(f"Error: {LEXIQUE_FILE} not found.")
        exit(1)
    if not os.path.exists(FREQ_FILE):
        print(f"Error: {FREQ_FILE} not found.")
        exit(1)
        
    word_to_lemma = load_lexique(LEXIQUE_FILE)
    lemma_counts = process_frequency(FREQ_FILE, word_to_lemma)
    save_counts(lemma_counts, OUTPUT_FILE)
