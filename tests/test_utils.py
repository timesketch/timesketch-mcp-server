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
from unittest.mock import patch
from timesketch_mcp_server.utils import get_timesketch_client


class TestUtils(unittest.TestCase):
    def setUp(self):
        # Clear the cache before each test to ensure isolation
        get_timesketch_client.cache_clear()

    @patch.dict(
        "os.environ",
        {
            "TIMESKETCH_HOST": "test-host",
            "TIMESKETCH_PORT": "8080",
            "TIMESKETCH_USER": "test-user",
            "TIMESKETCH_PASSWORD": "test-password",
        },
    )
    @patch("timesketch_mcp_server.utils.TimesketchApi")
    def test_get_timesketch_client_initialization(self, mock_api):
        """Test that the client is initialized with environment variables."""
        get_timesketch_client()

        mock_api.assert_called_once_with(
            host_uri="http://test-host:8080/",
            username="test-user",
            password="test-password",
        )

    @patch.dict(
        "os.environ",
        {
            "TIMESKETCH_HOST": "test-host",
            "TIMESKETCH_PORT": "8080",
            "TIMESKETCH_USER": "test-user",
            "TIMESKETCH_PASSWORD": "test-password",
        },
    )
    @patch("timesketch_mcp_server.utils.TimesketchApi")
    def test_get_timesketch_client_caching(self, mock_api):
        """Test that the client instance is cached."""
        client1 = get_timesketch_client()
        client2 = get_timesketch_client()

        # The constructor should only be called once
        mock_api.assert_called_once()
        # Both calls should return the exact same object
        self.assertIs(client1, client2)
