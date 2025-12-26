import unittest
from unittest.mock import MagicMock, patch
import json
import sqlite3
import sys
import os

# Ensure we can import the module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from augment_deck import get_model_id_from_name, generate_notes

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

if __name__ == '__main__':
    unittest.main()
