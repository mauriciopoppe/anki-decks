import requests
import json
import re

def invoke(action, **params):
    response = requests.post('http://localhost:8765', json={
        'action': action,
        'version': 6,
        'params': params
    })
    return response.json()

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
    query_kaishi = '"deck:Japanese::Kaishi 1.5k" prop:ivl>=1'
    notes_kaishi = invoke('findNotes', query=query_kaishi)['result']
    if notes_kaishi:
        notes_info = invoke('notesInfo', notes=notes_kaishi)['result']
        for note in notes_info:
            word = note['fields'].get('Word', {}).get('value')
            if word:
                cleaned = clean_html(word)
                if cleaned:
                    learned_words.add(cleaned)

    # Query for learned cards in Mining
    query_mining = '"deck:Japanese::Mining" prop:ivl>=1'
    notes_mining = invoke('findNotes', query=query_mining)['result']
    if notes_mining:
        notes_info = invoke('notesInfo', notes=notes_mining)['result']
        for note in notes_info:
            word = note['fields'].get('Expression', {}).get('value')
            if word:
                cleaned = clean_html(word)
                if cleaned:
                    learned_words.add(cleaned)

    return sorted(list(learned_words))

if __name__ == '__main__':
    words = get_learned_words()
    print("\n".join(words))
