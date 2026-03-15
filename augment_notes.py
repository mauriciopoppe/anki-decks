import os
import sys
import markdown
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
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"LiteLLM Error ({self.model}): {e}")
            return None


def check_and_warn_costs(model, num_notes):
    """
    Warns the user about potential costs for cloud models and asks for confirmation.
    """
    if num_notes == 0:
        return True

    api_base = os.environ.get("OPENAI_API_BASE", "") or os.environ.get(
        "OPEN_API_BASE", ""
    )
    is_local = (
        any(
            provider in model.lower()
            for provider in ["ollama", "local", "llama_cpp", "llama-cpp"]
        )
        or "localhost" in api_base.lower()
        or "127.0.0.1" in api_base
    )

    if not is_local:
        print("\n" + "!" * 60)
        print("COST WARNING: You are using a cloud-based model.")
        print(f"You are about to process {num_notes} notes.")
        print("This may incur significant API costs.")
        print("Consider using a local model via Ollama or llama.cpp for large decks.")
        print("!" * 60 + "\n")

        try:
            choice = (
                input(f"Do you want to continue processing {num_notes} notes? (y/n): ")
                .strip()
                .lower()
            )
            return choice in ["y", "yes"]
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return False
    return True


def ask_user_interactive(context, generated_text, target_field):
    """
    Shows the user the original context and the generated text,
    then asks for confirmation (y/n/q).
    Returns: 'y', 'n', or 'q'
    """
    print("\n" + "=" * 40)
    print("REVIEWING NOTE")
    print("-" * 20)
    print("CONTEXT:")
    for key, value in context.items():
        print(f"  {key}: {value}")
    print("-" * 20)
    print(f"PROPOSED CHANGE FOR '{target_field}':")
    print(generated_text)
    print("-" * 20)

    while True:
        try:
            choice = (
                input("Accept change? (y)es / (n)o / (s)kip remaining / (q)uit: ")
                .strip()
                .lower()[:1]
            )
            if choice in ["y", "n", "s", "q"]:
                return choice
        except KeyboardInterrupt:
            print("\nQuit signal received.")
            return "q"
        print("Invalid choice. Please enter 'y', 'n', 's', or 'q'.")


def extract_required_fields(prompt_template):
    """
    Extracts field names required by the prompt (e.g. "{Text}" -> ["Text"]).
    """
    return re.findall(r"\{(\w+)\}", prompt_template)


def process_content(text_content):
    if not text_content:
        return ""
    # Convert Markdown to HTML
    html = markdown.markdown(text_content)
    # Use <b> instead of <strong> for bold
    html = html.replace("<strong>", "<b>").replace("</strong>", "</b>")
    return html


# --- AnkiConnect Integration ---


def invoke_anki(action, **params):
    try:
        request_json = json.dumps({"action": action, "version": 6, "params": params})
        response = requests.post("http://localhost:8765", data=request_json).json()
        if len(response) != 2:
            raise Exception("response has an unexpected number of fields")
        if response["error"] is not None:
            raise Exception(response["error"])
        return response["result"]
    except requests.exceptions.ConnectionError:
        print(
            "Error: Could not connect to AnkiConnect. Is Anki running and AnkiConnect installed?"
        )
        sys.exit(1)
    except Exception as e:
        print(f"AnkiConnect Error: {e}")
        sys.exit(1)


def process_note_live(
    llm_client,
    nid,
    note_fields,
    tags,
    target_field,
    prompt_template,
    required_fields,
    interactive=False,
):
    # note_fields is a dict: { "FieldName": "Value", ... }

    # Check if target is empty
    if note_fields.get(target_field, "").strip():
        return None

    # Build context
    context = {}
    for field in required_fields:
        if field in note_fields:
            context[field] = note_fields[field]
        else:
            return None  # Should have been caught earlier, but safe check

    try:
        filled_prompt = prompt_template.format(**context)
        generated_text = llm_client.generate(filled_prompt)

        if interactive:
            choice = ask_user_interactive(context, generated_text, target_field)
            if choice == "q":
                raise KeyboardInterrupt("User quit during interaction")
            if choice == "s":
                return "skip_remaining"
            if choice == "n":
                return None

        generated_content = process_content(generated_text)

        if generated_content:
            new_tags = list(tags)
            date_tag = datetime.now().strftime("%Y-%m-%d")
            augment_tag = "anki_deck_augment"
            if date_tag not in new_tags:
                new_tags.append(date_tag)
            if augment_tag not in new_tags:
                new_tags.append(augment_tag)
            return (nid, generated_content, new_tags)
    except KeyError as e:
        print(f"Error formatting prompt for note {nid}: Missing field {e}")
        return None

    return None


def process_deck_ankiconnect(
    note_type,
    target_field,
    prompt_template,
    llm_client,
    dry_run=False,
    interactive=False,
    total_notes=None,
    sort_field="FreqSort",
):
    print(f"Querying Anki for Note Type: '{note_type}'...")
    query = f'note:"{note_type}"'
    note_ids = invoke_anki("findNotes", query=query)

    if not note_ids:
        print("No notes found for this query.")
        return

    print(f"Found {len(note_ids)} notes. Fetching details...")

    batch_size = 500
    all_notes = []

    for i in range(0, len(note_ids), batch_size):
        batch = note_ids[i : i + batch_size]
        infos = invoke_anki("notesInfo", notes=batch)
        all_notes.extend(infos)

    # Sort notes immediately after fetching
    print(f"Sorting notes by '{sort_field}'...")
    all_notes.sort(
        key=lambda x: int(
            x["fields"].get(sort_field, {}).get("value", "999999") or "999999"
        )
    )

    notes_to_process = []
    required_fields = extract_required_fields(prompt_template)

    # Check first note to verify fields exist
    if all_notes:
        fields = all_notes[0]["fields"]

        if target_field not in fields:
            print(
                f"Error: Target field '{target_field}' not found in note type '{note_type}'."
            )
            return

        for rf in required_fields:
            if rf not in fields:
                print(
                    f"Error: Required field '{rf}' (from prompt) not found in note type '{note_type}'."
                )
                return

        print(f"Verified fields: Target='{target_field}', Source={required_fields}")

    for info in all_notes:
        # We construct a simple dict { "FieldName": "Value" }
        note_fields = {k: v["value"] for k, v in info["fields"].items()}

        # Filter logic: if target is empty
        if not note_fields.get(target_field, "").strip():
            # We store the whole note_fields because we might need multiple source fields
            notes_to_process.append(
                {
                    "id": info["noteId"],
                    "fields": note_fields,
                    "tags": info["tags"],
                }
            )

    # Limit to total-notes if specified
    if total_notes is not None:
        notes_to_process = notes_to_process[:total_notes]

    print(f"Found {len(notes_to_process)} notes that require augmentation.")

    if dry_run:
        print("\n--- Dry Run: Notes to be updated via AnkiConnect ---")
        for n in notes_to_process:
            # Preview using first required field
            preview_field = required_fields[0] if required_fields else target_field
            preview_text = n["fields"].get(preview_field, "[Missing]")
            display_text = preview_text.replace("\n", " ")[:80]
            print(f"ID: {n['id']} | {preview_field}: {display_text}...")
        print("\nDry run complete. No changes made.")
        return

    if not notes_to_process:
        print("No updates needed.")
        return

    if not check_and_warn_costs(llm_client.model, len(notes_to_process)):
        print("Aborting.")
        return

    updates = []

    if interactive:
        print("Starting interactive processing...")
        try:
            for n in notes_to_process:
                result = process_note_live(
                    llm_client,
                    n["id"],
                    n["fields"],
                    n["tags"],
                    target_field,
                    prompt_template,
                    required_fields,
                    interactive=True,
                )
                if result == "skip_remaining":
                    print("\nSkipping all remaining notes...")
                    break
                if result:
                    updates.append(result)
        except KeyboardInterrupt:
            print("\nInteractive session ended early.")
    else:
        # Worker configuration
        max_workers = (
            1 if "ollama" in llm_client.model or "local" in llm_client.model else 15
        )
        print(f"Starting processing with {max_workers} workers...")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(
                    process_note_live,
                    llm_client,
                    n["id"],
                    n["fields"],
                    n["tags"],
                    target_field,
                    prompt_template,
                    required_fields,
                )
                for n in notes_to_process
            ]

            for future in tqdm(
                as_completed(futures),
                total=len(notes_to_process),
                desc="Augmenting Notes",
            ):
                result = future.result()
                if result:
                    updates.append(result)

    if updates:
        print(f"Updating {len(updates)} notes via AnkiConnect...")
        for nid, new_content, new_tags in tqdm(updates, desc="Sending updates to Anki"):
            invoke_anki(
                "updateNoteFields",
                note={"id": nid, "fields": {target_field: new_content}},
            )
            invoke_anki("addTags", notes=[nid], tags=" ".join(new_tags))
        print("Done!")
    else:
        print("No notes generated.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Augment Anki deck with AI-generated content using AnkiConnect."
    )

    parser.add_argument(
        "--note-type",
        required=True,
        help="Anki Model (Note Type) Name",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Identify and list notes without processing",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Process notes interactively, reviewing each AI-generated response",
    )
    parser.add_argument(
        "--target-field",
        required=True,
        help="The field to fill (e.g. 'Notes', 'Mnemonic')",
    )
    parser.add_argument(
        "--prompt-file",
        required=True,
        help="Path to a text file containing the prompt template. Use {FieldName} for placeholders.",
    )
    parser.add_argument(
        "--total-notes",
        type=int,
        default=None,
        help="Total number of notes to process",
    )
    parser.add_argument(
        "--sort-field",
        default="FreqSort",
        help="Field to sort by (default: FreqSort)",
    )

    # LLM Provider Arguments
    parser.add_argument(
        "--model",
        default="gemini/gemini-2.5-flash",
        help="LiteLLM model identifier (e.g., 'gemini/gemini-3-flash-preview', 'ollama/qwen3:4b'). Default: 'gemini/gemini-2.5-flash'",
    )

    args = parser.parse_args()

    if os.path.exists(args.prompt_file):
        with open(args.prompt_file, "r", encoding="utf-8") as f:
            prompt_template = f.read()
    else:
        print(f"Error: Prompt file '{args.prompt_file}' not found.")
        sys.exit(1)

    llm_client = LiteLLMClient(model=args.model)
    print(f"Using model: {args.model}")

    process_deck_ankiconnect(
        note_type=args.note_type,
        target_field=args.target_field,
        prompt_template=prompt_template,
        llm_client=llm_client,
        dry_run=args.dry_run,
        interactive=args.interactive,
        total_notes=args.total_notes,
        sort_field=args.sort_field,
    )
