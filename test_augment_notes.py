import unittest
from unittest.mock import MagicMock, patch, call
import sys
import os

# Ensure we can import the module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from augment_notes import process_deck_ankiconnect, LiteLLMClient, process_content

TEST_PROMPT = "Analyze: {Text}"
TEST_TARGET_FIELD = "Notes"


class TestAugmentNotes(unittest.TestCase):
    def test_process_content_bold_conversion(self):
        """Test that Markdown bold is converted to <b> tags."""
        markdown_input = "This is **bold** text."
        # markdown library wrap it in <p>
        expected_html = "<p>This is <b>bold</b> text.</p>"
        result = process_content(markdown_input)
        self.assertEqual(result, expected_html)

    @patch("augment_notes.litellm")
    def test_litellm_client_generate_success(self, mock_litellm):
        """Test successful generation with LiteLLM."""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "**Bold** response"
        mock_litellm.completion.return_value = mock_response

        client = LiteLLMClient(model="gemini/gemini-1.5-flash")
        result = client.generate("Test prompt")

        self.assertEqual(result, "**Bold** response")
        mock_litellm.completion.assert_called_once_with(
            model="gemini/gemini-1.5-flash",
            messages=[{"role": "user", "content": "Test prompt"}],
        )

    @patch("augment_notes.litellm")
    def test_litellm_client_generate_failure(self, mock_litellm):
        """Test error handling in LiteLLM generation."""
        mock_litellm.completion.side_effect = Exception("API Error")

        client = LiteLLMClient(model="gemini/gemini-1.5-flash")
        result = client.generate("Test prompt")

        self.assertIsNone(result)

    @patch("augment_notes.invoke_anki")
    def test_process_deck_ankiconnect_dry_run(self, mock_invoke_anki):
        """Test AnkiConnect mode dry run."""

        # Mock findNotes
        # query='deck:"Default"'
        # Returns list of IDs
        def side_effect(action, **params):
            if action == "findNotes":
                return [1, 2, 3]
            if action == "notesInfo":
                if params.get("notes") == [1]:
                    # Mock for note type inference
                    return [{"modelName": "Cloze"}]
                return [
                    {
                        "noteId": 1,
                        "fields": {
                            "Text": {"value": "Text1", "order": 0},
                            "Notes": {"value": "", "order": 2},
                            "FreqSort": {"value": "100", "order": 3},
                        },
                        "tags": ["tag1"],
                    },
                    {
                        "noteId": 2,
                        "fields": {
                            "Text": {"value": "Text2", "order": 0},
                            "Notes": {"value": "Existing", "order": 2},
                            "FreqSort": {"value": "200", "order": 3},
                        },
                        "tags": ["tag2"],
                    },
                    {
                        "noteId": 3,
                        "fields": {
                            "Text": {"value": "Text3", "order": 0},
                            "Notes": {"value": "", "order": 2},
                            "FreqSort": {"value": "300", "order": 3},
                        },
                        "tags": ["tag3"],
                    },
                ]
            return None

        mock_invoke_anki.side_effect = side_effect
        mock_llm_client = MagicMock()

        process_deck_ankiconnect(
            "Default", TEST_TARGET_FIELD, TEST_PROMPT, mock_llm_client, dry_run=True
        )

        # Verification
        mock_invoke_anki.assert_any_call("findNotes", query='deck:"Default"')
        # First call to notesInfo is for inference
        mock_invoke_anki.assert_any_call("notesInfo", notes=[1])
        # Second call to notesInfo is for details
        mock_invoke_anki.assert_any_call("notesInfo", notes=[1, 2, 3])

        # Ensure NO updateNoteFields calls happened
        calls = mock_invoke_anki.call_args_list
        update_calls = [c for c in calls if c[0][0] == "updateNoteFields"]
        self.assertEqual(len(update_calls), 0)


if __name__ == "__main__":
    unittest.main()
