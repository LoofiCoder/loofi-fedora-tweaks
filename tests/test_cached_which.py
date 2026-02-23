"""Tests for services.system.system.cached_which()."""

import sys
import os
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'loofi-fedora-tweaks'))

from services.system.system import cached_which


class TestCachedWhich(unittest.TestCase):
    """Tests for cached_which() utility function."""

    def setUp(self):
        """Clear LRU cache before each test."""
        cached_which.cache_clear()

    def tearDown(self):
        """Clear LRU cache after each test."""
        cached_which.cache_clear()

    @patch('services.system.system.shutil.which')
    def test_returns_path_for_existing_tool(self, mock_which):
        """cached_which returns full path for an installed tool."""
        mock_which.return_value = "/usr/bin/bash"
        result = cached_which("bash")
        self.assertEqual(result, "/usr/bin/bash")
        mock_which.assert_called_once_with("bash")

    @patch('services.system.system.shutil.which')
    def test_returns_none_for_missing_tool(self, mock_which):
        """cached_which returns None for a tool not found in PATH."""
        mock_which.return_value = None
        result = cached_which("nonexistent-tool")
        self.assertIsNone(result)
        mock_which.assert_called_once_with("nonexistent-tool")

    @patch('services.system.system.shutil.which')
    def test_cache_prevents_repeated_lookups(self, mock_which):
        """Repeated calls for the same tool use the cache."""
        mock_which.return_value = "/usr/bin/git"
        cached_which("git")
        cached_which("git")
        cached_which("git")
        mock_which.assert_called_once_with("git")

    @patch('services.system.system.shutil.which')
    def test_different_tools_cached_separately(self, mock_which):
        """Different tool names are cached independently."""
        mock_which.side_effect = lambda t: f"/usr/bin/{t}"
        result_a = cached_which("python3")
        result_b = cached_which("dnf")
        self.assertEqual(result_a, "/usr/bin/python3")
        self.assertEqual(result_b, "/usr/bin/dnf")
        self.assertEqual(mock_which.call_count, 2)

    @patch('services.system.system.shutil.which')
    def test_cache_stats_reflect_hits(self, mock_which):
        """LRU cache stats reflect hits and misses."""
        mock_which.return_value = "/usr/bin/ls"
        cached_which("ls")
        cached_which("ls")
        cached_which("ls")
        info = cached_which.cache_info()
        self.assertEqual(info.misses, 1)
        self.assertEqual(info.hits, 2)

    @patch('services.system.system.shutil.which')
    def test_cache_clear_resets(self, mock_which):
        """cache_clear() forces a fresh lookup on next call."""
        mock_which.return_value = "/usr/bin/vim"
        cached_which("vim")
        cached_which.cache_clear()
        cached_which("vim")
        self.assertEqual(mock_which.call_count, 2)

    @patch('services.system.system.shutil.which')
    def test_none_result_is_also_cached(self, mock_which):
        """None result (tool not found) is also cached."""
        mock_which.return_value = None
        cached_which("missing")
        cached_which("missing")
        mock_which.assert_called_once_with("missing")


if __name__ == "__main__":
    unittest.main()
