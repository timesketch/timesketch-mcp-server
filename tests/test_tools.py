import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path so we can import timesketch_mcp_server
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from timesketch_mcp_server import tools


class TestStarEvents(unittest.TestCase):
    @patch("timesketch_mcp_server.tools.get_timesketch_client")
    @patch("timesketch_mcp_server.tools.do_timesketch_search")
    def test_star_events(self, mock_search, mock_get_client):
        # Mock setup
        mock_sketch = MagicMock()
        mock_get_client.return_value.get_sketch.return_value = mock_sketch

        # Mock search results
        mock_events_df = MagicMock()
        mock_events = [{"_id": "event1", "_index": "index1"}]
        mock_events_df.to_dict.return_value = mock_events
        mock_search.return_value = mock_events_df

        # Mock label_events return value
        mock_sketch.label_events.return_value = {"result": "success"}

        # Call the tool function
        result = tools.star_events(sketch_id=1, event_ids=["event1"])

        # Verify
        mock_search.assert_called_with(
            sketch_id=1, query='_id:("event1")', return_fields="_id,_index"
        )
        mock_sketch.label_events.assert_called_with(mock_events, "__ts_star")
        self.assertEqual(result, {"result": "success"})

    def test_star_events_empty(self):
        result = tools.star_events(sketch_id=1, event_ids=[])
        self.assertEqual(result, {"result": "No event IDs provided."})

    @patch("timesketch_mcp_server.tools.get_timesketch_client")
    @patch("timesketch_mcp_server.tools.do_timesketch_search")
    def test_star_events_with_comment(self, mock_search, mock_get_client):
        # Mock setup
        mock_sketch = MagicMock()
        mock_get_client.return_value.get_sketch.return_value = mock_sketch

        # Mock search results
        mock_events_df = MagicMock()
        mock_events = [{"_id": "event1", "_index": "index1"}]
        mock_events_df.to_dict.return_value = mock_events
        mock_search.return_value = mock_events_df

        # Mock label_events return value
        mock_sketch.label_events.return_value = {"result": "success"}

        # Call the tool function with comment
        result = tools.star_events(
            sketch_id=1, event_ids=["event1"], comment="important"
        )

        # Verify
        mock_search.assert_called_with(
            sketch_id=1, query='_id:("event1")', return_fields="_id,_index"
        )
        mock_sketch.comment_event.assert_called_with("event1", "index1", "important")
        mock_sketch.label_events.assert_called_with(mock_events, "__ts_star")
        self.assertEqual(result, {"result": "success"})

    @patch("timesketch_mcp_server.tools.get_timesketch_client")
    @patch("timesketch_mcp_server.tools.do_timesketch_search")
    def test_unstar_events(self, mock_search, mock_get_client):
        # Mock setup
        mock_sketch = MagicMock()
        mock_get_client.return_value.get_sketch.return_value = mock_sketch

        # Mock search results
        mock_events_df = MagicMock()
        mock_events = [{"_id": "event1", "_index": "index1"}]
        mock_events_df.to_dict.return_value = mock_events
        mock_search.return_value = mock_events_df

        # Mock label_events return value
        mock_sketch.label_events.return_value = {"result": "success"}

        # Call the tool function
        result = tools.unstar_events(sketch_id=1, event_ids=["event1"])

        # Verify
        mock_search.assert_called_with(
            sketch_id=1, query='_id:("event1")', return_fields="_id,_index"
        )
        mock_sketch.label_events.assert_called_with(
            mock_events, "__ts_star", remove=True
        )
        self.assertEqual(result, {"result": "success"})

    def test_unstar_events_empty(self):
        result = tools.unstar_events(sketch_id=1, event_ids=[])
        self.assertEqual(result, {"result": "No event IDs provided."})

    def test_tag_events_empty(self):
        result = tools.tag_events(sketch_id=1, event_ids=[], tag_name="tag")
        self.assertEqual(result, [{"result": "No event IDs provided."}])

    def test_comment_events_empty(self):
        result = tools.comment_events(sketch_id=1, event_ids=[], annotation="comment")
        self.assertEqual(result, [{"result": "No event IDs provided."}])

    def test_get_events_by_id_empty(self):
        result = tools.get_events_by_id(sketch_id=1, event_ids=[])
        self.assertEqual(result, [])
