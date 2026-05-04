import json
import re
import urllib.request
import urllib.error

def invoke(action, **params):
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode("utf-8")
    try:
        req = urllib.request.Request("http://localhost:8765", data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            res = json.load(response)
            if res.get("error"):
                raise Exception(res["error"])
            return res
    except urllib.error.URLError as e:
        raise Exception(f"Failed to connect to AnkiConnect: {e}")

def clean_html(text):
    if not text:
        return ""
    # Remove HTML tags
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()

def get_learned_words():
    learned_words = set()
    
    # Query for learned cards in Kaishi 1.5k
    # A card is "learned" if its interval is > 0
    query_kaishi = '"deck:Language Japanese::Kaishi 1.5k" prop:ivl>=1'
    res_kaishi = invoke('findNotes', query=query_kaishi)
    notes_kaishi = res_kaishi.get('result', [])
    
    if notes_kaishi:
        res_info = invoke('notesInfo', notes=notes_kaishi)
        notes_info = res_info.get('result', [])
        for note in notes_info:
            word = note['fields'].get('Word', {}).get('value')
            if word:
                cleaned = clean_html(word)
                if cleaned:
                    learned_words.add(cleaned)

    # Query for learned cards in Mining
    query_mining = '"deck:Language Japanese::Mining" prop:ivl>=1'
    res_mining = invoke('findNotes', query=query_mining)
    notes_mining = res_mining.get('result', [])
    
    if notes_mining:
        res_info = invoke('notesInfo', notes=notes_mining)
        notes_info = res_info.get('result', [])
        for note in notes_info:
            word = note['fields'].get('Expression', {}).get('value')
            if word:
                cleaned = clean_html(word)
                if cleaned:
                    learned_words.add(cleaned)

    return sorted(list(learned_words))

if __name__ == '__main__':
    try:
        words = get_learned_words()
        print("\n".join(words))
    except Exception as e:
        print(f"Error: {e}")
