#!/usr/bin/env python3
"""Unit tests for stripe_cli: live-mode refusal, argv construction, clock advance.

Run with:  python3 -m unittest discover -s scripts/tests   (from the skill dir)
"""
import contextlib
import io
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)

import stripe_cli


class CheckEnvironmentTest(unittest.TestCase):
    def test_empty_environment_is_fine(self):
        stripe_cli.check_environment({})

    def test_configured_test_key_is_fine(self):
        stripe_cli.check_environment({"STRIPE_API_KEY": "sk_test_abc123"})

    def test_live_secret_key_in_environment_is_refused(self):
        with self.assertRaises(stripe_cli.GuardError) as cm:
            stripe_cli.check_environment({"STRIPE_API_KEY": "sk_live_abcdef"})
        self.assertEqual(cm.exception.code, stripe_cli.EXIT_KEY)

    def test_live_restricted_key_in_environment_is_refused(self):
        with self.assertRaises(stripe_cli.GuardError):
            stripe_cli.check_environment({"STRIPE_API_KEY": "rk_live_abcdef"})


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


class MainGuardOrderingTest(unittest.TestCase):
    """The guards must run before any subprocess is spawned.

    Proving check_environment raises in isolation, and that no built argv
    carries --live, does not prove main() checks the environment *first*. These
    tests replace run_cli with a recorder and assert it was never called, which
    is the property the module docstring actually sells.
    """

    def setUp(self):
        self.invocations = []
        self._real_run_cli = stripe_cli.run_cli
        stripe_cli.run_cli = self._recorder
        self.addCleanup(setattr, stripe_cli, "run_cli", self._real_run_cli)

    def _recorder(self, argv):
        self.invocations.append(argv)
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

    def test_live_key_spawns_no_cli_on_advance_clock(self):
        code, _err = self._main(
            ["advance-clock", "--clock", "clock_1", "--days", "8"],
            {"STRIPE_API_KEY": "rk_live_abcdef"},
        )
        self.assertEqual(code, stripe_cli.EXIT_KEY)
        self.assertEqual(self.invocations, [])

    def test_zero_days_is_a_usage_error_and_spawns_no_cli(self):
        code, err = self._main(
            ["advance-clock", "--clock", "clock_1", "--days", "0"], {}
        )
        self.assertEqual(code, stripe_cli.EXIT_USAGE)
        self.assertEqual(self.invocations, [])
        self.assertIn("--days must be at least 1", err)

    def test_negative_days_is_a_usage_error(self):
        code, _err = self._main(
            ["advance-clock", "--clock", "clock_1", "--days", "-3"], {}
        )
        self.assertEqual(code, stripe_cli.EXIT_USAGE)
        self.assertEqual(self.invocations, [])

    def test_malformed_clock_id_spawns_no_cli(self):
        code, _err = self._main(
            ["advance-clock", "--clock", "clock_1/../../customers", "--days", "1"], {}
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
