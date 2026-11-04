#!/usr/bin/env python3
# render_report.py - Render a Bitwarden Playwright test report as HTML from the
# canonical results JSON. Deterministic and dependency-free (stdlib only).
# Every interpolated value is HTML-escaped by this script (esc for body text,
# esc_linked for body text that may hold URLs, esc_attr for attribute values);
# the template markup the script owns is never escaped.
#
# Usage:
#   render_report.py --results <path> --template-dir <dir> --output <path>
#     --plan-name <str> --date <str> --slug <str> --services-tested <str>
#     --base-url <str> --plan-file <path> [--context-file <path>]
#
# --context-file is the context artifact; its **Title:** line becomes the
# report's headline. It is optional, and a missing title is not an error.
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

STATUS_META = {
    "PASS": ("pass", "Passed"),
    "PASS (adaptive)": ("adaptive", "Passed (adaptive)"),
    "FAIL": ("fail", "Failed"),
    "ERROR": ("error", "Error"),
}
STATUS_VALUES = set(STATUS_META)

SVG = '<svg viewBox="0 0 20 20" aria-hidden="true">{}</svg>'
ICON_CHECK = '<path d="M5 10.5l3.2 3.2L15 7" />'
ICON_X = '<path d="M6 6l8 8M14 6l-8 8" />'
ICON_BANG = '<path d="M10 5.5v5.5M10 14.2v.3" />'
ICON_HUMAN = '<circle cx="10" cy="7" r="2.6" /><path d="M5 15.5c.8-2.6 2.7-3.8 5-3.8s4.2 1.2 5 3.8" />'
STATUS_ICON = {"pass": ICON_CHECK, "adaptive": ICON_CHECK, "fail": ICON_X, "error": ICON_BANG}

# A run's progress ring and count tiles, in the order they are drawn.
RING_SEGMENTS = (("passed", "pass"), ("adaptive", "adaptive"), ("failed", "fail"), ("errored", "error"))
TILES = (
    ("total", "all", "Total"),
    ("passed", "pass", "Passed"),
    ("adaptive", "adaptive", "Adaptive"),
    ("failed", "fail", "Failed"),
    ("errored", "error", "Errors"),
)

URL_RE = re.compile(r"https?://[^\s<>\"']+")
URL_TRAILING_PUNCTUATION = ".,;:!?)]}"
# A route placeholder such as /:organizationId means the URL was never resolved.
URL_PLACEHOLDER_RE = re.compile(r"/:[A-Za-z_]")
CONTEXT_START = "<!-- CONTEXT START -->"
CONTEXT_END = "<!-- CONTEXT END -->"
TITLE_LINE_RE = re.compile(r"^\*\*Title:\*\*[ \t]*(.+)$", re.MULTILINE)
TITLE_MAX_LENGTH = 120
TIMESTAMP_RE = re.compile(r"^(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})$")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def esc(value):
    # Escape a raw-text leaf for element-body context (&, <, >).
    return html.escape("" if value is None else str(value), quote=False)


def esc_attr(value):
    # Escape a raw-text leaf destined for an attribute value (also quotes).
    return html.escape("" if value is None else str(value), quote=True)


def esc_linked(value):
    # Escape raw text for element-body context, turning each http(s) URL in it
    # into a link that opens in a new tab. Only text matching URL_RE becomes an
    # href, so no other scheme can reach one. A URL with an unresolved route
    # placeholder stays plain text, since a link to it would go nowhere.
    text = "" if value is None else str(value)
    pieces = []
    position = 0
    for match in URL_RE.finditer(text):
        url = match.group(0).rstrip(URL_TRAILING_PUNCTUATION)
        if not url or URL_PLACEHOLDER_RE.search(url):
            continue
        pieces.append(esc(text[position : match.start()]))
        pieces.append(f'<a href="{esc_attr(url)}" target="_blank" rel="noopener noreferrer">{esc(url)}</a>')
        position = match.start() + len(url)
    pieces.append(esc(text[position:]))
    return "".join(pieces)


def fill(template, **tokens):
    # Replace each {{TOKEN}} in the template exactly once; substituted values
    # are never re-scanned, so untrusted text cannot forge another token.
    return re.sub(
        r"\{\{(\w+)\}\}",
        lambda m: tokens.get(m.group(1), m.group(0)),
        template,
    )


def format_date(raw):
    # The orchestrator passes a YYYYMMDD-HHmm timestamp; show it as
    # "Oct 5, 2026 · 4:53 PM". Any other shape is shown as given.
    match = TIMESTAMP_RE.match(str(raw))
    if not match:
        return str(raw)
    year, month, day, hour, minute = (int(part) for part in match.groups())
    if not (1 <= month <= 12 and 1 <= day <= 31 and hour < 24 and minute < 60):
        return str(raw)
    suffix = "AM" if hour < 12 else "PM"
    return f"{MONTHS[month - 1]} {day}, {year} \u00b7 {hour % 12 or 12}:{minute:02d} {suffix}"


def read_title(context_path):
    # The run's one-line title comes from the context artifact's `**Title:**`
    # line, read here rather than passed on the command line, because the
    # artifact is distilled from untrusted feature source. Located by the first
    # START and last END marker, so an embedded marker cannot truncate it. The
    # title is cosmetic: a missing file, fence, or line yields no title.
    try:
        with open(context_path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError as err:
        print(f"render_report: warning: cannot read context file, no title: {err}", file=sys.stderr)
        return None
    start = text.find(CONTEXT_START)
    end = text.rfind(CONTEXT_END)
    if start == -1 or end <= start:
        return None
    match = TITLE_LINE_RE.search(text[start + len(CONTEXT_START) : end])
    if not match:
        return None
    title = " ".join(match.group(1).split())
    if len(title) > TITLE_MAX_LENGTH:
        title = title[: TITLE_MAX_LENGTH - 1].rstrip() + "\u2026"
    return title or None


def validate(data):
    if not isinstance(data, dict):
        fail("results root must be a JSON object")
    status = data.get("run_status")
    if status not in ("complete", "aborted"):
        fail(f"run_status must be 'complete' or 'aborted' to render, got {status!r}")
    if status == "aborted" and not data.get("cases"):
        # An aborted run with no cases is legitimate (setup failed before any
        # case ran). One WITH cases is a resumed run whose later segment
        # aborted, and its cases must be validated like any other.
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
        if not isinstance(stored, dict):
            fail("'totals' must be a JSON object")
        for key, value in counted.items():
            try:
                stored_value = int(stored.get(key, -1))
            except (TypeError, ValueError):
                fail(f"totals.{key} is not an integer: {stored.get(key)!r}")
            if stored_value != value:
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


def plural(count, noun):
    return f"{count} {noun}{'' if count == 1 else 's'}"


def step_kind(step):
    if step.get("human"):
        return "human"
    return {"PASS": "pass", "FAIL": "fail"}.get(step.get("outcome"), "neutral")


def render_pill(step, kind):
    if kind == "neutral":
        return f'<span class="pill pill-neutral">{esc(step.get("outcome") or "-")}</span>'
    label = {"pass": "Pass", "fail": "Fail", "human": "Human"}[kind]
    icon = {"pass": ICON_CHECK, "fail": ICON_X, "human": ICON_HUMAN}[kind]
    return f'<span class="pill pill-{kind}">{SVG.format(icon)}{label}</span>'


def render_error_entry(entry):
    request_line = esc(entry["request"])
    if entry.get("status") is not None:
        request_line += esc(f' → {entry["status"]} {entry.get("status_text") or ""}'.rstrip())
    count = entry.get("count")
    if isinstance(count, int) and not isinstance(count, bool) and count > 1:
        request_line += f" (×{count})"
    lines = [f'<span class="error-details-req">{request_line}</span>']
    if entry.get("message"):
        lines.append(esc_linked(entry["message"]))
    validation = entry.get("validation_errors")
    if isinstance(validation, dict):
        for field, messages in validation.items():
            if isinstance(messages, list) and all(isinstance(m, str) for m in messages):
                lines.extend(f"{esc(field)}: {esc_linked(m)}" for m in messages)
    if entry.get("exception_message"):
        lines.append(esc_linked(entry["exception_message"]))
    if entry.get("inner_exception_message"):
        lines.append("Inner: " + esc_linked(entry["inner_exception_message"]))
    stack = entry.get("stack_trace")
    stack_html = ""
    if isinstance(stack, str) and stack.strip():
        frames = sum(1 for line in stack.splitlines() if line.strip().startswith("at "))
        stack_html = (
            f'<details class="error-details-stack"><summary>Stack trace ({plural(frames, "frame")})</summary>'
            f"<pre>{esc(stack)}</pre></details>"
        )
    return f'<div class="error-details-box">{"<br />".join(lines)}{stack_html}</div>'


def render_error_details(entries, failed):
    # Server error text the runner captured for a 4xx/5xx response. It is
    # diagnostic only: red on a failed step, amber otherwise. Malformed entries
    # are skipped rather than failing the render.
    if not isinstance(entries, list):
        return ""
    boxes = [
        render_error_entry(entry)
        for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("request"), str)
    ]
    if not boxes:
        return ""
    tone = "fail" if failed else "warn"
    return (
        f'<div class="error-details error-details-{tone}"><span class="error-details-label">Error details</span>'
        f'{"".join(boxes)}</div>'
    )


def render_step(step, number):
    kind = step_kind(step)
    parts = [
        f'<li class="step step-{kind}"><span class="step-num">{number}</span><div class="step-body">',
        f'<div class="step-head"><span class="step-text">{esc_linked(step.get("text", ""))}</span>'
        f"{render_pill(step, kind)}</div>",
    ]
    if kind == "human" and step.get("outcome"):
        parts.append(f'<p class="human-answer">{esc_linked(step["outcome"])}</p>')
    observed = step.get("observed")
    if observed:
        label = "Observed (mismatch)" if kind == "fail" else "Observed"
        parts.append(
            f'<div class="observed"><span class="observed-label">{label}</span>'
            f"<code>{esc_linked(observed)}</code></div>"
        )
    parts.append(render_error_details(step.get("error_details"), kind == "fail"))
    filename = step.get("screenshot")
    if filename:
        alt = esc_attr(os.path.splitext(str(filename))[0])
        parts.append(
            f'<a class="thumb" href="screenshots/{esc_attr(filename)}" target="_blank" rel="noopener">'
            f'<img src="screenshots/{esc_attr(filename)}" alt="Screenshot: {alt}" loading="lazy" />'
            f'<span class="thumb-cap">{esc(filename)} &#8599;</span></a>'
        )
    parts.append("</div></li>")
    return "".join(parts)


def render_step_list(steps):
    items = "\n".join(render_step(step, number) for number, step in enumerate(steps, start=1))
    return f'<ol class="steps">\n{items}\n</ol>'


def render_case(case, tc_template):
    status_class, status_label = STATUS_META[case["status"]]
    setup_steps = case.get("setup_steps") or []
    test_steps = case.get("test_steps") or []
    url_block = ""
    if case.get("url"):
        url_block = f'<p class="url"><span>URL</span><code>{esc_linked(case["url"])}</code></p>'
    callout_block = ""
    adaptive = case.get("adaptive")
    if case["status"] == "PASS (adaptive)" and isinstance(adaptive, dict):
        callout_block = (
            '<div class="callout callout-adaptive"><strong>Adaptive pass</strong><dl>'
            f"<dt>Plan specified</dt><dd>{esc(adaptive.get('specified'))}</dd>"
            f"<dt>Runner found</dt><dd>{esc(adaptive.get('found'))}</dd></dl></div>"
        )
    setup_block = ""
    if setup_steps:
        # A failed setup step is why the case failed, so show it without a click.
        opened = " open" if any(step.get("outcome") == "FAIL" for step in setup_steps) else ""
        setup_block = (
            f'<details class="sub"{opened}><summary>Setup steps '
            f'<span class="sub-count">{len(setup_steps)}</span></summary>'
            f"{render_step_list(setup_steps)}</details>"
        )
    test_steps_block = (
        f'<h4 class="section-label">Test steps <span class="sub-count">{len(test_steps)}</span></h4>'
        + (render_step_list(test_steps) if test_steps else '<p class="muted">No test steps were recorded.</p>')
    )
    notes_block = ""
    if case.get("notes"):
        notes_block = (
            f'<div class="notes"><span class="notes-label">Notes</span><p>{esc_linked(case["notes"])}</p></div>'
        )
    step_counts = f"{len(setup_steps)} setup &middot; {plural(len(test_steps), 'test step')}"
    failed_steps = sum(1 for step in setup_steps + test_steps if step.get("outcome") == "FAIL")
    if failed_steps:
        step_counts += f' &middot; <b class="t-fail">{failed_steps} failed</b>'
    return fill(
        tc_template,
        NUMBER=esc_attr(case.get("number")),
        NAME=esc(case.get("name")),
        STATUS_CLASS=status_class,
        STATUS_LABEL=status_label,
        STATUS_ICON=STATUS_ICON[status_class],
        STEP_COUNTS=step_counts,
        URL_BLOCK=url_block,
        CALLOUT_BLOCK=callout_block,
        SETUP_BLOCK=setup_block,
        TEST_STEPS_BLOCK=test_steps_block,
        NOTES_BLOCK=notes_block,
    )


def issue_detail(case):
    if case.get("notes"):
        return case["notes"]
    for step in (case.get("setup_steps") or []) + (case.get("test_steps") or []):
        if step.get("outcome") == "FAIL":
            detail = step.get("text", "")
            if step.get("observed"):
                detail += f" - observed: {step['observed']}"
            return detail
    return ""


def render_issues(cases):
    items = []
    for case in cases:
        if case["status"] in ("FAIL", "ERROR"):
            status_class = STATUS_META[case["status"]][0]
            number = esc_attr(case.get("number"))
            detail = issue_detail(case)
            detail_html = f"<p>{esc_linked(detail)}</p>" if detail else ""
            items.append(
                f'<li class="issue issue-{status_class}">'
                f'<span class="badge badge-{status_class} badge-sm">{SVG.format(STATUS_ICON[status_class])}</span>'
                f'<div><a href="#case-{number}">Test Case {number}: {esc(case.get("name"))}</a>{detail_html}</div></li>'
            )
    if not items:
        return '<p class="muted">All test cases passed.</p>'
    return '<ul class="issues">\n' + "\n".join(items) + "\n</ul>"


def render_recommendations(cases):
    items = []
    for case in cases:
        if case["status"] in ("FAIL", "ERROR"):
            number = esc_attr(case.get("number"))
            items.append(
                f'<li>Fix: <a href="#case-{number}">Test Case {number}</a> ({esc(case.get("name"))})</li>'
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
        return '<p class="muted">No follow-up actions.</p>'
    return '<ul class="recs">\n' + "\n".join(items) + "\n</ul>"


def render_services(services_tested):
    services = [part.strip() for part in str(services_tested).split(",") if part.strip()]
    if not services:
        return esc(services_tested)
    return "".join(f'<span class="chip">{esc(service)}</span>' for service in services)


def render_tiles(totals):
    tiles = []
    for key, status_class, label in TILES:
        zero = " tile-zero" if totals[key] == 0 else ""
        tiles.append(
            f'<label class="tile tile-{status_class}{zero}" for="f-{status_class}">'
            f'<span class="tile-n">{totals[key]}</span><span class="tile-l">{label}</span></label>'
        )
    return "".join(tiles)


def ring_style(totals):
    # Conic-gradient stops for the pass-rate ring, one arc per non-empty status.
    total = totals["total"]
    if not total:
        return "background: rgba(140, 175, 235, 0.16)"
    stops = []
    start = 0.0
    for key, status_class in RING_SEGMENTS:
        if not totals[key]:
            continue
        end = start + 100.0 * totals[key] / total
        stops.append(f"var(--{status_class}) {start:.2f}% {end:.2f}%")
        start = end
    return "background: conic-gradient(" + ", ".join(stops) + ")"


def render_verdict(totals, aborted):
    # Returns (hero class, icon, text) for the headline of the summary card.
    if aborted:
        return "error", ICON_BANG, "Run aborted"
    if totals["failed"]:
        return "fail", ICON_X, "Run has failures"
    if totals["errored"]:
        return "error", ICON_BANG, "Run had errors"
    if not totals["total"]:
        return "error", ICON_BANG, "No test cases ran"
    return "pass", ICON_CHECK, "All tests passed"


def render_summary_line(totals, date):
    cases = plural(totals["total"], "test case")
    problems = []
    if totals["failed"]:
        problems.append(f"{totals['failed']} failed")
    if totals["errored"]:
        problems.append(plural(totals["errored"], "error"))
    if problems:
        summary = ", ".join(problems) + f" across {cases}"
    elif totals["total"]:
        summary = f"No failures across {cases}"
    else:
        summary = "No test cases"
    return esc(f"{summary} \u00b7 {format_date(date)}")


def render_heading(plan_name, title):
    if title:
        return f'<div class="hero-key">{esc(plan_name)}</div><h1>{esc(title)}</h1>'
    return f"<h1>{esc(plan_name)}</h1>"


def render(data, header):
    cases = data["cases"]
    totals = tally(cases)
    shell = read_template(header["template_dir"], "report.html")
    tc_template = read_template(header["template_dir"], "test-case.html")
    test_cases_html = "\n".join(render_case(case, tc_template) for case in cases)
    aborted = data.get("run_status") == "aborted"
    abort_block = ""
    if aborted:
        abort_block = (
            '<div class="abort-banner"><p><strong>Run aborted</strong>: '
            f'{esc_linked(data.get("abort_reason", ""))}<br />'
            "The test cases below completed before the run was aborted.</p>"
            f'{render_error_details(data.get("error_details"), True)}</div>'
        )
    hero_class, verdict_icon, verdict_text = render_verdict(totals, aborted)
    passed_or_adaptive = totals["passed"] + totals["adaptive"]
    # Floor, not round: a run with any failure must never read 100%.
    pass_percent = 100 * passed_or_adaptive // totals["total"] if totals["total"] else 0
    return fill(
        shell,
        PLAN_NAME=esc(header["plan_name"]),
        DATE=esc(format_date(header["date"])),
        SLUG=esc(header["slug"]),
        SERVICES_TESTED=render_services(header["services_tested"]),
        BASE_URL=esc_linked(header["base_url"]),
        PLAN_FILE=esc(header["plan_file"]),
        ABORT_BLOCK=abort_block,
        HERO_CLASS=hero_class,
        RING_STYLE=ring_style(totals),
        PASS_PERCENT=str(pass_percent),
        PASS_CAPTION=f"{passed_or_adaptive} of {totals['total']} passed",
        VERDICT_ICON=verdict_icon,
        VERDICT_TEXT=verdict_text,
        HERO_HEADING=render_heading(header["plan_name"], header.get("title")),
        HERO_SUMMARY=render_summary_line(totals, header["date"]),
        TILES=render_tiles(totals),
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
    parser.add_argument("--plan-file", required=True)
    parser.add_argument("--context-file")
    args = parser.parse_args(argv)

    data = load_results(args.results)
    if data["run_status"] == "aborted" and not data.get("cases"):
        print(
            "render_report: aborted run has no cases; caller should skip rendering",
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
        "plan_file": args.plan_file,
        "title": read_title(args.context_file) if args.context_file else None,
    }
    document = render(data, header)
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(document)
    print(f"report written: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
