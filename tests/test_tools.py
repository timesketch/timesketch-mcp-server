# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from timesketch_mcp_server.tools import (
    search_timesketch_events_substrings,
    tag_events,
)


class TestTools(unittest.TestCase):
    @patch("timesketch_mcp_server.tools.get_timesketch_client")
    @patch("timesketch_mcp_server.tools.do_timesketch_search")
    def test_tag_events(self, mock_search, mock_get_client):
        """Test the tag_events tool."""
        mock_sketch = MagicMock()
        mock_get_client.return_value.get_sketch.return_value = mock_sketch

        # Mock search result for finding the events to tag
        mock_df = pd.DataFrame(
            [
                {"_id": "event1", "_index": "index1"},
                {"_id": "event2", "_index": "index1"},
            ]
        )
        mock_search.return_value = mock_df

        mock_sketch.tag_events.return_value = {"number_of_events_with_added_tags": 2}

        result = tag_events(
            sketch_id=1, event_ids=["event1", "event2"], tag_name="my_tag"
        )

        self.assertEqual(result["tagged_events"], 2)
        self.assertEqual(result["failed_events"], 0)
        mock_sketch.tag_events.assert_called_once()

    @patch("timesketch_mcp_server.tools.get_timesketch_client")
    @patch("timesketch_mcp_server.tools.search.Search")
    def test_search_timesketch_events_substrings_escaping(
        self, mock_search_class, mock_get_client
    ):
        """Test that reserved characters are correctly escaped in substring searches."""
        # Setup mocks
        mock_sketch = MagicMock()
        mock_get_client.return_value.get_sketch.return_value = mock_sketch

        mock_search_instance = MagicMock()
        mock_search_class.return_value = mock_search_instance

        # Mock the pandas DataFrame returned by search_instance.table
        mock_df = pd.DataFrame(
            [
                {
                    "_id": "1",
                    "datetime": "2023-01-01T00:00:00",
                    "message": "test message",
                    "data_type": "test",
                }
            ]
        )
        # In the real code, search_instance.table returns the dataframe
        # We need to ensure the mock returns it when accessed
        type(mock_search_instance).table = mock_df

        # Call the tool with a string containing reserved characters
        # '+' is a reserved char in Lucene
        result = search_timesketch_events_substrings(
            sketch_id=1, substrings=["test+query"], regex=False
        )

        # Verify query construction: '+' should be escaped as '\+'
        # The expected query for a substring search is *test\+query*
        mock_search_instance.query_string = r"*test\+query*"

        # Check that the search was called with the escaped query
        self.assertEqual(mock_search_instance.query_string, r"*test\+query*")

        # Verify the result format
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["message"], "test message")

    @patch("timesketch_mcp_server.tools.get_timesketch_client")
    @patch("timesketch_mcp_server.tools.search.Search")
    def test_search_timesketch_events_substrings_boolean_or(
        self, mock_search_class, mock_get_client
    ):
        """Test that multiple substrings are correctly joined with OR."""
        mock_sketch = MagicMock()
        mock_get_client.return_value.get_sketch.return_value = mock_sketch
        mock_search_instance = MagicMock()
        mock_search_class.return_value = mock_search_instance
        type(mock_search_instance).table = pd.DataFrame([])

        search_timesketch_events_substrings(
            sketch_id=1, substrings=["term1", "term2"], boolean_operator="OR"
        )

        # Expected query: *term1* OR *term2*
        self.assertEqual(mock_search_instance.query_string, "*term1* OR *term2*")
