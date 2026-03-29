import urllib.request
import urllib.error
import json
import argparse
import os

def invoke(action, **params):
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode("utf-8")
    try:
        req = urllib.request.Request("http://localhost:8765", data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            res = json.load(response)
            return res
    except urllib.error.URLError as e:
        return {"error": f"Failed to connect to AnkiConnect: {e}"}

def main():
    parser = argparse.ArgumentParser(description='Backup an Anki deck to an .apkg file.')
    parser.add_argument('deck', help='The name of the deck to backup.')
    parser.add_argument('output', help='The path to the output .apkg file.')
    
    args = parser.parse_args()
    
    deck_name = args.deck
    output_path = os.path.abspath(args.output)
    
    print(f"Backing up deck '{deck_name}' to '{output_path}'...")
    
    result = invoke('exportPackage', deck=deck_name, path=output_path, includeSched=True)
    
    if result.get('error'):
        print(f"Error: {result['error']}")
        exit(1)
    
    if result.get('result') is True:
        print(f"Backup successful: {output_path}")
    else:
        print(f"Backup failed or returned unexpected result: {result.get('result')}")
        exit(1)

if __name__ == "__main__":
    main()