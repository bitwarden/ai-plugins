#!/usr/bin/env python3
"""Unit tests for emit_mcp._parse_mcp_tool_name — the pure name-splitting
logic that recovers the real MCP server/tool from the native
`mcp__<server>__<tool>` identifier.

Run with:  python3 -m unittest test_emit_mcp   (from the hooks/ dir)
      or:  python3 -m pytest test_emit_mcp.py
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from emit_mcp import _parse_mcp_tool_name


class ParseMcpToolNameTest(unittest.TestCase):
    def test_simple_server_and_tool(self):
        self.assertEqual(
            _parse_mcp_tool_name("mcp__github__list_issues"),
            ("github", "list_issues"),
        )

    def test_server_with_single_underscores(self):
        self.assertEqual(
            _parse_mcp_tool_name("mcp__bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page"),
            ("bitwarden-atlassian-tools_bitwarden-atlassian", "get_confluence_page"),
        )

    def test_tool_segment_with_extra_separators_is_rejoined(self):
        self.assertEqual(
            _parse_mcp_tool_name("mcp__server__tool__with__extra__parts"),
            ("server", "tool__with__extra__parts"),
        )

    def test_missing_tool_segment(self):
        self.assertEqual(_parse_mcp_tool_name("mcp__server"), ("server", ""))

    def test_missing_server_and_tool(self):
        self.assertEqual(_parse_mcp_tool_name("mcp__"), ("", ""))

    def test_non_mcp_tool_returns_none(self):
        self.assertIsNone(_parse_mcp_tool_name("Bash"))
        self.assertIsNone(_parse_mcp_tool_name("Edit"))

    def test_empty_string_returns_none(self):
        self.assertIsNone(_parse_mcp_tool_name(""))

    def test_none_returns_none(self):
        self.assertIsNone(_parse_mcp_tool_name(None))


if __name__ == "__main__":
    unittest.main()
