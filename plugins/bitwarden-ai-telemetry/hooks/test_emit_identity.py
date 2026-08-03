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

from emit_identity import _build_identity_attrs, _should_emit


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


class SlashExpansionTest(unittest.TestCase):
    """A slash-invoked skill fires no Skill tool call, so UserPromptExpansion's
    command_name is the only carrier of the name."""

    SLASH = {
        "hook_event_name": "UserPromptExpansion",
        "expansion_type": "slash_command",
        "command_name": "bitwarden-delivery-tools:labeling-changes",
        "command_args": "what are the supported labels?",
        "command_source": "plugin",
        "session_id": "session-4",
        "cwd": "/Users/dev/bitwarden/clients",
    }

    def test_slash_expansion_recovers_skill_name(self):
        attrs = _build_identity_attrs(self.SLASH)
        self.assertEqual(attrs["bw.skill"], "bitwarden-delivery-tools:labeling-changes")

    def test_slash_expansion_reports_skill_tool_for_query_parity(self):
        attrs = _build_identity_attrs(self.SLASH)
        self.assertEqual(attrs["bw.tool"], "Skill")

    def test_slash_expansion_preserves_true_origin_in_bw_hook(self):
        attrs = _build_identity_attrs(self.SLASH)
        self.assertEqual(attrs["bw.hook"], "UserPromptExpansion")

    def test_slash_expansion_sets_no_agent_type(self):
        attrs = _build_identity_attrs(self.SLASH)
        self.assertEqual(attrs["bw.agent_type"], "")

    def test_plugin_command_is_recorded_like_a_skill(self):
        # command == skill by design; the two are deliberately not distinguished.
        attrs = _build_identity_attrs({
            **self.SLASH, "command_name": "bitwarden-code-review:code-review-local",
        })
        self.assertEqual(attrs["bw.skill"], "bitwarden-code-review:code-review-local")

    def test_tool_path_still_wins_over_expansion(self):
        attrs = _build_identity_attrs({
            "hook_event_name": "PostToolUse",
            "tool_name": "Skill",
            "tool_input": {"skill": "tool-path:skill"},
            "expansion_type": "slash_command",
            "command_name": "expansion:skill",
        })
        self.assertEqual(attrs["bw.skill"], "tool-path:skill")
        self.assertEqual(attrs["bw.tool"], "Skill")

    def test_non_slash_expansion_yields_no_skill(self):
        attrs = _build_identity_attrs({
            "hook_event_name": "UserPromptExpansion",
            "expansion_type": "not-a-slash-command",
            "command_name": "something-else",
        })
        self.assertEqual(attrs["bw.skill"], "")
        self.assertEqual(attrs["bw.tool"], "")


class ShouldEmitTest(unittest.TestCase):
    def test_slash_expansion_emits(self):
        self.assertTrue(_should_emit(SlashExpansionTest.SLASH))

    def test_non_slash_expansion_is_suppressed(self):
        # Would otherwise write a content-free bw.identity row.
        self.assertFalse(_should_emit({
            "hook_event_name": "UserPromptExpansion",
            "expansion_type": "not-a-slash-command",
            "command_name": "something-else",
        }))

    def test_expansion_without_command_name_is_suppressed(self):
        self.assertFalse(_should_emit({
            "hook_event_name": "UserPromptExpansion",
            "expansion_type": "slash_command",
        }))

    def test_non_expansion_hooks_always_emit(self):
        self.assertTrue(_should_emit({"hook_event_name": "PostToolUse", "tool_name": "Skill"}))
        self.assertTrue(_should_emit({"hook_event_name": "SubagentStop"}))


if __name__ == "__main__":
    unittest.main()
