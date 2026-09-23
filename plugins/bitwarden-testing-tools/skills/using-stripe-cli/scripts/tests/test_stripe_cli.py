#!/usr/bin/env python3
"""Unit tests for stripe_cli: test-key guard, argv construction, clock advance.

Run with:  python3 -m unittest discover -s scripts/tests   (from the skill dir;
            Python 3.11+, which the config-reading tests need for tomllib)
"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)

import stripe_cli

FIXTURE_CONFIG = '[default]\ntest_mode_api_key = "sk_test_fixture"\n'


def config_env(test, text, **extra):
    """Write text as a Stripe CLI config.toml under a temp XDG_CONFIG_HOME.

    Returns an env that points check_key at it, so no test ever reads the
    developer's real ~/.config/stripe/config.toml.
    """
    root = tempfile.mkdtemp()
    test.addCleanup(__import__("shutil").rmtree, root, True)
    if text is not None:
        os.makedirs(os.path.join(root, "stripe"))
        with open(os.path.join(root, "stripe", "config.toml"), "w") as fh:
            fh.write(text)
    env = {"XDG_CONFIG_HOME": root}
    env.update(extra)
    return env


class CheckKeyTest(unittest.TestCase):
    def assertRefused(self, env, needle=None):
        with self.assertRaises(stripe_cli.GuardError) as cm:
            stripe_cli.check_key(env)
        self.assertEqual(cm.exception.code, stripe_cli.EXIT_KEY)
        if needle:
            self.assertIn(needle, cm.exception.message)
        return cm.exception

    def test_configured_test_key_in_profile_is_returned(self):
        self.assertEqual(
            stripe_cli.check_key(config_env(self, FIXTURE_CONFIG)), "sk_test_fixture"
        )

    def test_test_key_in_environment_is_returned(self):
        env = config_env(self, None, STRIPE_API_KEY="sk_test_abc123")
        self.assertEqual(stripe_cli.check_key(env), "sk_test_abc123")

    def test_restricted_test_key_is_accepted(self):
        env = config_env(self, '[default]\ntest_mode_api_key = "rk_test_abc"\n')
        self.assertEqual(stripe_cli.check_key(env), "rk_test_abc")

    def test_live_secret_key_in_environment_is_refused(self):
        self.assertRefused({"STRIPE_API_KEY": "sk_live_abcdef"}, "LIVE key")

    def test_live_restricted_key_in_environment_is_refused(self):
        self.assertRefused({"STRIPE_API_KEY": "rk_live_abcdef"}, "LIVE key")

    def test_environment_key_takes_precedence_over_the_config(self):
        env = config_env(
            self, '[default]\ntest_mode_api_key = "sk_live_abc"\n',
            STRIPE_API_KEY="sk_test_env",
        )
        self.assertEqual(stripe_cli.check_key(env), "sk_test_env")

    def test_empty_environment_key_counts_as_unset(self):
        env = config_env(self, FIXTURE_CONFIG, STRIPE_API_KEY="")
        self.assertEqual(stripe_cli.check_key(env), "sk_test_fixture")

    def test_live_key_in_test_mode_slot_is_refused(self):
        env = config_env(self, '[default]\ntest_mode_api_key = "sk_live_abc"\n')
        err = self.assertRefused(env, "LIVE key")
        self.assertIn("test_mode_api_key", err.message)

    def test_live_key_in_legacy_secret_key_is_refused(self):
        env = config_env(
            self,
            '[default]\nsecret_key = "sk_live_abc"\ntest_mode_api_key = "sk_test_x"\n',
        )
        self.assertRefused(env, "secret_key")

    def test_live_key_in_legacy_api_key_is_refused(self):
        env = config_env(
            self,
            '[default]\napi_key = "rk_live_abc"\ntest_mode_api_key = "sk_test_x"\n',
        )
        self.assertRefused(env, "api_key")

    def test_present_but_empty_legacy_key_wins_and_leaves_no_key(self):
        env = config_env(
            self, '[default]\nsecret_key = ""\ntest_mode_api_key = "sk_test_x"\n'
        )
        self.assertRefused(env, "no Stripe test-mode key")

    def test_non_test_key_is_refused(self):
        env = config_env(self, '[default]\ntest_mode_api_key = "sk_abc_def"\n')
        self.assertRefused(env, "not a test-mode key")

    def test_missing_config_file_is_refused(self):
        self.assertRefused(config_env(self, None), "no Stripe test-mode key")

    def test_missing_profile_is_refused(self):
        env = config_env(self, '[other]\ntest_mode_api_key = "sk_test_x"\n')
        self.assertRefused(env, "no Stripe test-mode key")

    def test_project_name_environment_selects_the_profile(self):
        env = config_env(
            self,
            '[default]\ntest_mode_api_key = "sk_live_a"\n'
            '[work]\ntest_mode_api_key = "sk_test_work"\n',
            STRIPE_PROJECT_NAME="work",
        )
        self.assertEqual(stripe_cli.check_key(env), "sk_test_work")

    def test_top_level_project_name_selects_the_profile(self):
        env = config_env(
            self,
            'project-name = "work"\n'
            '[default]\ntest_mode_api_key = "sk_test_default"\n'
            '[work]\ntest_mode_api_key = "sk_live_work"\n',
        )
        self.assertRefused(env, "`work` profile")

    def test_project_name_environment_beats_the_top_level_key(self):
        env = config_env(
            self,
            'project-name = "work"\n'
            '[default]\ntest_mode_api_key = "sk_test_default"\n'
            '[work]\ntest_mode_api_key = "sk_live_work"\n',
            STRIPE_PROJECT_NAME="default",
        )
        self.assertEqual(stripe_cli.check_key(env), "sk_test_default")

    def test_empty_project_name_counts_as_unset(self):
        env = config_env(self, FIXTURE_CONFIG, STRIPE_PROJECT_NAME="")
        self.assertEqual(stripe_cli.check_key(env), "sk_test_fixture")

    def test_table_and_field_names_ignore_case(self):
        env = config_env(self, '[DEFAULT]\nTest_Mode_API_Key = "sk_test_upper"\n')
        self.assertEqual(stripe_cli.check_key(env), "sk_test_upper")

    def test_tables_differing_only_by_case_are_refused(self):
        env = config_env(
            self,
            '[default]\ntest_mode_api_key = "sk_test_a"\n'
            '[DEFAULT]\ntest_mode_api_key = "sk_live_b"\n',
        )
        self.assertRefused(env, "differ only by case")

    def test_profiles_table_is_preferred_over_the_flat_table(self):
        env = config_env(
            self,
            '[default]\ntest_mode_api_key = "sk_live_flat"\n'
            '[profiles.default]\ntest_mode_api_key = "sk_test_nested"\n',
        )
        self.assertEqual(stripe_cli.check_key(env), "sk_test_nested")

    def test_empty_xdg_config_home_falls_back_to_home(self):
        home = tempfile.mkdtemp()
        self.addCleanup(__import__("shutil").rmtree, home, True)
        os.makedirs(os.path.join(home, ".config", "stripe"))
        with open(os.path.join(home, ".config", "stripe", "config.toml"), "w") as fh:
            fh.write(FIXTURE_CONFIG)
        env = {"XDG_CONFIG_HOME": "", "HOME": home}
        self.assertEqual(stripe_cli.check_key(env), "sk_test_fixture")

    def test_userprofile_is_used_when_home_is_unset(self):
        home = tempfile.mkdtemp()
        self.addCleanup(__import__("shutil").rmtree, home, True)
        os.makedirs(os.path.join(home, ".config", "stripe"))
        with open(os.path.join(home, ".config", "stripe", "config.toml"), "w") as fh:
            fh.write(FIXTURE_CONFIG)
        self.assertEqual(stripe_cli.check_key({"USERPROFILE": home}), "sk_test_fixture")

    def test_unparseable_config_is_refused(self):
        self.assertRefused(config_env(self, "[default\n"), "could not read")

    def test_unreadable_config_path_is_refused(self):
        root = tempfile.mkdtemp()
        self.addCleanup(__import__("shutil").rmtree, root, True)
        os.makedirs(os.path.join(root, "stripe", "config.toml"))  # a directory
        self.assertRefused({"XDG_CONFIG_HOME": root}, "could not read")

    def test_non_string_key_is_refused(self):
        env = config_env(self, "[default]\ntest_mode_api_key = 42\n")
        self.assertRefused(env, "not a string")

    def test_profile_that_is_not_a_table_is_refused(self):
        self.assertRefused(config_env(self, 'default = "x"\n'), "not a table")

    def test_missing_tomllib_is_refused_with_a_python_hint(self):
        env = config_env(self, FIXTURE_CONFIG)
        with mock.patch.dict(sys.modules, {"tomllib": None}):
            self.assertRefused(env, "Python 3.11+")

    def test_environment_key_needs_no_tomllib(self):
        with mock.patch.dict(sys.modules, {"tomllib": None}):
            self.assertEqual(
                stripe_cli.check_key({"STRIPE_API_KEY": "sk_test_abc"}), "sk_test_abc"
            )


class RunCliPinTest(unittest.TestCase):
    def test_checked_key_is_pinned_in_the_child_environment(self):
        completed = subprocess.CompletedProcess([], 0, stdout="{}", stderr="")
        with mock.patch.object(stripe_cli.subprocess, "run", return_value=completed) as run:
            stripe_cli.run_cli(["stripe", "get", "/v1/customers"], key="sk_test_pin")
        child_env = run.call_args.kwargs["env"]
        self.assertEqual(child_env["STRIPE_API_KEY"], "sk_test_pin")
        self.assertIn("PATH", child_env)


class CheckPathTest(unittest.TestCase):
    def test_v1_path_is_accepted(self):
        stripe_cli.check_path("/v1/customers/cus_123")

    def test_non_v1_path_is_refused(self):
        with self.assertRaises(stripe_cli.GuardError) as cm:
            stripe_cli.check_path("/v2/customers")
        self.assertEqual(cm.exception.code, stripe_cli.EXIT_PATH)

    def test_flag_injection_is_refused(self):
        with self.assertRaises(stripe_cli.GuardError):
            stripe_cli.check_path("/v1/customers --live")

    def test_whitespace_is_refused(self):
        with self.assertRaises(stripe_cli.GuardError):
            stripe_cli.check_path("/v1/cus tomers")  # cspell:ignore tomers


class CheckClockIdTest(unittest.TestCase):
    def test_bare_clock_id_is_accepted(self):
        stripe_cli.check_clock_id("clock_1234567890abcdef")

    def test_path_traversal_shaped_clock_id_is_refused(self):
        with self.assertRaises(stripe_cli.GuardError) as cm:
            stripe_cli.check_clock_id("clock_1/../../customers")
        self.assertEqual(cm.exception.code, stripe_cli.EXIT_PATH)

    def test_flag_shaped_clock_id_is_refused(self):
        with self.assertRaises(stripe_cli.GuardError):
            stripe_cli.check_clock_id("clock_1 --live")

    def test_wrong_prefix_is_refused(self):
        with self.assertRaises(stripe_cli.GuardError):
            stripe_cli.check_clock_id("cus_123")

    def test_empty_clock_id_is_refused(self):
        with self.assertRaises(stripe_cli.GuardError):
            stripe_cli.check_clock_id("")


class BuildArgvTest(unittest.TestCase):
    def test_read_argv_forwards_no_caller_flag(self):
        argv = stripe_cli.build_read_argv("/v1/customers", ["limit=3"])
        self.assertEqual(argv, ["stripe", "get", "/v1/customers", "-d", "limit=3"])
        self.assertNotIn("--live", argv)
        self.assertNotIn("--api-key", argv)

    def test_advance_argv_targets_the_test_helpers_endpoint(self):
        argv = stripe_cli.build_advance_argv("clock_1", 1750000000)
        self.assertEqual(
            argv,
            [
                "stripe", "post",
                "/v1/test_helpers/test_clocks/clock_1/advance",
                "-d", "frozen_time=1750000000",
            ],
        )
        self.assertNotIn("--live", argv)


class AdvanceClockTest(unittest.TestCase):
    def test_advances_one_day_per_step_and_waits_for_ready(self):
        calls = []
        statuses = iter(["advancing", "ready", "advancing", "ready"])

        def run(argv):
            calls.append(argv)
            if argv[1] == "get":
                if "advance" in argv[2]:
                    raise AssertionError("advance must use post")
                return json.dumps({"frozen_time": 1750000000, "status": next(statuses)})
            return json.dumps({"status": "advancing"})

        slept = []
        frozen = stripe_cli.advance_clock("clock_1", 2, run, slept.append)
        posts = [c for c in calls if c[1] == "post"]
        self.assertEqual(len(posts), 2)
        self.assertEqual(posts[0][4], "frozen_time=1750086400")
        self.assertEqual(posts[1][4], "frozen_time=1750172800")
        self.assertEqual(frozen, 1750172800)
        self.assertTrue(slept)

    def test_traversal_shaped_clock_id_never_reaches_the_cli(self):
        calls = []
        with self.assertRaises(stripe_cli.GuardError) as cm:
            stripe_cli.advance_clock(
                "clock_1/../../customers", 1, calls.append, lambda _s: None
            )
        self.assertEqual(cm.exception.code, stripe_cli.EXIT_PATH)
        self.assertEqual(calls, [])

    def test_missing_frozen_time_becomes_a_guard_error(self):
        def run(_argv):
            return json.dumps({"status": "ready"})

        with self.assertRaises(stripe_cli.GuardError) as cm:
            stripe_cli.advance_clock("clock_1", 1, run, lambda _s: None)
        self.assertEqual(cm.exception.code, stripe_cli.EXIT_CLI)
        self.assertIn("frozen_time", cm.exception.message)

    def test_null_frozen_time_becomes_a_guard_error(self):
        def run(_argv):
            return json.dumps({"frozen_time": None, "status": "ready"})

        with self.assertRaises(stripe_cli.GuardError) as cm:
            stripe_cli.advance_clock("clock_1", 1, run, lambda _s: None)
        self.assertEqual(cm.exception.code, stripe_cli.EXIT_CLI)

    def test_error_payload_on_advance_is_not_a_false_success(self):
        # The Stripe CLI returns exit 0 with an {"error": {...}} body on an
        # API-level rejection, so run_cli does not raise. If advance_clock
        # ignores the POST result it will see the clock still 'ready' at its old
        # frozen_time, break the poll immediately, and report a success that
        # never happened. It must detect the error payload and raise instead.
        def run(argv):
            if argv[1] == "post":
                return json.dumps(
                    {"error": {"type": "invalid_request_error",
                               "message": "No such test clock"}}
                )
            return json.dumps({"frozen_time": 1750000000, "status": "ready"})

        with self.assertRaises(stripe_cli.GuardError) as cm:
            stripe_cli.advance_clock("clock_1", 1, run, lambda _s: None)
        self.assertEqual(cm.exception.code, stripe_cli.EXIT_CLI)

    def test_poll_timeout_reports_partial_progress(self):
        # Day 1 goes ready; day 2 never does, so the poll exhausts. The error
        # must say how many days actually completed and the last frozen_time
        # it tried, so an interrupted multi-day advance is diagnosable.
        original_limit = stripe_cli.CLOCK_POLL_LIMIT
        stripe_cli.CLOCK_POLL_LIMIT = 2
        self.addCleanup(setattr, stripe_cli, "CLOCK_POLL_LIMIT", original_limit)
        posts = {"n": 0}

        def run(argv):
            if argv[1] == "post":
                posts["n"] += 1
                return "{}"
            status = "ready" if posts["n"] <= 1 else "advancing"
            return json.dumps({"frozen_time": 1750000000, "status": status})

        with self.assertRaises(stripe_cli.GuardError) as cm:
            stripe_cli.advance_clock("clock_1", 2, run, lambda _s: None)
        self.assertEqual(cm.exception.code, stripe_cli.EXIT_CLI)
        self.assertIn("advanced 1 of 2 day", cm.exception.message)
        self.assertIn("1750172800", cm.exception.message)

    def test_cli_failure_mid_advance_reports_partial_progress(self):
        # A CLI failure on day 2's advance must preserve the original message
        # and append how far the advance got before failing.
        posts = {"n": 0}

        def run(argv):
            if argv[1] == "post":
                posts["n"] += 1
                if posts["n"] == 2:
                    raise stripe_cli.GuardError(
                        stripe_cli.EXIT_CLI, "stripe CLI failed (1): boom"
                    )
                return "{}"
            return json.dumps({"frozen_time": 1750000000, "status": "ready"})

        with self.assertRaises(stripe_cli.GuardError) as cm:
            stripe_cli.advance_clock("clock_1", 3, run, lambda _s: None)
        self.assertEqual(cm.exception.code, stripe_cli.EXIT_CLI)
        self.assertIn("boom", cm.exception.message)
        self.assertIn("advanced 1 of 3 day", cm.exception.message)


class MainGuardOrderingTest(unittest.TestCase):
    """The guards must run before any subprocess is spawned.

    Proving check_key raises in isolation, and that no built argv
    carries --live, does not prove main() checks the key *first*. These
    tests replace run_cli with a recorder and assert it was never called, which
    is the property the module docstring actually sells.
    """

    def setUp(self):
        self.invocations = []
        self.keys = []
        self.env = config_env(self, FIXTURE_CONFIG)
        self._real_run_cli = stripe_cli.run_cli
        stripe_cli.run_cli = self._recorder
        self.addCleanup(setattr, stripe_cli, "run_cli", self._real_run_cli)

    def _recorder(self, argv, key=None):
        self.invocations.append(argv)
        self.keys.append(key)
        return json.dumps({"frozen_time": 1750000000, "status": "ready"})

    def _main(self, argv, env):
        with contextlib.redirect_stderr(io.StringIO()) as err:
            code = stripe_cli.main(argv, env)
        return code, err.getvalue()

    def test_live_key_spawns_no_cli_on_read(self):
        code, err = self._main(
            ["read", "--path", "/v1/customers"], {"STRIPE_API_KEY": "sk_live_abcdef"}
        )
        self.assertEqual(code, stripe_cli.EXIT_KEY)
        self.assertEqual(self.invocations, [])
        self.assertIn("LIVE key", err)

    def test_live_key_in_profile_spawns_no_cli_on_read(self):
        env = config_env(self, '[default]\ntest_mode_api_key = "sk_live_abc"\n')
        code, err = self._main(["read", "--path", "/v1/customers"], env)
        self.assertEqual(code, stripe_cli.EXIT_KEY)
        self.assertEqual(self.invocations, [])
        self.assertIn("LIVE key", err)

    def test_missing_key_spawns_no_cli(self):
        code, _err = self._main(["read", "--path", "/v1/customers"], config_env(self, None))
        self.assertEqual(code, stripe_cli.EXIT_KEY)
        self.assertEqual(self.invocations, [])

    def test_read_passes_the_checked_key_to_the_cli(self):
        with contextlib.redirect_stdout(io.StringIO()):
            code, _err = self._main(["read", "--path", "/v1/customers"], self.env)
        self.assertEqual(code, stripe_cli.EXIT_OK)
        self.assertEqual(self.keys, ["sk_test_fixture"])

    def test_advance_clock_passes_the_checked_key_on_every_call(self):
        with contextlib.redirect_stdout(io.StringIO()):
            code, _err = self._main(
                ["advance-clock", "--clock", "clock_1", "--days", "1"], self.env
            )
        self.assertEqual(code, stripe_cli.EXIT_OK)
        self.assertTrue(self.keys)
        self.assertEqual(set(self.keys), {"sk_test_fixture"})

    def test_live_key_spawns_no_cli_on_advance_clock(self):
        code, _err = self._main(
            ["advance-clock", "--clock", "clock_1", "--days", "8"],
            {"STRIPE_API_KEY": "rk_live_abcdef"},
        )
        self.assertEqual(code, stripe_cli.EXIT_KEY)
        self.assertEqual(self.invocations, [])

    def test_zero_days_is_a_usage_error_and_spawns_no_cli(self):
        code, err = self._main(
            ["advance-clock", "--clock", "clock_1", "--days", "0"], self.env
        )
        self.assertEqual(code, stripe_cli.EXIT_USAGE)
        self.assertEqual(self.invocations, [])
        self.assertIn("--days must be at least 1", err)

    def test_negative_days_is_a_usage_error(self):
        code, _err = self._main(
            ["advance-clock", "--clock", "clock_1", "--days", "-3"], self.env
        )
        self.assertEqual(code, stripe_cli.EXIT_USAGE)
        self.assertEqual(self.invocations, [])

    def test_over_max_days_is_a_usage_error_and_spawns_no_cli(self):
        code, err = self._main(
            [
                "advance-clock", "--clock", "clock_1",
                "--days", str(stripe_cli.MAX_ADVANCE_DAYS + 1),
            ],
            self.env,
        )
        self.assertEqual(code, stripe_cli.EXIT_USAGE)
        self.assertEqual(self.invocations, [])
        self.assertIn("at most", err)

    def test_max_days_is_accepted(self):
        # The cap is an upper *inclusive* bound: exactly MAX_ADVANCE_DAYS runs.
        with contextlib.redirect_stdout(io.StringIO()):
            code, _err = self._main(
                [
                    "advance-clock", "--clock", "clock_1",
                    "--days", str(stripe_cli.MAX_ADVANCE_DAYS),
                ],
                self.env,
            )
        self.assertEqual(code, stripe_cli.EXIT_OK)

    def test_malformed_clock_id_spawns_no_cli(self):
        code, _err = self._main(
            ["advance-clock", "--clock", "clock_1/../../customers", "--days", "1"],
            self.env,
        )
        self.assertEqual(code, stripe_cli.EXIT_PATH)
        self.assertEqual(self.invocations, [])


class ScriptIsExecutableTest(unittest.TestCase):
    def test_script_has_execute_bit(self):
        script_path = os.path.join(SCRIPTS, "stripe_cli.py")
        self.assertTrue(
            os.access(script_path, os.X_OK),
            f"{script_path} must be executable: SKILL.md invokes it by bare "
            "path relying on its shebang, with no python3 prefix",
        )


if __name__ == "__main__":
    unittest.main()
