#!/usr/bin/env python3
"""Unit tests for open_report: only a run's own HTML report is ever opened.

The working directory, platform, opener lookup, and process launch are
injected, so no test opens anything or depends on the machine it runs on.

Run with:  python3 -m unittest discover -s scripts/tests   (from the skill dir)
"""
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)

import open_report

REPORT_NAME = "report-20261006-0930.html"


class OpenReportTest(unittest.TestCase):
    def setUp(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.cwd = temp_dir.name
        self.run_dir = os.path.join(self.cwd, ".playwright-testing-artifacts", "pm-12345-slug")
        os.makedirs(self.run_dir)
        self.report = self.write(os.path.join(self.run_dir, REPORT_NAME))
        self.calls = []

    def write(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("<html></html>")
        return path

    def fake_run(self, returncode=0):
        def run(args, **_kwargs):
            self.calls.append(args)
            return subprocess.CompletedProcess(args, returncode)

        return run

    def main(self, argv, platform="darwin", which=None, run=None):
        which = which or (lambda name: f"/usr/bin/{name}")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = open_report.main(
                argv, cwd=self.cwd, platform=platform, which=which, run=run or self.fake_run()
            )
        return code, out.getvalue(), err.getvalue()

    def assert_refused(self, argv, reason):
        code, _out, err = self.main(argv)
        self.assertEqual(code, open_report.EXIT_REFUSED)
        self.assertIn(reason, err)
        self.assertEqual(self.calls, [])

    def test_macos_opens_the_report_with_open(self):
        code, out, _err = self.main([self.report])
        self.assertEqual(code, open_report.EXIT_OK)
        self.assertEqual(self.calls, [["/usr/bin/open", os.path.realpath(self.report)]])
        self.assertIn("Opened", out)

    def test_linux_opens_the_report_with_xdg_open(self):
        code, _out, _err = self.main([self.report], platform="linux")
        self.assertEqual(code, open_report.EXIT_OK)
        self.assertEqual(self.calls, [["/usr/bin/xdg-open", os.path.realpath(self.report)]])

    def test_relative_path_from_the_working_directory_is_accepted(self):
        relative = os.path.relpath(self.report, self.cwd)
        code, _out, _err = self.main([relative])
        self.assertEqual(code, open_report.EXIT_OK)

    def test_linux_without_xdg_open_is_skipped(self):
        code, out, _err = self.main([self.report], platform="linux", which=lambda _name: None)
        self.assertEqual(code, open_report.EXIT_SKIPPED)
        self.assertIn("skipped", out)
        self.assertEqual(self.calls, [])

    def test_other_platform_is_skipped(self):
        code, _out, _err = self.main([self.report], platform="win32")
        self.assertEqual(code, open_report.EXIT_SKIPPED)
        self.assertEqual(self.calls, [])

    def test_opener_failure_exits_1(self):
        code, _out, err = self.main([self.report], run=self.fake_run(returncode=4))
        self.assertEqual(code, open_report.EXIT_OPENER_FAILED)
        self.assertIn("exited 4", err)

    def test_opener_timeout_exits_1(self):
        def run(args, **_kwargs):
            raise subprocess.TimeoutExpired(args, 10)

        code, _out, _err = self.main([self.report], run=run)
        self.assertEqual(code, open_report.EXIT_OPENER_FAILED)

    def test_no_argument_is_refused(self):
        code, _out, err = self.main([])
        self.assertEqual(code, open_report.EXIT_REFUSED)
        self.assertIn("usage", err)

    def test_two_arguments_are_refused(self):
        code, _out, _err = self.main([self.report, self.report])
        self.assertEqual(code, open_report.EXIT_REFUSED)

    def test_wrong_file_name_is_refused(self):
        other = self.write(os.path.join(self.run_dir, "test-plan-20261006-0930.md"))
        self.assert_refused([other], "is not named report-YYYYMMDD-HHmm.html")

    def test_missing_file_is_refused(self):
        missing = os.path.join(self.run_dir, "report-20990101-0000.html")
        self.assert_refused([missing], "is not an existing file")

    def test_report_outside_the_artifacts_folder_is_refused(self):
        outside = self.write(os.path.join(self.cwd, "elsewhere", "run", REPORT_NAME))
        self.assert_refused([outside], "is not directly inside a run folder")

    def test_report_directly_in_the_artifacts_folder_is_refused(self):
        shallow = self.write(os.path.join(self.cwd, ".playwright-testing-artifacts", REPORT_NAME))
        self.assert_refused([shallow], "is not directly inside a run folder")

    def test_dot_dot_path_out_of_the_artifacts_folder_is_refused(self):
        self.write(os.path.join(self.cwd, "elsewhere", "run", REPORT_NAME))
        sneaky = os.path.join(self.run_dir, "..", "..", "elsewhere", "run", REPORT_NAME)
        self.assertTrue(os.path.isfile(sneaky))
        self.assert_refused([sneaky], "is not directly inside a run folder")

    def test_symlinked_report_is_refused(self):
        target = self.write(os.path.join(self.cwd, "elsewhere", "secret.html"))
        link = os.path.join(self.run_dir, "report-20261006-1000.html")
        os.symlink(target, link)
        self.assert_refused([link], "is a symlink")

    def test_report_reached_through_a_symlinked_run_folder_is_refused(self):
        real_dir = os.path.join(self.cwd, "elsewhere", "run")
        self.write(os.path.join(real_dir, REPORT_NAME))
        linked_dir = os.path.join(self.cwd, ".playwright-testing-artifacts", "linked")
        os.symlink(real_dir, linked_dir)
        self.assert_refused([os.path.join(linked_dir, REPORT_NAME)], "is not directly inside a run folder")


class ScriptIsExecutableTest(unittest.TestCase):
    def test_script_has_execute_bit(self):
        script_path = os.path.join(SCRIPTS, "open_report.py")
        self.assertTrue(os.access(script_path, os.X_OK), f"{script_path} must be executable")


if __name__ == "__main__":
    unittest.main()
