#!/usr/bin/env python3
"""Tests for restrict_planning_agents.py, run as a subprocess the way Claude Code runs it.

Run with:  python3 -m unittest discover -s hooks/tests   (from the plugin root)
"""
# cspell:ignore SYSTEMROOT
import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(HERE), "restrict_planning_agents.py")

ROOT = "/opt/plugins/cache/bitwarden-testing-tools/1.3.0"
MAPPER = "bitwarden-testing-tools:services-under-test-mapper"
MAPPER_DIR_FORM = (
    "bitwarden-testing-tools:services-under-test-mapper:services-under-test-mapper"
)
SCOPER = "bitwarden-testing-tools:playwright-application-context-scoper"
GATHERER = "bitwarden-testing-tools:playwright-test-context-gatherer"
MAPPER_SKILL = "bitwarden-testing-tools:mapping-services-under-test"
SCOPER_SKILL = "bitwarden-testing-tools:scoping-playwright-application-context"
GATHERER_SKILL = "bitwarden-atlassian-tools:researching-jira-issues"
FORKED_SKILL = "bitwarden-security-engineer:auditing-external-claude-plugins"
SKILL_BLOCK = "skill may be invoked in this agent"


def run_hook(stdin, root=ROOT):
    # SYSTEMROOT is passed through because Python fails to start without it on Windows.
    env = {k: os.environ[k] for k in ("PATH", "SYSTEMROOT") if k in os.environ}
    if root is not None:
        env["CLAUDE_PLUGIN_ROOT"] = root
    data = stdin if isinstance(stdin, bytes) else stdin.encode("utf-8")
    result = subprocess.run(
        [sys.executable, SCRIPT],
        input=data,
        capture_output=True,
        env=env,
        check=False,
    )
    return result.returncode, result.stderr.decode("utf-8", "replace")


def bash(command, agent_type=MAPPER):
    body = {"tool_name": "Bash", "tool_input": {"command": command}}
    if agent_type is not None:
        body["agent_type"] = agent_type
    return json.dumps(body)


def skill(name, agent_type=MAPPER):
    return json.dumps(
        {"tool_name": "Skill", "tool_input": {"skill": name}, "agent_type": agent_type}
    )


class AllowedTest(unittest.TestCase):
    def assertAllowed(self, stdin, root=ROOT):
        code, err = run_hook(stdin, root)
        self.assertEqual(code, 0, err)

    def test_mapper_invokes_its_own_skill(self):
        self.assertAllowed(skill(MAPPER_SKILL))

    def test_scoper_invokes_its_own_skill(self):
        self.assertAllowed(skill(SCOPER_SKILL, SCOPER))

    def test_gatherer_invokes_its_own_skill(self):
        self.assertAllowed(skill(GATHERER_SKILL, GATHERER))

    def test_directory_form_agent_type_invokes_its_own_skill(self):
        self.assertAllowed(skill(MAPPER_SKILL, MAPPER_DIR_FORM))

    def test_own_skill_with_leading_slash_and_spaces(self):
        self.assertAllowed(skill("  /" + MAPPER_SKILL + " "))

    def test_restricted_agent_other_tools_pass(self):
        body = json.dumps(
            {"tool_name": "Read", "tool_input": {"file_path": "/etc/hosts"}, "agent_type": MAPPER}
        )
        self.assertAllowed(body)

    def test_scoper_grep_tool_passes(self):
        body = json.dumps(
            {"tool_name": "Grep", "tool_input": {"pattern": "CohortService"}, "agent_type": SCOPER}
        )
        self.assertAllowed(body)

    def test_gatherer_mcp_tool_passes(self):
        body = json.dumps({
            "tool_name": "mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue",
            "tool_input": {"issue_key": "PM-1"},
            "agent_type": GATHERER,
        })
        self.assertAllowed(body)


class BlockedTest(unittest.TestCase):
    def assertBlocked(self, stdin, root=ROOT, message=SKILL_BLOCK):
        code, err = run_hook(stdin, root)
        self.assertEqual(code, 2)
        self.assertIn(message, err)

    def test_directory_form_agent_type_is_blocked_too(self):
        self.assertBlocked(skill(FORKED_SKILL, MAPPER_DIR_FORM))

    def test_skill_blocks_without_a_plugin_root(self):
        self.assertBlocked(skill(FORKED_SKILL), root=None)

    def test_skill_block_message_says_to_report_an_obstacle(self):
        self.assertBlocked(skill(FORKED_SKILL, SCOPER), message="report this step as an obstacle")

    def test_deeply_nested_input_is_blocked(self):
        # Deep enough to exhaust the JSON parser's recursion on every supported Python.
        nested = "[" * 1000000 + "]" * 1000000
        body = skill(FORKED_SKILL)[:-1] + ', "x": ' + nested + "}"
        self.assertBlocked(body)

    def test_non_utf8_skill_name_is_blocked(self):
        data = skill(FORKED_SKILL).encode("utf-8").replace(b"auditing", b"\xff")
        self.assertBlocked(data)

    def test_foreign_forked_skill_is_blocked(self):
        self.assertBlocked(skill(FORKED_SKILL))

    def test_gatherer_foreign_forked_skill_is_blocked(self):
        self.assertBlocked(skill(FORKED_SKILL, GATHERER))

    def test_other_planning_skill_is_blocked(self):
        self.assertBlocked(skill(SCOPER_SKILL))

    def test_bare_own_skill_name_is_blocked(self):
        self.assertBlocked(skill("mapping-services-under-test"))

    def test_own_skill_name_under_another_plugin_is_blocked(self):
        self.assertBlocked(skill("other-plugin:mapping-services-under-test"))

    def test_missing_skill_name_is_blocked(self):
        body = json.dumps({"tool_name": "Skill", "tool_input": {}, "agent_type": MAPPER})
        self.assertBlocked(body)

    def test_skill_block_message_names_the_allowed_skill(self):
        self.assertBlocked(skill(FORKED_SKILL, GATHERER), message=GATHERER_SKILL)


class PassThroughTest(unittest.TestCase):
    def assertPassesThrough(self, stdin):
        code, err = run_hook(stdin)
        self.assertEqual(code, 0, err)
        self.assertEqual(err, "")

    def test_restricted_agent_bash_is_left_to_the_allowlist(self):
        # The hook's matcher is Skill; an agent's `tools:` allowlist keeps Bash out.
        self.assertPassesThrough(bash("echo hi", SCOPER))

    def test_main_session_has_no_agent_type(self):
        self.assertPassesThrough(bash("echo hi", agent_type=None))

    def test_other_agent_in_this_plugin(self):
        self.assertPassesThrough(bash("echo hi", "bitwarden-testing-tools:playwright-test-runner"))

    def test_other_agent_invokes_any_skill(self):
        self.assertPassesThrough(skill(FORKED_SKILL, "bitwarden-testing-tools:playwright-test-runner"))

    def test_same_agent_name_in_another_plugin(self):
        self.assertPassesThrough(bash("echo hi", "other-plugin:services-under-test-mapper"))

    def test_single_segment_agent_type(self):
        self.assertPassesThrough(bash("echo hi", "services-under-test-mapper"))

    def test_invalid_json(self):
        self.assertPassesThrough("not json")

    def test_non_object_json(self):
        self.assertPassesThrough("[1, 2]")


class FailClosedTest(unittest.TestCase):
    """An unexpected error while deciding blocks a restricted agent, with the right message."""

    def setUp(self):
        spec = importlib.util.spec_from_file_location("restrict_planning_agents", SCRIPT)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

        def boom(_payload, _env):
            raise RuntimeError("unexpected")

        self.module.decide = boom

    def run_main(self, stdin):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = self.module.main(stdin, {"CLAUDE_PLUGIN_ROOT": ROOT})
        return code, err.getvalue()

    def test_skill_call_blocks_with_the_skill_message(self):
        code, err = self.run_main(skill(MAPPER_SKILL))
        self.assertEqual(code, 2)
        self.assertIn(SKILL_BLOCK, err)

    def test_unrestricted_agent_passes(self):
        code, err = self.run_main(bash("echo hi", agent_type=None))
        self.assertEqual((code, err), (0, ""))


class ScriptIsExecutableTest(unittest.TestCase):
    def test_script_has_execute_bit(self):
        self.assertTrue(os.access(SCRIPT, os.X_OK), f"{SCRIPT} must be executable")


if __name__ == "__main__":
    unittest.main()
