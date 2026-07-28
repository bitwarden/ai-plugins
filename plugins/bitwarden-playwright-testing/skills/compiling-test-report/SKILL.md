---
name: compiling-test-report
description: Deterministic HTML report rendering for Bitwarden Playwright web tests. Home of render_report.py (results JSON to HTML) and merge_results.py (runner segments to canonical results JSON), the report templates, the JSON results-schema reference, and their unit tests. The test-web-changes orchestrator runs these scripts directly; there is no report-compiler agent.
---

This skill is the home for the deterministic report pipeline. It contains no LLM assembly instructions; the two scripts do the parsing, escaping, and rendering.

## Contract

The results JSON contract is defined in `references/results-schema.md`, with concrete examples in `references/examples/`. Those examples are the producer's reference (see `executing-web-tests`) and the scripts' golden test fixtures.

## Scripts

Both are stdlib-only Python, executable, and invoked by absolute path. They share `scripts/results_common.py` (the `fail` and `tally` helpers), which is imported, not invoked directly.

- `scripts/merge_results.py <segment.json> [<segment.json> ...] --output <path>`: assembles one or more runner segment files into the canonical results JSON, deriving totals from the per-case statuses. `run_status` follows the last segment. A paused result carries `need_user_input`; an aborted last segment yields an aborted run with no cases. Prints a `run_status=... | N total | ...` summary line to stdout.
- `scripts/render_report.py --results <path> --template-dir <dir> --output <path> --plan-name <str> --date <str> --slug <str> --services-tested <str> --base-url <str>`: renders the canonical results JSON to an HTML report, writing the file directly. Every interpolated value is HTML-escaped by the script; template markup is not. Exits 2 on an aborted run (the caller skips rendering) and 3 on invalid results JSON.

## Templates

`templates/report.html` is the shell (head, styles, header, summary table, and the `{{TEST_CASES}}`, `{{ISSUES_SUMMARY}}`, `{{RECOMMENDATIONS}}` tokens). `templates/test-case.html` is one case. The document shell and the per-case structure live in these templates; the script composes the repeating pieces (each step `<li>`, its screenshot thumbnail, and the Issues Summary and Recommendations lists) as small HTML fragments, escaping every interpolated value.

## Tests

`scripts/tests/test_results_common.py`, `scripts/tests/test_render_report.py`, and `scripts/tests/test_merge_results.py` run with `python3 -m unittest discover -s scripts/tests` from the skill directory. They cover the shared helpers, rendering fidelity, HTML-escaping of malicious payloads, validation and invariant failures, and segment merge.
