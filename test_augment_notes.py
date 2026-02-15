import unittest
from unittest.mock import MagicMock, patch, call
import sqlite3
import sys
import os

# Ensure we can import the module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from augment_notes import (
    get_model_id_from_name,
    process_deck_file,
    process_deck_ankiconnect,
    LiteLLMClient,
    process_content
)

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

    def test_get_model_id_from_name_notetypes_table(self):
        """Test resolving ID from 'notetypes' table."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        # Mock fetching from notetypes
        mock_cursor.fetchall.return_value = [
            (123, "Basic"),
            (456, "Cloze"),
            (789, "My Model")
        ]

        result = get_model_id_from_name(mock_conn, "Cloze")
        self.assertEqual(result, 456)
        
        # Verify it tried to query notetypes
        mock_cursor.execute.assert_called_with("SELECT id, name FROM notetypes")

    def test_get_model_id_from_name_not_found(self):
        """Test returning None when model is not found."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        # Mock empty notetypes
        mock_cursor.fetchall.return_value = []
        
        result = get_model_id_from_name(mock_conn, "NonExistent")
        self.assertIsNone(result)

    @patch('augment_notes.litellm')
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
            messages=[{"role": "user", "content": "Test prompt"}]
        )

    @patch('augment_notes.litellm')
    def test_litellm_client_generate_failure(self, mock_litellm):
        """Test error handling in LiteLLM generation."""
        mock_litellm.completion.side_effect = Exception("API Error")

        client = LiteLLMClient(model="gemini/gemini-1.5-flash")
        result = client.generate("Test prompt")

        self.assertIsNone(result)

    @patch('augment_notes.setup_environment')
    @patch('sqlite3.connect')
    @patch('augment_notes.get_model_id_from_name')
    @patch('augment_notes.get_field_map')
    def test_process_deck_file_dry_run(self, mock_get_field_map, mock_get_mid, mock_connect, mock_setup_env):
        """Test file mode dry run."""
        mock_setup_env.return_value = "dummy.db"
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock model ID resolution
        mock_get_mid.return_value = 12345
        
        # Mock field map resolution
        mock_get_field_map.return_value = {"Text": 0, "Notes": 2}

        # Mock notes query
        # ID, Flds, Tags
        mock_cursor.fetchall.return_value = [
            (1, "Text1\x1fExtra\x1f\x1fImage", "tag1"), # Empty Note
            (2, "Text2\x1fExtra\x1fExisting Note\x1fImage", "tag2"), # Filled Note
            (3, "Text3\x1fExtra\x1f\x1fImage", "tag3"), # Empty Note
        ]

        mock_llm_client = MagicMock()

        # Call the function in dry run mode
        process_deck_file(
            "input.apkg", 
            "output.apkg", 
            "Cloze", 
            TEST_TARGET_FIELD, 
            TEST_PROMPT,
            mock_llm_client,
            dry_run=True
        )

        # Verification
        mock_get_mid.assert_called_with(mock_conn, "Cloze")
        mock_get_field_map.assert_called_with(mock_conn, 12345)
        
        # Should query for the resolved ID
        mock_cursor.execute.assert_called_with("SELECT id, flds, tags FROM notes WHERE mid=?", (12345,))
        
        # In dry run, we should NOT see any updates
        mock_cursor.executemany.assert_not_called()
        mock_conn.commit.assert_not_called()
        
        # Should close connection
        mock_conn.close.assert_called_once()

    @patch('augment_notes.invoke_anki')
    def test_process_deck_ankiconnect_dry_run(self, mock_invoke_anki):
        """Test AnkiConnect mode dry run."""
        
        # Mock findNotes
        # query='note:"Cloze"'
        # Returns list of IDs
        def side_effect(action, **params):
            if action == "findNotes":
                return [1, 2, 3]
            if action == "notesInfo":
                return [
                    {
                        "noteId": 1,
                        "fields": {
                            "Text": {"value": "Text1", "order": 0},
                            "Notes": {"value": "", "order": 2}
                        },
                        "tags": ["tag1"]
                    },
                    {
                        "noteId": 2,
                        "fields": {
                            "Text": {"value": "Text2", "order": 0},
                            "Notes": {"value": "Existing", "order": 2}
                        },
                        "tags": ["tag2"]
                    },
                    {
                        "noteId": 3,
                        "fields": {
                            "Text": {"value": "Text3", "order": 0},
                            "Notes": {"value": "", "order": 2}
                        },
                        "tags": ["tag3"]
                    }
                ]
            return None

        mock_invoke_anki.side_effect = side_effect
        mock_llm_client = MagicMock()

        process_deck_ankiconnect(
            "Cloze", 
            TEST_TARGET_FIELD, 
            TEST_PROMPT,
            mock_llm_client,
            dry_run=True
        )

        # Verification
        mock_invoke_anki.assert_any_call("findNotes", query='note:"Cloze"')
        mock_invoke_anki.assert_any_call("notesInfo", notes=[1, 2, 3])
        
        # Ensure NO updateNoteFields calls happened
        calls = mock_invoke_anki.call_args_list
        update_calls = [c for c in calls if c[0][0] == 'updateNoteFields']
        self.assertEqual(len(update_calls), 0)

    @patch('augment_notes.input')
    @patch('augment_notes.LiteLLMClient.generate')
    def test_process_note_file_interactive_accept(self, mock_generate, mock_input):
        """Test interactive mode: user accepts the change."""
        from augment_notes import process_note_file
        
        mock_generate.return_value = "Generated Content"
        mock_input.return_value = "y"
        
        llm_client = LiteLLMClient(model="local")
        field_map = {"Text": 0, "Notes": 1}
        # nid, flds, tags, field_map, target_field, prompt_template, required_fields, interactive
        result = process_note_file(
            llm_client,
            1,
            "Original Text\x1f",
            "tags",
            field_map,
            "Notes",
            "Analyze: {Text}",
            ["Text"],
            interactive=True
        )
        
        # Should return the update tuple
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "Original Text\x1f<p>Generated Content</p>")
        self.assertEqual(result[3], 1)

    @patch('augment_notes.input')
    @patch('augment_notes.LiteLLMClient.generate')
    def test_process_note_file_interactive_skip(self, mock_generate, mock_input):
        """Test interactive mode: user skips the change."""
        from augment_notes import process_note_file
        
        mock_generate.return_value = "Generated Content"
        mock_input.return_value = "n"
        
        llm_client = LiteLLMClient(model="local")
        field_map = {"Text": 0, "Notes": 1}
        result = process_note_file(
            llm_client,
            1,
            "Original Text\x1f",
            "tags",
            field_map,
            "Notes",
            "Analyze: {Text}",
            ["Text"],
            interactive=True
        )
        
        # Should return None (skipped)
        self.assertIsNone(result)

    @patch('augment_notes.input')
    @patch('augment_notes.LiteLLMClient.generate')
    def test_process_note_file_interactive_skip_remaining(self, mock_generate, mock_input):
        """Test interactive mode: user skips remaining notes."""
        from augment_notes import process_note_file
        
        mock_generate.return_value = "Generated Content"
        mock_input.return_value = "s"
        
        llm_client = LiteLLMClient(model="local")
        field_map = {"Text": 0, "Notes": 1}
        result = process_note_file(
            llm_client,
            1,
            "Original Text\x1f",
            "tags",
            field_map,
            "Notes",
            "Analyze: {Text}",
            ["Text"],
            interactive=True
        )
        
        # Should return "skip_remaining"
        self.assertEqual(result, "skip_remaining")

    @patch('augment_notes.input')
    @patch('augment_notes.LiteLLMClient.generate')
    def test_process_note_file_interactive_quit(self, mock_generate, mock_input):
        """Test interactive mode: user quits."""
        from augment_notes import process_note_file
        
        mock_generate.return_value = "Generated Content"
        mock_input.return_value = "q"
        
        llm_client = LiteLLMClient(model="local")
        field_map = {"Text": 0, "Notes": 1}
        
        with self.assertRaises(KeyboardInterrupt):
            process_note_file(
                llm_client,
                1,
                "Original Text\x1f",
                "tags",
                field_map,
                "Notes",
                "Analyze: {Text}",
                ["Text"],
                interactive=True
            )

    @patch('augment_notes.setup_environment')
    @patch('sqlite3.connect')
    @patch('augment_notes.get_model_id_from_name')
    @patch('augment_notes.get_field_map')
    @patch('augment_notes.process_note_file')
    @patch('augment_notes.check_and_warn_costs')
    @patch('shutil.copy')
    @patch('augment_notes.zstd.ZstdCompressor')
    @patch('builtins.open')
    @patch('zipfile.ZipFile')
    def test_process_deck_file_interactive(self, mock_zip, mock_open, mock_zstd, mock_copy, mock_warn, mock_process_note, mock_get_field_map, mock_get_mid, mock_connect, mock_setup_env):
        """Test process_deck_file in interactive mode."""
        mock_warn.return_value = True
        mock_setup_env.return_value = "dummy.db"
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_get_mid.return_value = 12345
        mock_get_field_map.return_value = {"Text": 0, "Notes": 1}
        mock_cursor.fetchall.return_value = [(1, "Text1\x1f", "tags")]
        
        # Mocking process_note_file to return an update
        mock_process_note.return_value = ("Text1\x1fNotes1", "tags", 123, 1)

        process_deck_file(
            "input.apkg", "output.apkg", "Cloze", "Notes", "Prompt",
            MagicMock(), interactive=True
        )

        # Should NOT use ThreadPoolExecutor
        # Should call process_note_file directly
        mock_process_note.assert_called_once()
        self.assertEqual(mock_process_note.call_args[1]['interactive'], True)
        
        # Should update database
        mock_cursor.executemany.assert_called_once()
        mock_conn.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()