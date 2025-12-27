import unittest
from unittest.mock import MagicMock, patch, call
import sqlite3
import sys
import os

# Ensure we can import the module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from augment_deck import (
    get_model_id_from_name,
    generate_notes,
    process_deck_file,
    process_deck_ankiconnect,
)

class TestAugmentDeck(unittest.TestCase):

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

    def test_generate_notes_success(self):
        """Test successful note generation and formatting."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        
        # Mock the API response text
        mock_response.text = "**Bold** explanation."
        mock_client.models.generate_content.return_value = mock_response

        text = "Bonjour"
        result = generate_notes(mock_client, text)

        # Check if markdown was converted to HTML
        self.assertIn("<strong>Bold</strong>", result)
        self.assertIn("explanation", result)
        
        # Verify API call arguments
        mock_client.models.generate_content.assert_called_once()
        call_args = mock_client.models.generate_content.call_args
        self.assertEqual(call_args.kwargs['model'], 'gemini-3-flash-preview')
        self.assertIn(text, call_args.kwargs['contents'])

    def test_generate_notes_failure(self):
        """Test error handling during generation."""
        mock_client = MagicMock()
        
        # Simulate an exception
        mock_client.models.generate_content.side_effect = Exception("API Error")

        result = generate_notes(mock_client, "Test")
        self.assertEqual(result, "")

    @patch('augment_deck.setup_environment')
    @patch('sqlite3.connect')
    @patch('augment_deck.get_model_id_from_name')
    def test_process_deck_file_dry_run(self, mock_get_mid, mock_connect, mock_setup_env):
        """Test file mode dry run."""
        mock_setup_env.return_value = "dummy.db"
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock model ID resolution
        mock_get_mid.return_value = 12345

        # Mock notes query
        # ID, Flds
        mock_cursor.fetchall.return_value = [
            (1, "Text1\x1fExtra\x1f\x1fImage"), # Empty Note
            (2, "Text2\x1fExtra\x1fExisting Note\x1fImage"), # Filled Note
            (3, "Text3\x1fExtra\x1f\x1fImage"), # Empty Note
        ]

        # Call the function in dry run mode
        process_deck_file("input.apkg", "output.apkg", "Cloze", dry_run=True)

        # Verification
        mock_get_mid.assert_called_with(mock_conn, "Cloze")
        # Should query for the resolved ID
        mock_cursor.execute.assert_called_with("SELECT id, flds FROM notes WHERE mid=?", (12345,))
        
        # In dry run, we should NOT see any updates
        mock_cursor.executemany.assert_not_called()
        mock_conn.commit.assert_not_called()
        
        # Should close connection
        mock_conn.close.assert_called_once()

    @patch('augment_deck.invoke_anki')
    @patch('augment_deck.setup_gemini') 
    def test_process_deck_ankiconnect_dry_run(self, mock_setup_gemini, mock_invoke_anki):
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
                        }
                    },
                    {
                        "noteId": 2,
                        "fields": {
                            "Text": {"value": "Text2", "order": 0},
                            "Notes": {"value": "Existing", "order": 2}
                        }
                    },
                    {
                        "noteId": 3,
                        "fields": {
                            "Text": {"value": "Text3", "order": 0},
                            "Notes": {"value": "", "order": 2}
                        }
                    }
                ]
            return None

        mock_invoke_anki.side_effect = side_effect

        process_deck_ankiconnect("Cloze", dry_run=True)

        # Verification
        mock_invoke_anki.assert_any_call("findNotes", query='note:"Cloze"')
        mock_invoke_anki.assert_any_call("notesInfo", notes=[1, 2, 3])
        
        # Ensure NO updateNoteFields calls happened
        calls = mock_invoke_anki.call_args_list
        update_calls = [c for c in calls if c[0][0] == 'updateNoteFields']
        self.assertEqual(len(update_calls), 0)
        
        # Gemini should not be setup in dry run if we skip processing
        # Wait, current logic sets up gemini only if needed?
        # Actually in the code:
        # if dry_run: ... return
        # So setup_gemini() should NOT be called.
        mock_setup_gemini.assert_not_called()

if __name__ == '__main__':
    unittest.main()