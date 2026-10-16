#!/usr/bin/env python3
"""Unit tests for open_pause_link: only a Stripe test-mode subscription page is ever opened.

The platform, opener lookup, and process launch are injected, so no test opens
anything or depends on the machine it runs on.

Run with:  python3 -m unittest discover -s scripts/tests   (from the skill dir)
"""
import contextlib
import io
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
SKILL = os.path.dirname(SCRIPTS)
sys.path.insert(0, SCRIPTS)

import open_pause_link

LINK = "https://dashboard.stripe.com/test/subscriptions/sub_1234"


class OpenPauseLinkTest(unittest.TestCase):
    def setUp(self):
        self.calls = []

    def fake_run(self, returncode=0):
        def run(args, **_kwargs):
            self.calls.append(args)
            return subprocess.CompletedProcess(args, returncode)

        return run

    def main(self, argv, platform="darwin", which=None, run=None):
        which = which or (lambda name: f"/usr/bin/{name}")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = open_pause_link.main(
                argv, platform=platform, which=which, run=run or self.fake_run()
            )
        return code, out.getvalue(), err.getvalue()

    def assert_refused(self, argv):
        code, _out, err = self.main(argv)
        self.assertEqual(code, open_pause_link.EXIT_REFUSED)
        self.assertIn("refusing to open", err)
        self.assertEqual(self.calls, [])

    def test_macos_opens_the_link_with_open(self):
        code, out, _err = self.main([LINK])
        self.assertEqual(code, open_pause_link.EXIT_OK)
        self.assertEqual(self.calls, [["/usr/bin/open", LINK]])
        self.assertIn("Opened", out)

    def test_linux_opens_the_link_with_xdg_open(self):
        code, _out, _err = self.main([LINK], platform="linux")
        self.assertEqual(code, open_pause_link.EXIT_OK)
        self.assertEqual(self.calls, [["/usr/bin/xdg-open", LINK]])

    def test_linux_without_xdg_open_is_skipped(self):
        code, out, _err = self.main([LINK], platform="linux", which=lambda _name: None)
        self.assertEqual(code, open_pause_link.EXIT_SKIPPED)
        self.assertIn("skipped", out)
        self.assertEqual(self.calls, [])

    def test_other_platform_is_skipped(self):
        code, _out, _err = self.main([LINK], platform="win32")
        self.assertEqual(code, open_pause_link.EXIT_SKIPPED)
        self.assertEqual(self.calls, [])

    def test_opener_failure_exits_1(self):
        code, _out, err = self.main([LINK], run=self.fake_run(returncode=4))
        self.assertEqual(code, open_pause_link.EXIT_OPENER_FAILED)
        self.assertIn("exited 4", err)

    def test_opener_timeout_exits_1(self):
        def run(args, **_kwargs):
            raise subprocess.TimeoutExpired(args, 10)

        code, _out, _err = self.main([LINK], run=run)
        self.assertEqual(code, open_pause_link.EXIT_OPENER_FAILED)

    def test_no_argument_is_refused(self):
        code, _out, err = self.main([])
        self.assertEqual(code, open_pause_link.EXIT_REFUSED)
        self.assertIn("usage", err)

    def test_two_arguments_are_refused(self):
        code, _out, _err = self.main([LINK, LINK])
        self.assertEqual(code, open_pause_link.EXIT_REFUSED)

    def test_live_mode_page_is_refused(self):
        self.assert_refused(["https://dashboard.stripe.com/subscriptions/sub_1234"])

    def test_other_dashboard_page_is_refused(self):
        self.assert_refused(["https://dashboard.stripe.com/test/customers/cus_1234"])

    def test_http_is_refused(self):
        self.assert_refused(["http://dashboard.stripe.com/test/subscriptions/sub_1234"])

    def test_other_host_is_refused(self):
        self.assert_refused(["https://dashboard.stripe.com.evil.example/test/subscriptions/sub_1234"])

    def test_userinfo_host_trick_is_refused(self):
        self.assert_refused(["https://dashboard.stripe.com@evil.example/test/subscriptions/sub_1234"])

    def test_query_string_is_refused(self):
        self.assert_refused([LINK + "?next=https://evil.example"])

    def test_fragment_is_refused(self):
        self.assert_refused([LINK + "#frag"])

    def test_trailing_path_is_refused(self):
        self.assert_refused([LINK + "/../../apikeys"])

    def test_trailing_newline_is_refused(self):
        self.assert_refused([LINK + "\n"])

    def test_non_subscription_id_is_refused(self):
        self.assert_refused(["https://dashboard.stripe.com/test/subscriptions/cus_1234"])

    def test_empty_subscription_id_is_refused(self):
        self.assert_refused(["https://dashboard.stripe.com/test/subscriptions/sub_"])

    def test_file_url_is_refused(self):
        self.assert_refused(["file:///etc/passwd"])

    def test_option_looking_argument_is_refused(self):
        self.assert_refused(["--help"])


class SkillMatchesScriptTest(unittest.TestCase):
    def test_skill_states_the_same_pattern_the_script_enforces(self):
        with open(os.path.join(SKILL, "SKILL.md"), encoding="utf-8") as handle:
            skill_text = handle.read()
        self.assertIn(f"`^{open_pause_link.LINK_REGEX}$`", skill_text)


class ScriptIsExecutableTest(unittest.TestCase):
    def test_script_has_execute_bit(self):
        script_path = os.path.join(SCRIPTS, "open_pause_link.py")
        self.assertTrue(os.access(script_path, os.X_OK), f"{script_path} must be executable")


if __name__ == "__main__":
    unittest.main()
