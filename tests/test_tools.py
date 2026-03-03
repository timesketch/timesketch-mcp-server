import unittest
from unittest.mock import MagicMock, patch

# This import should fail if add_event is not implemented
from timesketch_mcp_server.tools import add_event, DEFAULT_SOURCE_SHORT


class TestAddEvent(unittest.TestCase):
    def setUp(self):
        self.patcher = patch("timesketch_mcp_server.tools.get_timesketch_client")
        self.mock_get_client = self.patcher.start()

        self.mock_sketch = MagicMock()
        self.mock_sketch.add_event.return_value = "Event added"

        self.mock_client = MagicMock()
        self.mock_client.get_sketch.return_value = self.mock_sketch

        self.mock_get_client.return_value = self.mock_client

    def tearDown(self):
        self.patcher.stop()

    def test_add_event_success(self):
        # Call the function
        result = add_event.fn(
            1,
            "Test Event",
            "2023-10-26T12:00:00+00:00",
            "Test Timestamp",
            {"key1": "value1", "key2": "value2"},
        )

        # Verify result structure
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"], "Event added")

        # Verify add_event was called with correct arguments
        # Check that source_short is added
        expected_attributes = {
            "key1": "value1",
            "key2": "value2",
            "source_short": DEFAULT_SOURCE_SHORT,
        }
        self.mock_sketch.add_event.assert_called_with(
            message="Test Event",
            date="2023-10-26T12:00:00+00:00",
            timestamp_desc="Test Timestamp",
            attributes=expected_attributes,
        )

    def test_add_event_no_attributes(self):
        # Call the function with default attributes (None)
        result = add_event.fn(
            1, "Test Event No Attr", "2023-10-26T12:00:00+00:00", "Test Timestamp"
        )

        # Verify add_event was called with attributes containing source_short
        self.mock_sketch.add_event.assert_called_with(
            message="Test Event No Attr",
            date="2023-10-26T12:00:00+00:00",
            timestamp_desc="Test Timestamp",
            attributes={"source_short": DEFAULT_SOURCE_SHORT},
        )
        self.assertEqual(result["status"], "success")

    def test_add_event_with_source_short(self):
        # Call the function
        result = add_event.fn(
            1,
            "Test Event Custom Source",
            "2023-10-26T12:00:00+00:00",
            "Test Timestamp",
            {"source_short": "CustomSource"},
        )

        # Verify source_short is NOT overwritten
        self.mock_sketch.add_event.assert_called_with(
            message="Test Event Custom Source",
            date="2023-10-26T12:00:00+00:00",
            timestamp_desc="Test Timestamp",
            attributes={"source_short": "CustomSource"},
        )
        self.assertEqual(result["status"], "success")

    def test_add_event_error(self):
        # Setup mocks to raise an exception
        def side_effect(**kwargs):
            raise ValueError("Invalid date format")

        self.mock_sketch.add_event.side_effect = side_effect

        # Call the function
        result = add_event.fn(1, "Test Event Error", "invalid-date", "Test Timestamp")

        # Verify error message is returned
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"], "Invalid date format")

    def test_add_event_sketch_not_found(self):
        # Setup mocks
        self.mock_client.get_sketch.return_value = None

        # Call the function
        result = add_event.fn(
            999, "Test Event", "2023-10-26T12:00:00+00:00", "Test Timestamp"
        )

        # Verify error message is returned
        self.assertEqual(result["status"], "error")
        self.assertIn("Sketch with ID 999 not found", result["error"])


if __name__ == "__main__":
    unittest.main()
