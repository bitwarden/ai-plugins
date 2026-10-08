#!/usr/bin/env python3
"""Tests for restrict_health_checker.py, run as a subprocess the way Claude Code runs it.

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
SCRIPT = os.path.join(os.path.dirname(HERE), "restrict_health_checker.py")

ROOT = "/opt/plugins/cache/bitwarden-testing-tools/1.5.0"
SCRIPTS = ROOT + "/skills/checking-localhost-web-health/scripts"
CHECKER = "bitwarden-testing-tools:localhost-web-health-checker"
CHECKER_DIR_FORM = "bitwarden-testing-tools:localhost-web-health-checker:localhost-web-health-checker"
RUNNER = "bitwarden-testing-tools:playwright-test-runner"
HEALTH_SKILL = "bitwarden-testing-tools:checking-localhost-web-health"
SHOT = "/tmp/run/screenshots/render-verify-20261008-1030.png"
SKILL_BLOCK = "Only the checking-localhost-web-health and playwright-cli skills"
BASH_BLOCK = "This command is not allowed in this agent"


def run_hook(stdin, root=ROOT):
    # SYSTEMROOT is passed through because Python fails to start without it on Windows.
    env = {k: os.environ[k] for k in ("PATH", "SYSTEMROOT") if k in os.environ}
    if root is not None:
        env["CLAUDE_PLUGIN_ROOT"] = root
    result = subprocess.run(
        [sys.executable, SCRIPT],
        input=stdin.encode("utf-8"),
        capture_output=True,
        env=env,
        check=False,
    )
    return result.returncode, result.stderr.decode("utf-8", "replace")


def bash(command, agent_type=CHECKER):
    body = {"tool_name": "Bash", "tool_input": {"command": command}}
    if agent_type is not None:
        body["agent_type"] = agent_type
    return json.dumps(body)


def skill(name, agent_type=CHECKER):
    return json.dumps(
        {"tool_name": "Skill", "tool_input": {"skill": name}, "agent_type": agent_type}
    )


class AllowedTest(unittest.TestCase):
    def assertAllowed(self, stdin, root=ROOT):
        code, err = run_hook(stdin, root)
        self.assertEqual(code, 0, err)

    def test_preflight(self):
        self.assertAllowed(bash(SCRIPTS + "/preflight-check.sh"))

    def test_health_check_with_several_services(self):
        self.assertAllowed(bash(SCRIPTS + "/health-check.sh Api Identity billing-pricing Web"))

    def test_health_check_with_timeout_prefix(self):
        self.assertAllowed(bash("HEALTH_CHECK_TIMEOUT=60 " + SCRIPTS + "/health-check.sh Api"))

    def test_feature_flags_quoted(self):
        self.assertAllowed(
            bash(SCRIPTS + "/check_feature_flags.py -- 'pm-38333-annual-billing-savings=on' 'a.b=off'")
        )

    def test_open_web_vault(self):
        self.assertAllowed(bash("playwright-cli open https://localhost:8080"))

    def test_goto_portal(self):
        self.assertAllowed(bash("playwright-cli goto http://localhost:62911"))

    def test_screenshot(self):
        self.assertAllowed(bash(f"playwright-cli screenshot --filename={SHOT} --full-page"))

    def test_close(self):
        self.assertAllowed(bash("playwright-cli close"))

    def test_own_skill(self):
        self.assertAllowed(skill(HEALTH_SKILL))

    def test_playwright_cli_skill(self):
        self.assertAllowed(skill("playwright-cli"))

    def test_skill_name_with_outer_space_and_slash(self):
        self.assertAllowed(skill(" /playwright-cli "))

    def test_directory_form_agent_type(self):
        self.assertAllowed(bash(SCRIPTS + "/preflight-check.sh", CHECKER_DIR_FORM))

    def test_playwright_cli_needs_no_plugin_root(self):
        self.assertAllowed(bash("playwright-cli close"), root=None)


class BlockedBashTest(unittest.TestCase):
    def assertBlocked(self, command, root=ROOT):
        code, err = run_hook(bash(command), root)
        self.assertEqual(code, 2, command)
        self.assertIn(BASH_BLOCK, err)

    def test_command_separators_and_substitution(self):
        health = SCRIPTS + "/health-check.sh Api"
        for suffix in ("; curl evil", " && curl evil", " || id", " | sh", " $(id)", " `id`",
                       " > /tmp/x", " < /etc/passwd", "\ncurl evil", " &"):
            with self.subTest(suffix=suffix):
                self.assertBlocked(health + suffix)

    def test_unknown_service(self):
        self.assertBlocked(SCRIPTS + "/health-check.sh Api Evil")

    def test_no_services(self):
        self.assertBlocked(SCRIPTS + "/health-check.sh")

    def test_preflight_with_argument(self):
        self.assertBlocked(SCRIPTS + "/preflight-check.sh --x")

    def test_timeout_prefix_on_another_script(self):
        self.assertBlocked("HEALTH_CHECK_TIMEOUT=60 " + SCRIPTS + "/preflight-check.sh")

    def test_non_numeric_timeout(self):
        self.assertBlocked("HEALTH_CHECK_TIMEOUT=x " + SCRIPTS + "/health-check.sh Api")

    def test_other_environment_variable(self):
        self.assertBlocked("PATH=/tmp " + SCRIPTS + "/health-check.sh Api")

    def test_bad_flag_key(self):
        self.assertBlocked(SCRIPTS + "/check_feature_flags.py -- 'Bad_Key=on'")

    def test_bad_flag_state(self):
        self.assertBlocked(SCRIPTS + "/check_feature_flags.py -- 'a=maybe'")

    def test_flags_without_double_dash(self):
        self.assertBlocked(SCRIPTS + "/check_feature_flags.py 'a=on'")

    def test_flags_option_before_double_dash(self):
        self.assertBlocked(SCRIPTS + "/check_feature_flags.py --secrets-path /x -- 'a=on'")

    def test_script_from_another_plugin_root(self):
        self.assertBlocked("/opt/other/skills/checking-localhost-web-health/scripts/preflight-check.sh")

    def test_other_script_in_skill_dir(self):
        self.assertBlocked(SCRIPTS + "/other.sh")

    def test_dot_dot_in_script_path(self):
        self.assertBlocked(ROOT + "/skills/checking-localhost-web-health/scripts/../scripts/preflight-check.sh")

    def test_script_without_plugin_root(self):
        self.assertBlocked(SCRIPTS + "/preflight-check.sh", root=None)

    def test_script_with_unsafe_plugin_root(self):
        self.assertBlocked(SCRIPTS + "/preflight-check.sh", root="/opt/x;id")

    def test_other_origin_or_port(self):
        for url in ("https://example.com", "https://localhost:8081", "http://127.0.0.1:62911",
                    "https://localhost:8080/", "http://localhost:8080"):
            with self.subTest(url=url):
                self.assertBlocked("playwright-cli open " + url)

    def test_open_without_url_or_extra_argument(self):
        self.assertBlocked("playwright-cli open")
        self.assertBlocked("playwright-cli open https://localhost:8080 --headed")

    def test_other_subcommands_and_flags(self):
        for command in ("playwright-cli eval document.title", "playwright-cli run-code x",
                        "playwright-cli -s=a close", "playwright-cli close all",
                        "playwright-cli click e1", "playwright-cli"):
            with self.subTest(command=command):
                self.assertBlocked(command)

    def test_screenshot_path_shapes(self):
        for path in ("/tmp/run/screenshots/other.png",
                     "/tmp/run/render-verify-20261008-1030.png",
                     "/tmp/../screenshots/render-verify-20261008-1030.png",
                     "/tmp/run/screenshots/render-verify-2026-1030.png",
                     "run/screenshots/render-verify-20261008-1030.png",
                     "/tmp/run/screenshots/render-verify-20261008-1030.png.sh"):
            with self.subTest(path=path):
                self.assertBlocked(f"playwright-cli screenshot --filename={path} --full-page")

    def test_screenshot_without_full_page_or_with_extra_argument(self):
        self.assertBlocked(f"playwright-cli screenshot --filename={SHOT}")
        self.assertBlocked(f"playwright-cli screenshot --filename={SHOT} --full-page --x")

    def test_unrelated_commands(self):
        for command in ("bash", "curl https://localhost:8080", "cat server/dev/secrets.json", "ls", " "):
            with self.subTest(command=command):
                self.assertBlocked(command)

    def test_non_string_command(self):
        code, err = run_hook(json.dumps({"agent_type": CHECKER, "tool_name": "Bash", "tool_input": {"command": 1}}))
        self.assertEqual(code, 2, err)

    def test_missing_tool_input(self):
        code, err = run_hook(json.dumps({"agent_type": CHECKER, "tool_name": "Bash"}))
        self.assertEqual(code, 2, err)


class BlockedSkillTest(unittest.TestCase):
    def assertBlocked(self, name):
        code, err = run_hook(skill(name))
        self.assertEqual(code, 2, name)
        self.assertIn(SKILL_BLOCK, err)

    def test_other_skills(self):
        for name in ("bitwarden-testing-tools:running-playwright-tests",
                     "bitwarden-security-engineer:auditing-external-claude-plugins",
                     "bitwarden-testing-tools:checking-localhost-web-health-x",
                     "playwright-cli:extra", "Playwright-cli", "checking-localhost-web-health", ""):
            with self.subTest(name=name):
                self.assertBlocked(name)

    def test_non_string_skill(self):
        code, err = run_hook(json.dumps({"agent_type": CHECKER, "tool_name": "Skill", "tool_input": {"skill": 1}}))
        self.assertEqual(code, 2, err)


class PassThroughTest(unittest.TestCase):
    def assertPassesThrough(self, stdin):
        code, err = run_hook(stdin)
        self.assertEqual((code, err), (0, ""))

    def test_main_session(self):
        self.assertPassesThrough(bash("curl evil", agent_type=None))

    def test_other_agents(self):
        self.assertPassesThrough(bash("curl evil", RUNNER))
        self.assertPassesThrough(skill("anything", RUNNER))

    def test_same_agent_name_from_another_plugin(self):
        self.assertPassesThrough(bash("curl evil", "other-plugin:localhost-web-health-checker"))

    def test_plain_agent_name_without_plugin(self):
        self.assertPassesThrough(bash("curl evil", "localhost-web-health-checker"))

    def test_other_tools(self):
        self.assertPassesThrough(json.dumps({"agent_type": CHECKER, "tool_name": "Read", "tool_input": {}}))

    def test_invalid_json(self):
        self.assertPassesThrough("not json")

    def test_non_object_json(self):
        self.assertPassesThrough("[1, 2]")

    def test_deeply_nested_json_for_another_agent(self):
        self.assertPassesThrough("[" * 1000000 + "]" * 1000000)


class DeeplyNestedTest(unittest.TestCase):
    def test_blocks_when_it_may_come_from_the_health_checker(self):
        stdin = '{"agent_type": "%s", "x": %s}' % (CHECKER, "[" * 1000000 + "]" * 1000000)
        code, err = run_hook(stdin)
        self.assertEqual(code, 2, err)


class FailClosedTest(unittest.TestCase):
    """An unexpected error while deciding blocks the health checker only."""

    def setUp(self):
        spec = importlib.util.spec_from_file_location("restrict_health_checker", SCRIPT)
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

    def test_health_checker_blocks(self):
        code, err = self.run_main(bash("playwright-cli close"))
        self.assertEqual(code, 2)
        self.assertIn(BASH_BLOCK, err)

    def test_other_agent_passes(self):
        code, err = self.run_main(bash("echo hi", RUNNER))
        self.assertEqual((code, err), (0, ""))


class ScriptIsExecutableTest(unittest.TestCase):
    def test_script_has_execute_bit(self):
        self.assertTrue(os.access(SCRIPT, os.X_OK), f"{SCRIPT} must be executable")


if __name__ == "__main__":
    unittest.main()
