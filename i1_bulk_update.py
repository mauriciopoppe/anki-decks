import os
import sys
import argparse
import requests
import json
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import litellm

class LiteLLMClient:
    def __init__(self, model):
        self.model = model

    def generate(self, prompt):
        try:
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"LiteLLM Error ({self.model}): {e}")
            return None

def invoke_anki(action, **params):
    try:
        request_json = json.dumps({"action": action, "version": 6, "params": params})
        response = requests.post("http://localhost:8765", data=request_json).json()
        if response["error"] is not None:
            raise Exception(response["error"])
        return response["result"]
    except Exception as e:
        print(f"AnkiConnect Error: {e}")
        sys.exit(1)

def clean_json_response(text):
    # Strip markdown code blocks if present
    if text.startswith("```"):
        text = re.sub(r"```json\n?|```", "", text).strip()
    return text

def process_batch(llm_client, batch_notes, prompt_template, learned_words):
    target_words = [n['fields']['Expression'] for n in batch_notes]
    target_words_str = "\n".join(target_words)

    filled_prompt = prompt_template.replace("{LEARNED_WORDS}", learned_words).replace("{TARGET_WORDS}", target_words_str)

    generated_text = llm_client.generate(filled_prompt)
    if not generated_text:
        return []

    try:
        clean_json = clean_json_response(generated_text)
        data = json.loads(clean_json)

        batch_updates = []
        for note in batch_notes:
            word = note['fields']['Expression']
            if word in data:
                res = data[word]
                if all(k in res for k in ("sentence", "english")):
                    batch_updates.append((note['id'], res))
                else:
                    print(f"Error: AI response for '{word}' missing fields.")
            else:
                print(f"Error: AI response missing entry for '{word}'.")
        return batch_updates
    except Exception as e:
        print(f"Error parsing JSON batch: {e}\nResponse: {generated_text}")
        return []

def is_useless(fields):
    sentence = fields.get('Sentence', '').strip()

    if not sentence:
        return True

    return False

def check_and_warn_costs(model, num_notes):
    """
    Warns the user about potential costs for cloud models and asks for confirmation.
    """
    if num_notes == 0:
        return True

    is_local = any(provider in model.lower() for provider in ["ollama", "local", "llama_cpp", "llama-cpp"])

    if not is_local:
        print("\n" + "!" * 60)
        print("COST WARNING: You are using a cloud-based model.")
        print(f"You are about to process {num_notes} notes.")
        print("This may incur significant API costs.")
        print("!" * 60 + "\n")

        try:
            choice = input(f"Do you want to continue processing {num_notes} notes? (y/n): ").strip().lower()
            return choice in ["y", "yes"]
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Batched i+1 Augmentation for Japanese::Mining")
    parser.add_argument("--model", default="gemini/gemini-2.5-flash", help="LiteLLM model")
    parser.add_argument("--total-notes", type=int, default=20, help="Total number of notes to process")
    parser.add_argument("--batch-size", type=int, default=5, help="Number of words per prompt")
    args = parser.parse_args()

    # Load prompt template
    if not os.path.exists("i1_prompt_template.txt"):
        print("Error: i1_prompt_template.txt not found.")
        return
    with open("i1_prompt_template.txt", "r", encoding="utf-8") as f:
        prompt_template = f.read()

    # Load learned words
    if not os.path.exists("learned_words.txt"):
        print("Error: learned_words.txt not found. Run extract_learned_vocab.py first.")
        return
    with open("learned_words.txt", "r", encoding="utf-8") as f:
        learned_words = f.read().strip()

    print("Fetching notes from Japanese::Mining...")
    note_ids = invoke_anki("findNotes", query='"deck:Japanese::Mining"')
    if not note_ids:
        print("No notes found.")
        return

    notes_info = invoke_anki("notesInfo", notes=note_ids)

    # Sort all notes by FreqSort immediately
    notes_info.sort(key=lambda x: int(x['fields'].get('FreqSort', {}).get('value', '999999') or '999999'))

    # Filter for useless notes
    notes_to_process = []
    for info in notes_info:
        fields = {k: v['value'] for k, v in info['fields'].items()}
        if is_useless(fields):
            notes_to_process.append({'id': info['noteId'], 'fields': fields})

    # Limit to total-notes
    notes_to_process = notes_to_process[:args.total_notes]

    if not notes_to_process:
        print("No useless notes found to process.")
        return

    print(f"\nWords to be processed ({len(notes_to_process)} total):")
    expressions = [n['fields']['Expression'].strip() for n in notes_to_process]
    print(", ".join(expressions))

    if not check_and_warn_costs(args.model, len(notes_to_process)):
        print("Aborting.")
        return

    print(f"Processing {len(notes_to_process)} notes in batches of {args.batch_size}...")

    llm_client = LiteLLMClient(model=args.model)
    all_updates = []

    batches = [notes_to_process[i:i + args.batch_size] for i in range(0, len(notes_to_process), args.batch_size)]

    # Using max_workers=3 to balance speed and stability
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(process_batch, llm_client, b, prompt_template, learned_words) for b in batches]
        for future in tqdm(as_completed(futures), total=len(batches), desc="Processing batches"):
            all_updates.extend(future.result())

    if all_updates:
        print(f"Updating {len(all_updates)} notes in Anki...")
        for nid, data in tqdm(all_updates, desc="Syncing to Anki"):
            invoke_anki("updateNoteFields", note={
                "id": nid,
                "fields": {
                    "Sentence": data['sentence'],
                    "SentenceEnglish": data['english']
                }
            })
        print("Done!")
    else:
        print("No updates generated.")

if __name__ == "__main__":
    main()
