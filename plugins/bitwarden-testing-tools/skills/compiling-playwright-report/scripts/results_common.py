#!/usr/bin/env python3
# results_common.py - Helpers shared by the Bitwarden Playwright report scripts
# (render_report.py and merge_results.py). Stdlib only. Imported by both scripts;
# never invoked directly, so it needs no shebang execute bit.

import sys

STATUS_BUCKET = {
    "PASS": "passed",
    "PASS (adaptive)": "adaptive",
    "FAIL": "failed",
    "ERROR": "errored",
}


def fail(msg):
    print(f"results: ERROR: {msg}", file=sys.stderr)
    sys.exit(3)


def tally(cases):
    counts = {"total": len(cases), "passed": 0, "adaptive": 0, "failed": 0, "errored": 0}
    for case in cases:
        status = case.get("status")
        if status not in STATUS_BUCKET:
            fail(f"case {case.get('number')} has invalid status {status!r}")
        counts[STATUS_BUCKET[status]] += 1
    return counts
