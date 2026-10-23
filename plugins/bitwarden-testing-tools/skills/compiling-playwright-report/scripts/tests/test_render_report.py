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
    "plan_file": ".playwright-testing-artifacts/billing-ui/test-plan-20260729-1432.md",
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

    def test_summary_tile_counts(self):
        self.assertIn('<span class="tile-n">3</span><span class="tile-l">Total</span>', self.out)
        self.assertIn('<span class="tile-n">1</span><span class="tile-l">Errors</span>', self.out)

    def test_zero_count_tile_is_dimmed(self):
        self.assertIn('class="tile tile-fail tile-zero"', self.out)
        self.assertNotIn('class="tile tile-error tile-zero"', self.out)

    def test_status_labels_and_data_attributes(self):
        self.assertIn('data-status="pass"', self.out)
        self.assertIn('data-status="error"', self.out)
        self.assertIn('data-status="adaptive"', self.out)
        self.assertRegex(self.out, r'status-text t-adaptive">Passed \(adaptive\)<')

    def test_every_case_starts_collapsed(self):
        self.assertNotIn('<details class="case case-pass" id="case-1" data-status="pass" open', self.out)
        self.assertNotRegex(self.out, r'<details class="case[^>]* open')

    def test_adaptive_case_shows_specified_and_found(self):
        self.assertIn("<dt>Plan specified</dt><dd>badge reads 'Inactive'</dd>", self.out)
        self.assertIn("<dt>Runner found</dt><dd>badge reads 'Canceled'</dd>", self.out)

    def test_setup_and_test_sections_present(self):
        self.assertIn("Setup steps", self.out)
        self.assertIn("Test steps", self.out)

    def test_setup_section_only_when_present(self):
        # Only case 1 has setup steps.
        self.assertEqual(self.out.count('<details class="sub"'), 1)

    def test_setup_section_opens_when_a_setup_step_failed(self):
        data = {
            "run_status": "complete",
            "cases": [
                {
                    "number": 1,
                    "name": "x",
                    "status": "FAIL",
                    "setup_steps": [{"text": "log in", "outcome": "FAIL"}],
                    "test_steps": [],
                }
            ],
        }
        self.assertIn('<details class="sub" open>', render_report.render(data, HEADER))

    def test_human_step_class(self):
        self.assertIn('class="step step-human"', self.out)
        self.assertIn("Attach a Stripe test clock", self.out)

    def test_screenshot_thumbnail_relative_path(self):
        self.assertIn(
            'href="screenshots/setup-tc-1-step-1-20260724-0930.png"', self.out
        )
        self.assertIn(
            '<img src="screenshots/setup-tc-1-step-1-20260724-0930.png"', self.out
        )

    def test_step_outcome_is_a_pill(self):
        self.assertIn("Clicked Tools dropdown</span>", self.out)
        self.assertIn('<span class="pill pill-pass">', self.out)

    def test_observed_value_rendered(self):
        self.assertIn("<code>500 response</code>", self.out)

    def test_failed_step_error_details_are_red(self):
        self.assertIn('class="errdet errdet-fail"', self.out)
        self.assertIn("@OrganizationKeyId is not a parameter", self.out)

    def test_passed_step_error_details_are_amber(self):
        self.assertIn('class="errdet errdet-warn"', self.out)
        self.assertIn("GET /api/sends", self.out)

    def test_request_line_shows_status_and_count(self):
        self.assertIn("POST /api/organizations/abc/export → 500 Internal Server Error", self.out)
        self.assertIn("GET /api/sends → 404 Not Found (×2)", self.out)

    def test_stack_trace_is_collapsed_with_frame_count(self):
        self.assertIn("<summary>Stack trace (2 frames)</summary>", self.out)
        self.assertNotIn('<details class="errdet-stack" open', self.out)

    def test_issues_summary_lists_error_with_notes(self):
        self.assertIn("Test Case 2:", self.out)
        self.assertIn("Server returned 500 on export request.", self.out)

    def test_issue_links_to_its_case(self):
        self.assertIn('<a href="#case-2">Test Case 2:', self.out)
        self.assertIn('id="case-2"', self.out)

    def test_recommendations_fix_adaptive_retest(self):
        self.assertIn('Fix: <a href="#case-2">Test Case 2</a>', self.out)
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
        # The report carries its own inline script, so check the payload, not the tag.
        self.assertNotIn("<script>alert(1)", out)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", out)
        self.assertNotIn("<img", out)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", out)


def render_one_step(step):
    data = {
        "run_status": "complete",
        "cases": [{"number": 1, "name": "Case", "status": "PASS", "test_steps": [step]}],
    }
    return render_report.render(data, HEADER)


class RenderErrorDetailsTest(unittest.TestCase):
    def test_error_details_without_observed(self):
        out = render_one_step(
            {"text": "Click", "outcome": "PASS", "error_details": [{"request": "GET /api/x", "status": 400}]}
        )
        self.assertIn('class="errdet errdet-warn"', out)
        self.assertNotIn('class="observed"', out)

    def test_no_error_details_no_section(self):
        for step in ({"text": "Click", "outcome": "PASS"},
                     {"text": "Click", "outcome": "PASS", "error_details": []}):
            with self.subTest(step=step):
                self.assertNotIn("errdet", render_one_step(step))

    def test_external_trigger_entry_has_no_status(self):
        out = render_one_step(
            {"text": "Trigger", "outcome": "PASS",
             "error_details": [{"request": "POST /stripe/webhook", "exception_message": "boom"}]}
        )
        self.assertIn("POST /stripe/webhook", out)
        box = out[out.index('class="errdet-box"'):]
        self.assertNotIn("→", box[: box.index("</div>")])

    def test_validation_errors_are_listed(self):
        out = render_one_step(
            {"text": "Save", "outcome": "FAIL",
             "error_details": [{"request": "POST /api/x", "status": 400,
                                "validation_errors": {"Name": ["Required."]}}]}
        )
        self.assertIn("Name: Required.", out)

    def test_malformed_error_details_are_skipped(self):
        out = render_one_step({"text": "Click", "outcome": "PASS", "error_details": "oops"})
        self.assertNotIn("errdet", out)
        out = render_one_step(
            {"text": "Click", "outcome": "PASS",
             "error_details": [1, {"status": 500}, {"request": "GET /ok", "status": "500"}]}
        )
        self.assertIn("GET /ok → 500", out)
        self.assertEqual(out.count('class="errdet-box"'), 1)

    def test_error_details_render_inert(self):
        out = render_one_step(
            {"text": "Click", "outcome": "FAIL",
             "error_details": [{"request": 'GET /x"><img src=x onerror=alert(1)>',
                                "exception_message": "<script>alert(2)</script>"}]}
        )
        self.assertNotIn("<img src=x", out)
        self.assertNotIn("<script>alert(2)", out)
        self.assertIn("&lt;script&gt;alert(2)", out)


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
                    "--plan-file", "/tmp/test-plan.md",
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

    def test_totals_of_the_wrong_type_exit_3(self):
        case = {"number": 1, "name": "x", "status": "PASS", "test_steps": []}
        for totals in ([1], "five", 7):
            with self.subTest(totals=totals):
                text = json.dumps({"run_status": "complete", "totals": totals, "cases": [case]})
                self.assertEqual(self._main_expecting_exit(text), 3)

    def test_non_numeric_total_exits_3(self):
        case = {"number": 1, "name": "x", "status": "PASS", "test_steps": []}
        for value in ("many", None, [1]):
            with self.subTest(value=value):
                text = json.dumps(
                    {"run_status": "complete", "totals": {"total": value}, "cases": [case]}
                )
                self.assertEqual(self._main_expecting_exit(text), 3)

    def test_bad_enum_exits_3(self):
        text = json.dumps(
            {"run_status": "complete", "cases": [{"number": 1, "name": "x", "status": "NOPE", "test_steps": []}]}
        )
        self.assertEqual(self._main_expecting_exit(text), 3)


ABORTED_WITH_CASES = {
    "run_status": "aborted",
    "abort_reason": "setup failure before test cases (re-authentication failed)",
    "totals": {"total": 1, "passed": 1, "adaptive": 0, "failed": 0, "errored": 0},
    "cases": [
        {
            "number": 1,
            "name": "Login",
            "status": "PASS",
            "url": "https://localhost:8080",
            "test_steps": [{"text": "Sign in", "outcome": "PASS"}],
        }
    ],
}


class RenderAbortedWithCasesTest(unittest.TestCase):
    def test_renders_and_names_the_abort_reason(self):
        out = render_report.render(ABORTED_WITH_CASES, HEADER)
        self.assertIn("Run aborted", out)
        self.assertIn("re-authentication failed", out)
        self.assertIn("Login", out)

    def test_main_renders_aborted_run_with_cases(self):
        d = tempfile.mkdtemp()
        results = os.path.join(d, "results.json")
        out_path = os.path.join(d, "report.html")
        with open(results, "w", encoding="utf-8") as f:
            json.dump(ABORTED_WITH_CASES, f)
        rc = render_report.main(
            [
                "--results", results,
                "--template-dir", TEMPLATES,
                "--output", out_path,
                "--plan-name", "Billing UI",
                "--date", "2026-07-29",
                "--slug", "billing-ui",
                "--services-tested", "web (8080)",
                "--base-url", "https://localhost:8080",
                "--plan-file", "/tmp/test-plan-20260729-1432.md",
            ]
        )
        self.assertEqual(rc, 0)
        self.assertTrue(os.path.exists(out_path))

    def test_main_still_refuses_aborted_run_with_no_cases(self):
        d = tempfile.mkdtemp()
        results = os.path.join(d, "results.json")
        with open(results, "w", encoding="utf-8") as f:
            json.dump({"run_status": "aborted", "abort_reason": "login failed"}, f)
        rc = render_report.main(
            [
                "--results", results,
                "--template-dir", TEMPLATES,
                "--output", os.path.join(d, "report.html"),
                "--plan-name", "Billing UI",
                "--date", "2026-07-29",
                "--slug", "billing-ui",
                "--services-tested", "web (8080)",
                "--base-url", "https://localhost:8080",
                "--plan-file", "/tmp/test-plan-20260729-1432.md",
            ]
        )
        self.assertEqual(rc, 2)

    def test_complete_run_has_no_abort_banner(self):
        out = render_report.render(load_example("complete-run.json"), HEADER)
        self.assertNotIn("Run aborted", out)


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
                "--plan-file", ".playwright-testing-artifacts/billing-ui/test-plan-20260724-0930.md",
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
                "--plan-file", "/tmp/test-plan.md",
            ]
        )
        self.assertEqual(rc, 2)


class PlanFileHeaderTest(unittest.TestCase):
    def test_header_shows_the_timestamped_plan_file(self):
        out = render_report.render(load_example("complete-run.json"), HEADER)
        self.assertIn("test-plan-20260729-1432.md", out)

    def test_header_does_not_hardcode_an_unversioned_plan_name(self):
        out = render_report.render(load_example("complete-run.json"), HEADER)
        self.assertNotIn("/test-plan.md", out)


def case_with(status, **extra):
    return {"number": 1, "name": "n", "status": status, "test_steps": [], **extra}


def run_of(*statuses):
    return {
        "run_status": "complete",
        "cases": [dict(case_with(status), number=i) for i, status in enumerate(statuses, start=1)],
    }


class FormatDateTest(unittest.TestCase):
    def test_afternoon_timestamp_is_12_hour_pm(self):
        self.assertEqual(render_report.format_date("20261005-1653"), "Oct 5, 2026 \u00b7 4:53 PM")

    def test_morning_timestamp_is_am(self):
        self.assertEqual(render_report.format_date("20260729-0905"), "Jul 29, 2026 \u00b7 9:05 AM")

    def test_midnight_and_noon(self):
        self.assertEqual(render_report.format_date("20260101-0000"), "Jan 1, 2026 \u00b7 12:00 AM")
        self.assertEqual(render_report.format_date("20260101-1200"), "Jan 1, 2026 \u00b7 12:00 PM")

    def test_other_shapes_are_shown_as_given(self):
        for raw in ("2026-07-24", "yesterday", "20261305-1653", "20261005-2561"):
            with self.subTest(raw=raw):
                self.assertEqual(render_report.format_date(raw), raw)


class EscLinkedTest(unittest.TestCase):
    def test_url_becomes_a_new_tab_link(self):
        self.assertEqual(
            render_report.esc_linked("see https://localhost:8080/a"),
            'see <a href="https://localhost:8080/a" target="_blank" rel="noopener noreferrer">'
            "https://localhost:8080/a</a>",
        )

    def test_trailing_punctuation_stays_outside_the_link(self):
        out = render_report.esc_linked("(https://localhost:8080/a).")
        self.assertIn('href="https://localhost:8080/a"', out)
        self.assertTrue(out.endswith("</a>)."))

    def test_url_with_an_unresolved_placeholder_is_not_linked(self):
        out = render_report.esc_linked("https://localhost:8080/#/organizations/:organizationId/billing")
        self.assertNotIn("<a ", out)

    def test_only_http_and_https_are_linked(self):
        for text in ("javascript:alert(1)", "data:text/html,x", "ftp://host/x", "file:///etc/passwd"):
            with self.subTest(text=text):
                self.assertNotIn("<a ", render_report.esc_linked(text))

    def test_surrounding_text_and_url_are_escaped(self):
        out = render_report.esc_linked('<b>x</b> https://localhost:8080/?a=1&b=2')
        self.assertIn("&lt;b&gt;x&lt;/b&gt;", out)
        self.assertIn('href="https://localhost:8080/?a=1&amp;b=2"', out)

    # cspell:ignore onmouseover
    def test_quote_cannot_break_out_of_the_href(self):
        out = render_report.esc_linked('https://localhost:8080/x"onmouseover="alert(1)')
        self.assertIn('<a href="https://localhost:8080/x" target="_blank"', out)
        self.assertNotRegex(out, r"<a [^>]*onmouseover")

    def test_urls_are_linked_in_a_rendered_report(self):
        data = run_of("PASS")
        data["cases"][0]["url"] = "https://localhost:8080/#/vault"
        data["cases"][0]["test_steps"] = [
            {"text": "open https://localhost:8080/#/x", "outcome": "PASS", "observed": "landed on https://localhost:8080/#/y"}
        ]
        out = render_report.render(data, HEADER)
        for url in ("https://localhost:8080/#/vault", "https://localhost:8080/#/x", "https://localhost:8080/#/y"):
            with self.subTest(url=url):
                self.assertIn(f'<a href="{url}"', out)

    def test_base_url_in_the_header_is_linked(self):
        out = render_report.render(run_of("PASS"), HEADER)
        self.assertIn('<a href="https://localhost:8080"', out)


class HeroTest(unittest.TestCase):
    def render_hero(self, *statuses, header=HEADER):
        return render_report.render(run_of(*statuses), header)

    def test_all_pass(self):
        out = self.render_hero("PASS", "PASS")
        self.assertIn('class="hero hero-pass"', out)
        self.assertIn("All tests passed", out)
        self.assertIn("<b>100%</b>", out)
        self.assertIn("2 of 2 passed", out)

    def test_failure_wins_over_error(self):
        out = self.render_hero("PASS", "FAIL", "ERROR")
        self.assertIn('class="hero hero-fail"', out)
        self.assertIn("Run has failures", out)
        self.assertIn("1 failed, 1 error across 3 test cases", out)

    def test_error_without_failure(self):
        out = self.render_hero("PASS", "ERROR")
        self.assertIn('class="hero hero-error"', out)
        self.assertIn("Run had errors", out)

    def test_adaptive_counts_toward_the_pass_rate(self):
        out = self.render_hero("PASS", "PASS (adaptive)", "FAIL", "FAIL")
        self.assertIn("<b>50%</b>", out)
        self.assertIn("2 of 4 passed", out)

    def test_a_run_with_a_failure_never_reads_100_percent(self):
        out = self.render_hero(*(["PASS"] * 199 + ["FAIL"]))
        self.assertIn("<b>99%</b>", out)

    def test_aborted_run_is_flagged(self):
        out = render_report.render(ABORTED_WITH_CASES, HEADER)
        self.assertIn('class="hero hero-error"', out)
        self.assertIn("Run aborted", out)

    def test_empty_complete_run_does_not_divide_by_zero(self):
        out = render_report.render({"run_status": "complete", "cases": []}, HEADER)
        self.assertIn("No test cases ran", out)
        self.assertIn("<b>0%</b>", out)

    def test_ring_has_one_arc_per_non_empty_status(self):
        style = render_report.ring_style({"total": 4, "passed": 3, "adaptive": 0, "failed": 0, "errored": 1})
        self.assertEqual(
            style,
            "background: conic-gradient(var(--pass) 0.00% 75.00%, var(--error) 75.00% 100.00%)",
        )

    def test_date_is_shown_in_12_hour_time_in_the_hero_and_run_details(self):
        header = dict(HEADER, date="20261005-1653")
        out = self.render_hero("PASS", header=header)
        self.assertEqual(out.count("Oct 5, 2026 \u00b7 4:53 PM"), 2)
        self.assertNotIn("16:53", out)

    def test_services_become_chips(self):
        header = dict(HEADER, services_tested="api (4000), web (8080)")
        out = self.render_hero("PASS", header=header)
        self.assertIn('<span class="chip">api (4000)</span><span class="chip">web (8080)</span>', out)


class TitleTest(unittest.TestCase):
    def write_context(self, text):
        handle = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
        handle.write(text)
        handle.close()
        self.addCleanup(os.unlink, handle.name)
        return handle.name

    def test_title_is_read_from_the_context_fence(self):
        path = self.write_context(
            "<!-- CONTEXT START -->\n\n# Context\n\n**Input Type:** jira-ticket\n"
            "**Title:** Switch to annual billing\n\n## Feature Description\n\nx\n<!-- CONTEXT END -->\n"
        )
        self.assertEqual(render_report.read_title(path), "Switch to annual billing")

    def test_no_title_line_yields_none(self):
        path = self.write_context("<!-- CONTEXT START -->\n# Context\n<!-- CONTEXT END -->\n")
        self.assertIsNone(render_report.read_title(path))

    def test_title_outside_the_fence_is_ignored(self):
        path = self.write_context("**Title:** outside\n<!-- CONTEXT START -->\n# Context\n<!-- CONTEXT END -->\n")
        self.assertIsNone(render_report.read_title(path))

    def test_embedded_end_marker_cannot_hide_the_title(self):
        path = self.write_context(
            "<!-- CONTEXT START -->\n**Title:** real\n<!-- CONTEXT END -->\nnoise\n<!-- CONTEXT END -->\n"
        )
        self.assertEqual(render_report.read_title(path), "real")

    def test_missing_file_yields_none_and_a_warning(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(render_report.read_title(os.path.join(d, "absent.md")))

    def test_long_title_is_truncated(self):
        path = self.write_context("<!-- CONTEXT START -->\n**Title:** " + "word " * 60 + "\n<!-- CONTEXT END -->\n")
        title = render_report.read_title(path)
        self.assertEqual(len(title), render_report.TITLE_MAX_LENGTH)
        self.assertTrue(title.endswith("\u2026"))

    def test_title_is_the_heading_with_the_plan_name_as_a_key(self):
        out = render_report.render(run_of("PASS"), dict(HEADER, title="Switch to annual billing"))
        self.assertIn('<div class="hero-key">Billing UI</div><h1>Switch to annual billing</h1>', out)

    def test_without_a_title_the_plan_name_is_the_heading(self):
        out = render_report.render(run_of("PASS"), HEADER)
        self.assertIn("<h1>Billing UI</h1>", out)
        self.assertNotIn("hero-key\">", out)

    def test_title_is_escaped(self):
        out = render_report.render(run_of("PASS"), dict(HEADER, title="<img src=x onerror=alert(1)>"))
        self.assertNotIn("<img src=x", out)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", out)

    def test_main_takes_the_title_from_context_file(self):
        context = self.write_context("<!-- CONTEXT START -->\n**Title:** From the artifact\n<!-- CONTEXT END -->\n")
        d = tempfile.mkdtemp()
        out = os.path.join(d, "report.html")
        rc = render_report.main(
            [
                "--results", os.path.join(EXAMPLES, "complete-run.json"),
                "--template-dir", TEMPLATES, "--output", out,
                "--plan-name", "Billing UI", "--date", "20260724-0930",
                "--slug", "billing-ui", "--services-tested", "web (8080)",
                "--base-url", "https://localhost:8080",
                "--plan-file", "/tmp/test-plan-20260724-0930.md",
                "--context-file", context,
            ]
        )
        self.assertEqual(rc, 0)
        with open(out, encoding="utf-8") as f:
            self.assertIn("<h1>From the artifact</h1>", f.read())


if __name__ == "__main__":
    unittest.main()
