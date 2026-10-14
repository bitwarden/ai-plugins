#!/usr/bin/env python3
"""Tests for restrict_execution_agents.py, run as a subprocess the way Claude Code runs it.

Run with:  python3 -m unittest discover -s hooks/tests   (from the plugin root)
"""
# cspell:ignore SYSTEMROOT usersecrets
import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(HERE), "restrict_execution_agents.py")

ROOT = "/opt/plugins/cache/bitwarden-testing-tools/1.5.0"
HEALTH_SCRIPTS = ROOT + "/skills/checking-localhost-web-health/scripts"
RUN_SCRIPTS = ROOT + "/skills/running-playwright-tests/scripts"
CONFIG = ROOT + "/skills/running-playwright-tests/playwright.config.json"
MAILCATCHER_SCRIPT = (
    "/opt/plugins/cache/bitwarden-marketplace/bitwarden-mailcatcher-tools/1.0.0"
    "/skills/reading-mailcatcher-api/scripts/read_mailcatcher.py"
)
STRIPE_SCRIPT = (
    "/opt/plugins/cache/bitwarden-marketplace/bitwarden-stripe-tools/1.0.0"
    "/skills/using-stripe-cli/scripts/stripe_cli.py"
)
SHOT = "/tmp/run/screenshots/setup-login-20261008-1030.png"

CHECKER = "bitwarden-testing-tools:localhost-web-health-checker"
CHECKER_DIR_FORM = "bitwarden-testing-tools:localhost-web-health-checker:localhost-web-health-checker"
RUNNER = "bitwarden-testing-tools:playwright-test-runner"
SCOPER = "bitwarden-testing-tools:playwright-application-context-scoper"
HEALTH_SKILL = "bitwarden-testing-tools:checking-localhost-web-health"
RUN_SKILL = "bitwarden-testing-tools:running-playwright-tests"
MAILCATCHER_SKILL = "bitwarden-mailcatcher-tools:reading-mailcatcher-api"
STRIPE_SKILL = "bitwarden-stripe-tools:using-stripe-cli"

SKILL_BLOCK = "skill(s) may be invoked in this agent"
BASH_BLOCK = "This command is not allowed in this agent"
READ_BLOCK = "Reading secrets files is not allowed in this agent"


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


def read(path, agent_type=CHECKER, cwd=None):
    body = {"tool_name": "Read", "tool_input": {"file_path": path}, "agent_type": agent_type}
    if cwd is not None:
        body["cwd"] = cwd
    return json.dumps(body)


class AssertionsMixin:
    def assertAllowed(self, stdin, root=ROOT):
        code, err = run_hook(stdin, root)
        self.assertEqual(code, 0, err)

    def assertBashBlocked(self, command, agent_type=CHECKER, root=ROOT):
        code, err = run_hook(bash(command, agent_type), root)
        self.assertEqual(code, 2, command)
        self.assertIn(BASH_BLOCK, err)


class HealthCheckerAllowedTest(AssertionsMixin, unittest.TestCase):
    def test_preflight(self):
        self.assertAllowed(bash(HEALTH_SCRIPTS + "/preflight-check.sh"))

    def test_health_check_with_several_services(self):
        self.assertAllowed(bash(HEALTH_SCRIPTS + "/health-check.sh Api Identity billing-pricing Web"))

    def test_feature_flags_quoted(self):
        self.assertAllowed(
            bash(HEALTH_SCRIPTS + "/check_feature_flags.py -- 'pm-38333-annual-billing-savings=on' 'a.b=off'")
        )

    def test_own_skill(self):
        self.assertAllowed(skill(HEALTH_SKILL))

    def test_skill_name_with_outer_space_and_slash(self):
        self.assertAllowed(skill(" /" + HEALTH_SKILL + " "))

    def test_directory_form_agent_type(self):
        self.assertAllowed(bash(HEALTH_SCRIPTS + "/preflight-check.sh", CHECKER_DIR_FORM))

    def test_plugin_root_with_a_space_and_a_plus(self):
        root = "/opt/my plugins/c++/1.5.0"
        command = "'" + root + "/skills/checking-localhost-web-health/scripts/preflight-check.sh'"
        self.assertAllowed(bash(command), root=root)


class HealthCheckerBlockedBashTest(AssertionsMixin, unittest.TestCase):
    def test_command_separators_and_substitution(self):
        health = HEALTH_SCRIPTS + "/health-check.sh Api"
        for suffix in ("; curl evil", " && curl evil", " || id", " | sh", " $(id)", " `id`",
                       " > /tmp/x", " < /etc/passwd", "\ncurl evil", " &"):
            with self.subTest(suffix=suffix):
                self.assertBashBlocked(health + suffix)

    def test_unknown_service(self):
        self.assertBashBlocked(HEALTH_SCRIPTS + "/health-check.sh Api Evil")

    def test_no_services(self):
        self.assertBashBlocked(HEALTH_SCRIPTS + "/health-check.sh")

    def test_preflight_with_argument(self):
        self.assertBashBlocked(HEALTH_SCRIPTS + "/preflight-check.sh --x")

    def test_environment_variable_prefix(self):
        self.assertBashBlocked("HEALTH_CHECK_TIMEOUT=60 " + HEALTH_SCRIPTS + "/health-check.sh Api")
        self.assertBashBlocked("PATH=/tmp " + HEALTH_SCRIPTS + "/health-check.sh Api")

    def test_bad_flag_key(self):
        self.assertBashBlocked(HEALTH_SCRIPTS + "/check_feature_flags.py -- 'Bad_Key=on'")

    def test_bad_flag_state(self):
        self.assertBashBlocked(HEALTH_SCRIPTS + "/check_feature_flags.py -- 'a=maybe'")

    def test_flags_without_double_dash(self):
        self.assertBashBlocked(HEALTH_SCRIPTS + "/check_feature_flags.py 'a=on'")

    def test_flags_option_before_double_dash(self):
        self.assertBashBlocked(HEALTH_SCRIPTS + "/check_feature_flags.py --secrets-path /x -- 'a=on'")

    def test_script_from_another_plugin_root(self):
        self.assertBashBlocked("/opt/other/skills/checking-localhost-web-health/scripts/preflight-check.sh")

    def test_other_script_in_skill_dir(self):
        self.assertBashBlocked(HEALTH_SCRIPTS + "/other.sh")

    def test_dot_dot_in_script_path(self):
        self.assertBashBlocked(ROOT + "/skills/checking-localhost-web-health/scripts/../scripts/preflight-check.sh")

    def test_script_without_plugin_root(self):
        self.assertBashBlocked(HEALTH_SCRIPTS + "/preflight-check.sh", root=None)

    def test_runner_commands(self):
        for command in ("playwright-cli close", RUN_SCRIPTS + "/external_trigger.py http://localhost:4000",
                        MAILCATCHER_SCRIPT + " --recipient a@b.c"):
            with self.subTest(command=command):
                self.assertBashBlocked(command)

    def test_unrelated_commands(self):
        for command in ("bash", "curl https://localhost:8080", "cat server/dev/secrets.json", "ls", " "):
            with self.subTest(command=command):
                self.assertBashBlocked(command)

    def test_non_string_command(self):
        code, err = run_hook(json.dumps({"agent_type": CHECKER, "tool_name": "Bash", "tool_input": {"command": 1}}))
        self.assertEqual(code, 2, err)

    def test_missing_tool_input(self):
        code, err = run_hook(json.dumps({"agent_type": CHECKER, "tool_name": "Bash"}))
        self.assertEqual(code, 2, err)


class RunnerAllowedTest(AssertionsMixin, unittest.TestCase):
    def allowed(self, command):
        with self.subTest(command=command):
            self.assertAllowed(bash(command, RUNNER))

    def test_open_with_the_plugin_config(self):
        self.allowed("playwright-cli open --config=" + CONFIG)

    def test_navigation_to_the_two_local_origins(self):
        for url in ("https://localhost:8080", "https://localhost:8080/vault/login",
                    "'https://localhost:8080/#/login'", "'https://localhost:8080/vault?a=1&b=2'",
                    "http://localhost:62911/login"):
            self.allowed("playwright-cli goto " + url)
            self.allowed("playwright-cli tab-new " + url)

    def test_new_tab_without_a_url(self):
        self.allowed("playwright-cli tab-new")

    def test_interaction_and_inspection(self):
        for command in ("playwright-cli close", "playwright-cli snapshot", "playwright-cli click e15",
                        "playwright-cli fill e5 'user@example.com'", 'playwright-cli type "page.click"',
                        "playwright-cli press Enter", "playwright-cli upload ./document.pdf", "playwright-cli mousewheel 0 -100",
                        "playwright-cli console warning", "playwright-cli cookie-get session_id"):
            self.allowed(command)

    def test_eval_and_run_code_payloads_in_quotes(self):
        for command in ("playwright-cli eval 'document.title'",
                        'playwright-cli eval "el => el.textContent" e5',
                        "playwright-cli run-code 'async page => { await page.click(\"#go\"); }'",
                        'playwright-cli run-code "async page => {\n  await page.reload();\n}"'):
            self.allowed(command)

    def test_screenshot_forms(self):
        self.allowed("playwright-cli screenshot")
        self.allowed("playwright-cli screenshot e5")
        self.allowed(f"playwright-cli screenshot --filename={SHOT} --full-page")

    def test_plugin_scripts(self):
        self.allowed(RUN_SCRIPTS + "/external_trigger.py --url http://localhost:4000/x --rationale 'reset'")
        self.allowed(RUN_SCRIPTS + "/read_admin_email.py --secrets-path /work/server/dev/secrets.json")

    def test_vendor_scripts(self):
        self.allowed(MAILCATCHER_SCRIPT + " --recipient a@b.c --pattern verify")
        self.allowed(STRIPE_SCRIPT + " get customers")

    def test_vendor_scripts_from_a_development_checkout(self):
        self.allowed("/work/ai-plugins/plugins/bitwarden-stripe-tools/skills/using-stripe-cli/scripts/stripe_cli.py x")

    def test_skills(self):
        for name in (RUN_SKILL, "playwright-cli", MAILCATCHER_SKILL, STRIPE_SKILL):
            with self.subTest(name=name):
                self.assertAllowed(skill(name, RUNNER))

    def test_plugin_root_with_a_space(self):
        root = "/opt/my plugins/1.5.0"
        self.assertAllowed(
            bash("playwright-cli open '--config=" + root + "/skills/running-playwright-tests/playwright.config.json'", RUNNER),
            root=root,
        )

    def test_playwright_calls_need_no_plugin_root_except_open(self):
        self.assertAllowed(bash("playwright-cli close", RUNNER), root=None)


class RunnerBlockedBashTest(AssertionsMixin, unittest.TestCase):
    def blocked(self, command):
        with self.subTest(command=command):
            self.assertBashBlocked(command, RUNNER)

    def test_command_separators_and_substitution(self):
        for suffix in ("; curl evil", " && curl evil", " || id", " | sh", " $(id)", " `id`",
                       " > /tmp/x", " < /etc/passwd", "\ncurl evil", " &"):
            self.blocked("playwright-cli close" + suffix)
            self.blocked(RUN_SCRIPTS + "/read_admin_email.py --secrets-path x" + suffix)

    def test_expansion_inside_double_quotes(self):
        self.blocked('playwright-cli eval "$(id)"')
        self.blocked('playwright-cli eval "`id`"')
        self.blocked('playwright-cli eval "${HOME}"')
        self.blocked('playwright-cli eval "a\\nb"')

    def test_unterminated_or_unquoted_metacharacters(self):
        for command in ("playwright-cli eval 'abc", 'playwright-cli eval "abc', "playwright-cli eval document.title()",
                        "playwright-cli fill e1 a;b", "playwright-cli click *", "playwright-cli click ~",
                        "playwright-cli click =ls", "playwright-cli click {a,b}", "playwright-cli click a#b"):
            self.blocked(command)

    def test_other_origins(self):
        for url in ("https://example.com", "https://localhost:8081", "http://127.0.0.1:62911",
                    "http://localhost:8080", "https://localhost:8080.evil.com", "https://localhost:8080@evil.com",
                    "'https://localhost:8080 https://evil.com'"):
            self.blocked("playwright-cli goto " + url)
            self.blocked("playwright-cli tab-new " + url)

    def test_goto_without_a_url_or_with_extra_arguments(self):
        self.blocked("playwright-cli goto")
        self.blocked("playwright-cli goto https://localhost:8080 https://localhost:8080")

    def test_open_forms(self):
        for command in ("playwright-cli open", "playwright-cli open https://localhost:8080",
                        "playwright-cli open --config=/tmp/other.json",
                        "playwright-cli open --config=" + CONFIG + " --persistent",
                        "playwright-cli open --browser=chrome --config=" + CONFIG):
            self.blocked(command)

    def test_open_without_a_plugin_root(self):
        self.assertBashBlocked("playwright-cli open --config=" + CONFIG, RUNNER, root=None)

    def test_subcommands_outside_the_list(self):
        for command in ("playwright-cli state-save x.json", "playwright-cli state-load x.json",
                        "playwright-cli pdf --filename=x.pdf", "playwright-cli route '**/*' --status=404",
                        "playwright-cli tracing-start", "playwright-cli video-start",
                        "playwright-cli cookie-set a b", "playwright-cli delete-data", "playwright-cli kill-all",
                        "playwright-cli close-all", "playwright-cli list", "playwright-cli -s=a close",
                        "playwright-cli --version", "playwright-cli"):
            self.blocked(command)

    def test_arguments_on_no_argument_subcommands(self):
        self.blocked("playwright-cli close all")
        self.blocked("playwright-cli snapshot --filename=/tmp/x.yaml")

    def test_wrong_number_of_eval_arguments(self):
        self.blocked("playwright-cli eval")
        self.blocked("playwright-cli eval a b c")
        self.blocked("playwright-cli run-code")
        self.blocked("playwright-cli run-code a b")

    def test_screenshot_path_shapes(self):
        for path in ("/tmp/run/other/x.png", "/tmp/run/screenshots/x.sh", "/tmp/../screenshots/x.png",
                     "run/screenshots/x.png", "/tmp/run/screenshots/sub/../x.png"):
            self.blocked(f"playwright-cli screenshot --filename={path} --full-page")

    def test_screenshot_with_another_flag(self):
        self.blocked(f"playwright-cli screenshot --filename={SHOT} --full-page --x")

    def test_scripts_from_another_plugin_root(self):
        self.blocked("/opt/other/skills/running-playwright-tests/scripts/external_trigger.py http://localhost:4000")

    def test_other_script_in_the_runner_skill_dir(self):
        self.blocked(RUN_SCRIPTS + "/other.sh")

    def test_plugin_script_without_a_plugin_root(self):
        self.assertBashBlocked(RUN_SCRIPTS + "/external_trigger.py x", RUNNER, root=None)

    def test_vendor_script_shapes(self):
        for path in (MAILCATCHER_SCRIPT.replace("read_mailcatcher", "get_admin_email"),
                     MAILCATCHER_SCRIPT.replace("bitwarden-mailcatcher-tools", "other-tools"),
                     MAILCATCHER_SCRIPT.replace("/1.0.0/", "/../1.0.0/"),
                     "relative/" + STRIPE_SCRIPT, STRIPE_SCRIPT + ".sh", "/tmp/stripe_cli.py"):
            self.blocked(path)

    def test_health_check_scripts(self):
        self.blocked(HEALTH_SCRIPTS + "/preflight-check.sh")

    def test_unrelated_commands(self):
        for command in ("bash", "curl https://localhost:8080", "cat server/dev/secrets.json", "ls", "ls /tmp/*x*", " ", ""):
            self.blocked(command)

    def test_non_string_command(self):
        code, err = run_hook(json.dumps({"agent_type": RUNNER, "tool_name": "Bash", "tool_input": {"command": 1}}))
        self.assertEqual(code, 2, err)


class BlockedSkillTest(unittest.TestCase):
    def assertBlocked(self, name, agent_type):
        code, err = run_hook(skill(name, agent_type))
        self.assertEqual(code, 2, name)
        self.assertIn(SKILL_BLOCK, err)

    def test_health_checker_other_skills(self):
        for name in ("playwright-cli", RUN_SKILL, MAILCATCHER_SKILL, STRIPE_SKILL,
                     "bitwarden-security-engineer:auditing-external-claude-plugins",
                     HEALTH_SKILL + "-x", "checking-localhost-web-health", ""):
            with self.subTest(name=name):
                self.assertBlocked(name, CHECKER)

    def test_runner_other_skills(self):
        for name in (HEALTH_SKILL, "running-playwright-tests", "Playwright-cli", "playwright-cli:extra",
                     "bitwarden-security-engineer:auditing-external-claude-plugins", ""):
            with self.subTest(name=name):
                self.assertBlocked(name, RUNNER)

    def test_block_message_names_the_allowed_skills(self):
        _, err = run_hook(skill("other", RUNNER))
        self.assertIn(RUN_SKILL, err)

    def test_non_string_skill(self):
        for agent_type in (CHECKER, RUNNER):
            code, err = run_hook(json.dumps({"agent_type": agent_type, "tool_name": "Skill", "tool_input": {"skill": 1}}))
            self.assertEqual(code, 2, err)


class ReadTest(unittest.TestCase):
    def assertReadBlocked(self, path, agent_type=CHECKER, cwd=None):
        code, err = run_hook(read(path, agent_type, cwd))
        self.assertEqual(code, 2, path)
        self.assertIn(READ_BLOCK, err)

    def assertReadAllowed(self, path, agent_type=CHECKER, cwd=None):
        code, err = run_hook(read(path, agent_type, cwd))
        self.assertEqual(code, 0, err)

    def test_secrets_files_are_blocked_for_both_agents(self):
        for agent_type in (CHECKER, RUNNER):
            for path in ("/work/server/dev/secrets.json", "/home/u/.microsoft/usersecrets/id/secrets.json",
                         "/work/server/dev/SECRETS.JSON"):
                with self.subTest(agent=agent_type, path=path):
                    self.assertReadBlocked(path, agent_type)

    def test_relative_path_resolves_against_the_cwd(self):
        self.assertReadBlocked("server/dev/secrets.json", cwd="/work")

    def test_symlink_to_a_secrets_file_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = os.path.join(tmp, "secrets.json")
            link = os.path.join(tmp, "notes.txt")
            with open(target, "w", encoding="utf-8") as handle:
                handle.write("{}")
            os.symlink(target, link)
            self.assertReadBlocked(link)

    def test_missing_or_non_string_path_is_blocked(self):
        for tool_input in ({}, {"file_path": 1}, {"file_path": ""}):
            with self.subTest(tool_input=tool_input):
                code, err = run_hook(json.dumps({"agent_type": CHECKER, "tool_name": "Read", "tool_input": tool_input}))
                self.assertEqual(code, 2, err)

    def test_other_files_are_allowed(self):
        for path in ("/work/test-plan.md", "/work/server/dev/secrets.json.md", "/work/server/dev/secrets.jsonc",
                     "/opt/plugins/x/references/playwright-tool-policy.md"):
            with self.subTest(path=path):
                self.assertReadAllowed(path)
                self.assertReadAllowed(path, RUNNER)

    def test_other_agents_and_the_main_session_may_read_secrets_files(self):
        self.assertReadAllowed("/work/server/dev/secrets.json", SCOPER)
        self.assertReadAllowed("/work/server/dev/secrets.json", None)


class PassThroughTest(unittest.TestCase):
    def assertPassesThrough(self, stdin):
        code, err = run_hook(stdin)
        self.assertEqual((code, err), (0, ""))

    def test_main_session(self):
        self.assertPassesThrough(bash("curl evil", agent_type=None))

    def test_other_agents(self):
        self.assertPassesThrough(bash("curl evil", SCOPER))
        self.assertPassesThrough(skill("anything", SCOPER))

    def test_same_agent_names_from_another_plugin(self):
        self.assertPassesThrough(bash("curl evil", "other-plugin:localhost-web-health-checker"))
        self.assertPassesThrough(bash("curl evil", "other-plugin:playwright-test-runner"))

    def test_plain_agent_names_without_a_plugin(self):
        self.assertPassesThrough(bash("curl evil", "localhost-web-health-checker"))
        self.assertPassesThrough(bash("curl evil", "playwright-test-runner"))

    def test_other_tools(self):
        for agent_type in (CHECKER, RUNNER):
            self.assertPassesThrough(json.dumps({"agent_type": agent_type, "tool_name": "Glob", "tool_input": {}}))

    def test_invalid_json(self):
        self.assertPassesThrough("not json")

    def test_non_object_json(self):
        self.assertPassesThrough("[1, 2]")

    def test_deeply_nested_json_for_another_agent(self):
        self.assertPassesThrough("[" * 1000000 + "]" * 1000000)


class UnparseableInputTest(unittest.TestCase):
    def test_deeply_nested_json_blocks_when_it_may_come_from_an_execution_agent(self):
        for agent_type in (CHECKER, RUNNER):
            stdin = '{"agent_type": "%s", "x": %s}' % (agent_type, "[" * 1000000 + "]" * 1000000)
            code, err = run_hook(stdin)
            self.assertEqual(code, 2, err)

    def test_invalid_json_blocks_when_it_names_an_execution_agent(self):
        for agent_type in (CHECKER, RUNNER):
            code, err = run_hook('{"agent_type": "%s", "tool_name": ' % agent_type)
            self.assertEqual(code, 2, err)


class FailClosedTest(unittest.TestCase):
    """An unexpected error while deciding blocks the execution agents only."""

    def setUp(self):
        spec = importlib.util.spec_from_file_location("restrict_execution_agents", SCRIPT)
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

    def test_execution_agents_block(self):
        for agent_type in (CHECKER, RUNNER):
            code, err = self.run_main(bash("playwright-cli close", agent_type))
            self.assertEqual(code, 2)
            self.assertIn(BASH_BLOCK, err)

    def test_other_agent_passes(self):
        code, err = self.run_main(bash("echo hi", SCOPER))
        self.assertEqual((code, err), (0, ""))


class SplitCommandTest(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location("restrict_execution_agents", SCRIPT)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def test_quotes_join_into_one_word(self):
        self.assertEqual(self.module.split_command("a 'b c' \"d e\" f'g'h"), ["a", "b c", "d e", "fgh"])

    def test_empty_quoted_argument_is_a_word(self):
        self.assertEqual(self.module.split_command("a ''"), ["a", ""])

    def test_newline_is_literal_inside_quotes_only(self):
        self.assertEqual(self.module.split_command("a 'b\nc'"), ["a", "b\nc"])
        self.assertIsNone(self.module.split_command("a\nb"))

    def test_nothing_to_split(self):
        self.assertIsNone(self.module.split_command("   "))


class ScriptIsExecutableTest(unittest.TestCase):
    def test_script_has_execute_bit(self):
        self.assertTrue(os.access(SCRIPT, os.X_OK), f"{SCRIPT} must be executable")


if __name__ == "__main__":
    unittest.main()
