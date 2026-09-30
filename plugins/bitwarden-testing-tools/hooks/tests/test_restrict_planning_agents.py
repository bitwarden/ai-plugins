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
SPACED_ROOT = "/Users/Dev User/.claude/plugins/cache/bitwarden-marketplace/bitwarden-testing-tools/1.3.0"
WINDOWS_ROOT = (
    "C:\\Users\\Dev User\\.claude\\plugins\\cache\\bitwarden-marketplace"
    "\\bitwarden-testing-tools\\1.3.0"
)
MAPPER = "bitwarden-testing-tools:services-under-test-mapper"
MAPPER_DIR_FORM = (
    "bitwarden-testing-tools:services-under-test-mapper:services-under-test-mapper"
)
SCOPER = "bitwarden-testing-tools:playwright-application-context-scoper"
GATHERER = "bitwarden-testing-tools:playwright-test-context-gatherer"
WRITER = "bitwarden-testing-tools:playwright-test-case-writer"
MAPPER_SKILL = "bitwarden-testing-tools:mapping-services-under-test"
SCOPER_SKILL = "bitwarden-testing-tools:scoping-playwright-application-context"
GATHERER_SKILL = "bitwarden-atlassian-tools:researching-jira-issues"
WRITER_SKILL = "bitwarden-testing-tools:writing-playwright-test-cases"
FORKED_SKILL = "bitwarden-security-engineer:auditing-external-claude-plugins"
ALLOWED = ROOT + "/scripts/repo-diff.sh server"
BASH_BLOCK = "Only repo-diff.sh may run through Bash in this agent"
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

    def test_mapper_runs_repo_diff_with_a_bare_path(self):
        self.assertAllowed(bash(ALLOWED))

    def test_directory_form_agent_type_is_recognized_and_allowed(self):
        self.assertAllowed(bash(ALLOWED, MAPPER_DIR_FORM))

    def test_scoper_runs_repo_diff(self):
        self.assertAllowed(bash(ROOT + "/scripts/repo-diff.sh /Users/dev/bitwarden/clients", SCOPER))

    def test_single_quoted_path(self):
        self.assertAllowed(bash(ROOT + "/scripts/repo-diff.sh '/Users/dev/my repos/server'"))

    def test_double_quoted_path(self):
        self.assertAllowed(bash(ROOT + '/scripts/repo-diff.sh "/Users/dev/my repos/server"'))

    def test_double_quoted_script_path_with_a_space_in_the_root(self):
        self.assertAllowed(bash('"' + SPACED_ROOT + '/scripts/repo-diff.sh" server'), SPACED_ROOT)

    def test_single_quoted_script_path_with_a_windows_root(self):
        command = "'" + WINDOWS_ROOT + "/scripts/repo-diff.sh' C:/Users/dev/bitwarden/server"
        self.assertAllowed(bash(command), WINDOWS_ROOT)

    def test_surrounding_whitespace_is_ignored(self):
        self.assertAllowed(bash("  " + ALLOWED + "\n"))

    def test_windows_path_with_forward_slashes(self):
        self.assertAllowed(bash(ROOT + "/scripts/repo-diff.sh C:/Users/dev/bitwarden/server"))

    def test_mapper_invokes_its_own_skill(self):
        self.assertAllowed(skill(MAPPER_SKILL))

    def test_scoper_invokes_its_own_skill(self):
        self.assertAllowed(skill(SCOPER_SKILL, SCOPER))

    def test_gatherer_invokes_its_own_skill(self):
        self.assertAllowed(skill(GATHERER_SKILL, GATHERER))

    def test_writer_invokes_its_own_skill(self):
        self.assertAllowed(skill(WRITER_SKILL, WRITER))

    def test_own_skill_with_leading_slash_and_spaces(self):
        self.assertAllowed(skill("  /" + MAPPER_SKILL + " "))

    def test_restricted_agent_other_tools_pass(self):
        body = json.dumps(
            {"tool_name": "Read", "tool_input": {"file_path": "/etc/hosts"}, "agent_type": MAPPER}
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
    def assertBlocked(self, stdin, root=ROOT, message=BASH_BLOCK):
        code, err = run_hook(stdin, root)
        self.assertEqual(code, 2)
        self.assertIn(message, err)

    def test_unrelated_command(self):
        self.assertBlocked(bash("echo hi"))

    def test_scoper_unrelated_command(self):
        self.assertBlocked(bash("cat ~/.ssh/id_rsa", SCOPER))

    def test_directory_form_agent_type_is_blocked_too(self):
        self.assertBlocked(bash("echo hi", MAPPER_DIR_FORM))

    def test_chained_with_semicolon(self):
        self.assertBlocked(bash(ALLOWED + "; echo x"))

    def test_chained_with_and(self):
        self.assertBlocked(bash(ALLOWED + " && echo x"))

    def test_piped(self):
        self.assertBlocked(bash(ALLOWED + " | cat"))

    def test_redirected(self):
        self.assertBlocked(bash(ALLOWED + " > /tmp/x"))

    def test_command_substitution_in_path(self):
        self.assertBlocked(bash(ROOT + "/scripts/repo-diff.sh $(echo server)"))

    def test_backtick_substitution_in_path(self):
        self.assertBlocked(bash(ROOT + "/scripts/repo-diff.sh `echo server`"))

    def test_expansion_inside_double_quotes(self):
        self.assertBlocked(bash(ROOT + '/scripts/repo-diff.sh "$(echo server)"'))

    def test_second_command_on_a_new_line(self):
        self.assertBlocked(bash(ALLOWED + "\necho x"))

    def test_second_argument(self):
        self.assertBlocked(bash(ALLOWED + " clients"))

    def test_look_alike_root(self):
        self.assertBlocked(bash("/evil/scripts/repo-diff.sh server"))

    def test_root_prefix_trick(self):
        self.assertBlocked(bash(ROOT + "-evil/scripts/repo-diff.sh server"))

    def test_literal_plugin_root_placeholder(self):
        self.assertBlocked(bash("${CLAUDE_PLUGIN_ROOT}/scripts/repo-diff.sh server"))

    def test_unquoted_script_path_with_a_space_in_the_root(self):
        self.assertBlocked(bash(SPACED_ROOT + "/scripts/repo-diff.sh server"), SPACED_ROOT)

    def test_double_quoted_script_path_with_a_windows_root(self):
        self.assertBlocked(bash('"' + WINDOWS_ROOT + '/scripts/repo-diff.sh" server'), WINDOWS_ROOT)

    def test_leading_non_ascii_space_is_blocked(self):
        # bash treats U+00A0 as part of the command word, making it a relative path.
        self.assertBlocked(bash("\u00a0" + ALLOWED))

    def test_leading_carriage_return_is_blocked(self):
        # bash treats CR as part of the command word too.
        self.assertBlocked(bash("\r" + ALLOWED))

    def test_deeply_nested_input_is_blocked(self):
        # Deep enough to exhaust the JSON parser's recursion on every supported Python.
        nested = "[" * 1000000 + "]" * 1000000
        body = bash("echo hi")[:-1] + ', "x": ' + nested + "}"
        self.assertBlocked(body)

    def test_cd_prefix(self):
        self.assertBlocked(bash("cd server && " + ROOT + "/scripts/repo-diff.sh ."))

    def test_unquoted_path_with_a_space(self):
        self.assertBlocked(bash(ROOT + "/scripts/repo-diff.sh /Users/dev/my repos/server"))

    def test_windows_backslash_path(self):
        self.assertBlocked(bash(ROOT + "/scripts/repo-diff.sh C:\\Users\\dev\\bitwarden\\server"))

    def test_environment_assignment_prefix(self):
        self.assertBlocked(bash("GIT_DIR=/tmp " + ALLOWED))

    def test_interpreter_wrapper(self):
        self.assertBlocked(bash("bash " + ALLOWED))

    def test_no_argument(self):
        self.assertBlocked(bash(ROOT + "/scripts/repo-diff.sh"))

    def test_missing_command(self):
        self.assertBlocked(json.dumps({"tool_name": "Bash", "agent_type": MAPPER, "tool_input": {}}))

    def test_missing_plugin_root_fails_closed(self):
        self.assertBlocked(bash(ALLOWED), root=None)

    def test_non_utf8_command_is_blocked(self):
        data = bash("echo x").encode("utf-8").replace(b"echo x", b"echo \xff")
        self.assertBlocked(data)

    def test_gatherer_bash_is_blocked(self):
        self.assertBlocked(bash("echo hi", GATHERER))

    def test_writer_bash_is_blocked(self):
        self.assertBlocked(bash("echo hi", WRITER))

    def test_writer_foreign_forked_skill_is_blocked(self):
        self.assertBlocked(skill(FORKED_SKILL, WRITER), message=SKILL_BLOCK)

    def test_foreign_forked_skill_is_blocked(self):
        self.assertBlocked(skill(FORKED_SKILL), message=SKILL_BLOCK)

    def test_gatherer_foreign_forked_skill_is_blocked(self):
        self.assertBlocked(skill(FORKED_SKILL, GATHERER), message=SKILL_BLOCK)

    def test_other_planning_skill_is_blocked(self):
        self.assertBlocked(skill(SCOPER_SKILL), message=SKILL_BLOCK)

    def test_bare_own_skill_name_is_blocked(self):
        self.assertBlocked(skill("mapping-services-under-test"), message=SKILL_BLOCK)

    def test_own_skill_name_under_another_plugin_is_blocked(self):
        self.assertBlocked(skill("other-plugin:mapping-services-under-test"), message=SKILL_BLOCK)

    def test_missing_skill_name_is_blocked(self):
        body = json.dumps({"tool_name": "Skill", "tool_input": {}, "agent_type": MAPPER})
        self.assertBlocked(body, message=SKILL_BLOCK)

    def test_skill_block_message_names_the_allowed_skill(self):
        self.assertBlocked(skill(FORKED_SKILL, GATHERER), message=GATHERER_SKILL)


class PassThroughTest(unittest.TestCase):
    def assertPassesThrough(self, stdin):
        code, err = run_hook(stdin)
        self.assertEqual(code, 0, err)
        self.assertEqual(err, "")

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

    def test_bash_call_blocks_with_the_bash_message(self):
        code, err = self.run_main(bash(ALLOWED))
        self.assertEqual(code, 2)
        self.assertIn(BASH_BLOCK, err)

    def test_unrestricted_agent_passes(self):
        code, err = self.run_main(bash("echo hi", agent_type=None))
        self.assertEqual((code, err), (0, ""))


class ScriptIsExecutableTest(unittest.TestCase):
    def test_script_has_execute_bit(self):
        self.assertTrue(os.access(SCRIPT, os.X_OK), f"{SCRIPT} must be executable")


if __name__ == "__main__":
    unittest.main()
