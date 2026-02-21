import unittest
from unittest.mock import MagicMock, patch

# This import should fail if add_event is not implemented
from src.timesketch_mcp_server.tools import add_event

class TestAddEvent(unittest.TestCase):

    @patch('src.timesketch_mcp_server.tools.get_timesketch_client')
    def test_add_event_success(self, mock_get_client):
        # Setup mocks
        mock_sketch = MagicMock()
        # Mock add_event return value
        mock_sketch.add_event.return_value = "Event added"
        mock_client = MagicMock()
        mock_client.get_sketch.return_value = mock_sketch
        mock_get_client.return_value = mock_client

        sketch_id = 1
        message = "Test Event"
        date = "2023-10-26T12:00:00+00:00"
        timestamp_desc = "Test Timestamp"
        attributes = "key1=value1,key2=value2"

        # Call the function
        result = add_event(sketch_id, message, date, timestamp_desc, attributes)

        # Verify result structure
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"], "Event added")

        # Verify add_event was called with correct arguments
        expected_attributes = {"key1": "value1", "key2": "value2"}
        mock_sketch.add_event.assert_called_with(
            message=message,
            date=date,
            timestamp_desc=timestamp_desc,
            attributes=expected_attributes
        )

    @patch('src.timesketch_mcp_server.tools.get_timesketch_client')
    def test_add_event_no_attributes(self, mock_get_client):
        # Setup mocks
        mock_sketch = MagicMock()
        mock_sketch.add_event.return_value = "Event added"
        mock_client = MagicMock()
        mock_client.get_sketch.return_value = mock_sketch
        mock_get_client.return_value = mock_client

        sketch_id = 1
        message = "Test Event No Attr"
        date = "2023-10-26T12:00:00+00:00"
        timestamp_desc = "Test Timestamp"

        # Call the function with empty attributes
        result = add_event(sketch_id, message, date, timestamp_desc)

        # Verify add_event was called with empty attributes dict
        mock_sketch.add_event.assert_called_with(
            message=message,
            date=date,
            timestamp_desc=timestamp_desc,
            attributes={}
        )
        self.assertEqual(result["status"], "success")

    @patch('src.timesketch_mcp_server.tools.get_timesketch_client')
    def test_add_event_error(self, mock_get_client):
        # Setup mocks to raise an exception
        mock_sketch = MagicMock()
        def side_effect(**kwargs):
            raise ValueError("Invalid date format")
        mock_sketch.add_event.side_effect = side_effect

        mock_client = MagicMock()
        mock_client.get_sketch.return_value = mock_sketch
        mock_get_client.return_value = mock_client

        sketch_id = 1
        message = "Test Event Error"
        date = "invalid-date"
        timestamp_desc = "Test Timestamp"

        # Call the function
        result = add_event(sketch_id, message, date, timestamp_desc)

        # Verify error message is returned
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"], "Invalid date format")

    @patch('src.timesketch_mcp_server.tools.get_timesketch_client')
    def test_add_event_sketch_not_found(self, mock_get_client):
        # Setup mocks
        mock_client = MagicMock()
        mock_client.get_sketch.return_value = None
        mock_get_client.return_value = mock_client

        sketch_id = 999
        message = "Test Event"
        date = "2023-10-26T12:00:00+00:00"
        timestamp_desc = "Test Timestamp"

        # Call the function
        result = add_event(sketch_id, message, date, timestamp_desc)

        # Verify error message is returned
        self.assertEqual(result["status"], "error")
        self.assertIn("Sketch with ID 999 not found", result["error"])

if __name__ == '__main__':
    unittest.main()
