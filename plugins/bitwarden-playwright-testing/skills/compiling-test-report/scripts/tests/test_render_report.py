#!/usr/bin/env python3
"""Unit tests for render_report: rendering fidelity, escaping, and validation.

Run with:  python3 -m unittest discover -s scripts/tests   (from the skill dir)
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
SKILL = os.path.dirname(SCRIPTS)
sys.path.insert(0, SCRIPTS)

import render_report

EXAMPLES = os.path.join(SKILL, "references", "examples")
TEMPLATES = os.path.join(SKILL, "templates")
HEADER = {
    "template_dir": TEMPLATES,
    "plan_name": "Billing UI",
    "date": "2026-07-24",
    "slug": "billing-ui",
    "services_tested": "web (8080)",
    "base_url": "https://localhost:8080",
}


def load_example(name):
    with open(os.path.join(EXAMPLES, name), encoding="utf-8") as f:
        return json.load(f)


class RenderCompleteRunTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_example("complete-run.json")
        cls.out = render_report.render(cls.data, HEADER)

    def test_tally_counts(self):
        self.assertEqual(
            render_report.tally(self.data["cases"]),
            {"total": 3, "passed": 1, "adaptive": 1, "failed": 0, "errored": 1},
        )

    def test_summary_table_total_cell(self):
        self.assertIn("<td>3</td>", self.out)

    def test_status_emoji_mapping(self):
        self.assertIn("✅ PASS", self.out)
        self.assertIn("⚠️ ERROR", self.out)
        self.assertIn("⚠️ PASS (adaptive)", self.out)

    def test_setup_and_test_lists_present(self):
        self.assertIn("<strong>Setup Steps</strong>", self.out)
        self.assertIn("<strong>Test Steps</strong>", self.out)

    def test_setup_section_only_when_present(self):
        # Only case 1 has setup steps.
        self.assertEqual(self.out.count("<strong>Setup Steps</strong>"), 1)

    def test_human_step_class(self):
        self.assertIn('class="human-step"', self.out)
        self.assertIn("Attach a Stripe test clock", self.out)

    def test_screenshot_thumbnail_relative_path(self):
        self.assertIn(
            'href="screenshots/setup-tc-1-step-1-20260724-0930.png"', self.out
        )
        self.assertIn(
            '<img src="screenshots/setup-tc-1-step-1-20260724-0930.png"', self.out
        )

    def test_step_separator_is_hyphen(self):
        self.assertIn("Clicked Tools dropdown - PASS", self.out)

    def test_observed_value_rendered(self):
        self.assertIn("(500 response)", self.out)

    def test_issues_summary_lists_error_with_notes(self):
        self.assertIn("Test Case 2:", self.out)
        self.assertIn("Server returned 500 on export request.", self.out)

    def test_recommendations_fix_adaptive_retest(self):
        self.assertIn("Fix: Test Case 2", self.out)
        self.assertIn(
            "Update test plan: TC3 asserted badge reads 'Inactive', "
            "actual rendering is badge reads 'Canceled'.",
            self.out,
        )
        self.assertIn("Re-test", self.out)


class RenderEscapingTest(unittest.TestCase):
    def test_payloads_render_inert(self):
        data = {
            "run_status": "complete",
            "cases": [
                {
                    "number": 1,
                    "name": "<script>alert(1)</script>",
                    "status": "FAIL",
                    "test_steps": [{"text": "attempt", "outcome": "FAIL"}],
                    "notes": "<img src=x onerror=alert(1)>",
                }
            ],
        }
        out = render_report.render(data, HEADER)
        self.assertNotIn("<script>", out)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", out)
        self.assertNotIn("<img", out)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", out)


class RenderValidationTest(unittest.TestCase):
    def _main_expecting_exit(self, text):
        d = tempfile.mkdtemp()
        rp = os.path.join(d, "r.json")
        op = os.path.join(d, "o.html")
        with open(rp, "w", encoding="utf-8") as f:
            f.write(text)
        with self.assertRaises(SystemExit) as cm:
            render_report.main(
                [
                    "--results", rp, "--template-dir", TEMPLATES, "--output", op,
                    "--plan-name", "p", "--date", "d", "--slug", "s",
                    "--services-tested", "x", "--base-url", "u",
                ]
            )
        return cm.exception.code

    def test_malformed_json_exits_3(self):
        self.assertEqual(self._main_expecting_exit("{not json"), 3)

    def test_missing_status_exits_3(self):
        text = json.dumps(
            {"run_status": "complete", "cases": [{"number": 1, "name": "x", "test_steps": []}]}
        )
        self.assertEqual(self._main_expecting_exit(text), 3)

    def test_bad_enum_exits_3(self):
        text = json.dumps(
            {"run_status": "complete", "cases": [{"number": 1, "name": "x", "status": "NOPE", "test_steps": []}]}
        )
        self.assertEqual(self._main_expecting_exit(text), 3)


class RenderMainTest(unittest.TestCase):
    def test_main_writes_report(self):
        d = tempfile.mkdtemp()
        out = os.path.join(d, "report.html")
        rc = render_report.main(
            [
                "--results", os.path.join(EXAMPLES, "complete-run.json"),
                "--template-dir", TEMPLATES, "--output", out,
                "--plan-name", "Billing UI", "--date", "2026-07-24",
                "--slug", "billing-ui", "--services-tested", "web (8080)",
                "--base-url", "https://localhost:8080",
            ]
        )
        self.assertEqual(rc, 0)
        with open(out, encoding="utf-8") as f:
            doc = f.read()
        self.assertIn("<title>Web Test Report: Billing UI</title>", doc)

    def test_aborted_run_returns_2(self):
        d = tempfile.mkdtemp()
        out = os.path.join(d, "report.html")
        rc = render_report.main(
            [
                "--results", os.path.join(EXAMPLES, "aborted-run.json"),
                "--template-dir", TEMPLATES, "--output", out,
                "--plan-name", "p", "--date", "d", "--slug", "s",
                "--services-tested", "x", "--base-url", "u",
            ]
        )
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
