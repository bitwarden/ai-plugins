#!/usr/bin/env python3
"""Unit tests for emit_identity._build_identity_attrs — the pure reduction
from a hook-invocation dict to the bw.identity attrs, including the
agent_type precedence rule (top-level agent_type over tool_input.subagent_type).

Run with:  python3 -m unittest test_emit_identity   (from the hooks/ dir)
      or:  python3 -m pytest test_emit_identity.py
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from emit_identity import _build_identity_attrs


class BuildIdentityAttrsTest(unittest.TestCase):
    def test_subagent_stop_uses_top_level_agent_type(self):
        attrs = _build_identity_attrs({
            "hook_event_name": "SubagentStop",
            "agent_type": "bitwarden-software-engineer",
            "session_id": "session-1",
            "cwd": "/Users/dev/bitwarden/clients",
        })
        self.assertEqual(attrs["bw.agent_type"], "bitwarden-software-engineer")
        self.assertEqual(attrs["bw.skill"], "")
        self.assertEqual(attrs["repo"], "clients")

    def test_task_dispatch_falls_back_to_tool_input_subagent_type(self):
        attrs = _build_identity_attrs({
            "hook_event_name": "PostToolUse",
            "tool_name": "Agent",
            "tool_input": {"subagent_type": "Explore"},
            "session_id": "session-2",
        })
        self.assertEqual(attrs["bw.agent_type"], "Explore")

    def test_top_level_agent_type_wins_over_tool_input_when_both_present(self):
        attrs = _build_identity_attrs({
            "agent_type": "bitwarden-code-reviewer",
            "tool_input": {"subagent_type": "general-purpose"},
        })
        self.assertEqual(attrs["bw.agent_type"], "bitwarden-code-reviewer")

    def test_skill_dispatch(self):
        attrs = _build_identity_attrs({
            "hook_event_name": "PostToolUse",
            "tool_name": "Skill",
            "tool_input": {"skill": "bitwarden-atlassian-tools:researching-jira-issues"},
            "session_id": "session-3",
        })
        self.assertEqual(attrs["bw.skill"], "bitwarden-atlassian-tools:researching-jira-issues")
        self.assertEqual(attrs["bw.agent_type"], "")

    def test_missing_tool_input_does_not_raise(self):
        attrs = _build_identity_attrs({"hook_event_name": "SubagentStop"})
        self.assertEqual(attrs["bw.agent_type"], "")
        self.assertEqual(attrs["bw.skill"], "")

    def test_missing_cwd_gives_empty_repo(self):
        attrs = _build_identity_attrs({})
        self.assertEqual(attrs["repo"], "")

    def test_repo_is_basename_only(self):
        attrs = _build_identity_attrs({"cwd": "/Users/dev/bitwarden/ai-plugins"})
        self.assertEqual(attrs["repo"], "ai-plugins")


if __name__ == "__main__":
    unittest.main()
