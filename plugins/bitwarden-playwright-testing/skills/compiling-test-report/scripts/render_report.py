#!/usr/bin/env python3
# render_report.py - Render a Bitwarden Playwright test report as HTML from the
# canonical results JSON. Deterministic and dependency-free (stdlib only).
# Every interpolated value is HTML-escaped by this script (esc for body text,
# esc_attr for attribute values); the template markup the script owns is never
# escaped.
#
# Usage:
#   render_report.py --results <path> --template-dir <dir> --output <path>
#     --plan-name <str> --date <str> --slug <str> --services-tested <str>
#     --base-url <str>
#
# Exit codes: 0 report written; 2 usage error or aborted run (caller skips
# rendering); 3 invalid or malformed results JSON.

import argparse
import html
import json
import os
import re
import sys

from results_common import fail, tally

STATUS_DISPLAY = {
    "PASS": "✅ PASS",
    "PASS (adaptive)": "⚠️ PASS (adaptive)",
    "FAIL": "❌ FAIL",
    "ERROR": "⚠️ ERROR",
}
STATUS_VALUES = set(STATUS_DISPLAY)
ISSUE_EMOJI = {"FAIL": "❌", "ERROR": "⚠️"}

STEP_LI = "<li{cls}>{text}{screenshot}</li>"
SCREENSHOT = (
    '\n  <a class="screenshot-link" href="screenshots/{file}" target="_blank">'
    '<img src="screenshots/{file}" alt="{alt}" /></a>'
)


def esc(value):
    # Escape a raw-text leaf for element-body context (&, <, >).
    return html.escape("" if value is None else str(value), quote=False)


def esc_attr(value):
    # Escape a raw-text leaf destined for an attribute value (also quotes).
    return html.escape("" if value is None else str(value), quote=True)


def fill(template, **tokens):
    # Replace each {{TOKEN}} in the template exactly once; substituted values
    # are never re-scanned, so untrusted text cannot forge another token.
    return re.sub(
        r"\{\{(\w+)\}\}",
        lambda m: tokens.get(m.group(1), m.group(0)),
        template,
    )


def validate(data):
    if not isinstance(data, dict):
        fail("results root must be a JSON object")
    status = data.get("run_status")
    if status not in ("complete", "aborted"):
        fail(f"run_status must be 'complete' or 'aborted' to render, got {status!r}")
    if status == "aborted":
        return
    cases = data.get("cases")
    if not isinstance(cases, list):
        fail("'cases' must be a list for a complete run")
    for case in cases:
        if not isinstance(case, dict):
            fail("each case must be a JSON object")
        if "status" not in case:
            fail(f"case {case.get('number')} is missing 'status'")
        if case["status"] not in STATUS_VALUES:
            fail(f"case {case.get('number')} has invalid status {case['status']!r}")
    counted = tally(cases)
    stored = data.get("totals")
    if stored is not None:
        for key, value in counted.items():
            if int(stored.get(key, -1)) != value:
                fail(f"totals.{key}={stored.get(key)} does not match counted {value}")


def load_results(path):
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        fail(f"results file not found: {path}")
    except json.JSONDecodeError as err:
        fail(f"results file is not valid JSON: {err}")
    validate(data)
    return data


def read_template(template_dir, name):
    with open(os.path.join(template_dir, name), encoding="utf-8") as handle:
        return handle.read()


def render_step(step):
    text = esc(step.get("text", ""))
    outcome = step.get("outcome")
    if outcome:
        text += " - " + esc(outcome)
    observed = step.get("observed")
    if observed:
        text += " (" + esc(observed) + ")"
    screenshot = ""
    filename = step.get("screenshot")
    if filename:
        alt = esc_attr(os.path.splitext(str(filename))[0])
        screenshot = SCREENSHOT.format(file=esc_attr(filename), alt=alt)
    cls = ' class="human-step"' if step.get("human") else ""
    return STEP_LI.format(cls=cls, text=text, screenshot=screenshot)


def render_step_list(steps):
    items = "\n".join(render_step(step) for step in steps)
    return f"<ol>\n{items}\n</ol>"


def render_case(case, tc_template):
    url_block = ""
    if case.get("url"):
        url_block = f"<p><strong>URL</strong>: <code>{esc(case['url'])}</code></p>"
    setup_block = ""
    if case.get("setup_steps"):
        setup_block = "<p><strong>Setup Steps</strong>:</p>\n" + render_step_list(
            case["setup_steps"]
        )
    notes_block = ""
    if case.get("notes"):
        notes_block = f"<p><strong>Notes</strong>: {esc(case['notes'])}</p>"
    return fill(
        tc_template,
        NUMBER=esc(case.get("number")),
        NAME=esc(case.get("name")),
        STATUS=STATUS_DISPLAY[case["status"]],
        URL_BLOCK=url_block,
        SETUP_BLOCK=setup_block,
        TEST_STEPS=render_step_list(case.get("test_steps", [])),
        NOTES_BLOCK=notes_block,
    )


def render_issues(cases):
    items = []
    for case in cases:
        if case["status"] in ("FAIL", "ERROR"):
            emoji = ISSUE_EMOJI[case["status"]]
            desc = esc(case.get("notes") or case.get("name"))
            items.append(f"<li>{emoji} Test Case {esc(case.get('number'))}: {desc}</li>")
    if not items:
        return "<p><em>All test cases passed.</em></p>"
    return "<ul>\n" + "\n".join(items) + "\n</ul>"


def render_recommendations(cases):
    items = []
    for case in cases:
        if case["status"] in ("FAIL", "ERROR"):
            items.append(
                f"<li>Fix: Test Case {esc(case.get('number'))} ({esc(case.get('name'))})</li>"
            )
    for case in cases:
        if case["status"] == "PASS (adaptive)":
            adaptive = case.get("adaptive") or {}
            items.append(
                f"<li>Update test plan: TC{esc(case.get('number'))} asserted "
                f"{esc(adaptive.get('specified'))}, actual rendering is "
                f"{esc(adaptive.get('found'))}. Update the assertion in the test plan to match.</li>"
            )
    if any(case["status"] in ("FAIL", "ERROR") for case in cases):
        items.append("<li>Re-test after applying the fixes above.</li>")
    if not items:
        return "<p><em>No follow-up actions.</em></p>"
    return "<ul>\n" + "\n".join(items) + "\n</ul>"


def render(data, header):
    cases = data["cases"]
    totals = tally(cases)
    shell = read_template(header["template_dir"], "report.html")
    tc_template = read_template(header["template_dir"], "test-case.html")
    test_cases_html = "\n".join(render_case(case, tc_template) for case in cases)
    return fill(
        shell,
        PLAN_NAME=esc(header["plan_name"]),
        DATE=esc(header["date"]),
        SLUG=esc(header["slug"]),
        SERVICES_TESTED=esc(header["services_tested"]),
        BASE_URL=esc(header["base_url"]),
        TOTAL=esc(totals["total"]),
        PASSED=esc(totals["passed"]),
        ADAPTIVE=esc(totals["adaptive"]),
        FAILED=esc(totals["failed"]),
        ERRORED=esc(totals["errored"]),
        TEST_CASES=test_cases_html,
        ISSUES_SUMMARY=render_issues(cases),
        RECOMMENDATIONS=render_recommendations(cases),
    )


def main(argv):
    parser = argparse.ArgumentParser(description="Render a Playwright test report as HTML.")
    parser.add_argument("--results", required=True)
    parser.add_argument("--template-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--plan-name", required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--services-tested", required=True)
    parser.add_argument("--base-url", required=True)
    args = parser.parse_args(argv)

    data = load_results(args.results)
    if data["run_status"] == "aborted":
        print(
            "render_report: aborted runs have no report; caller should skip rendering",
            file=sys.stderr,
        )
        return 2

    header = {
        "template_dir": args.template_dir,
        "plan_name": args.plan_name,
        "date": args.date,
        "slug": args.slug,
        "services_tested": args.services_tested,
        "base_url": args.base_url,
    }
    document = render(data, header)
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(document)
    print(f"report written: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
