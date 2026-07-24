#!/usr/bin/env python3
# merge_results.py - Assemble the canonical Bitwarden Playwright results JSON
# from one or more test-runner segment files. Concatenates the per-segment
# cases in order, derives the run totals from the per-case statuses, validates
# the result, and writes it out. Stdlib only.
#
# Usage:
#   merge_results.py <segment.json> [<segment.json> ...] --output <path>
#
# The run_status of the assembled result is that of the LAST segment
# (complete | paused | aborted). For a paused result, need_user_input is
# carried forward from the last segment. Totals are derived, never trusted
# from the runner. A single segment is validated and tallied (passthrough).
#
# Exit codes: 0 written; 2 usage error; 3 invalid or malformed segment JSON.

import argparse
import json
import sys

from results_common import fail, tally

VALID_RUN_STATUS = {"complete", "paused", "aborted"}


def load_segment(path):
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        fail(f"segment file not found: {path}")
    except json.JSONDecodeError as err:
        fail(f"segment {path} is not valid JSON: {err}")
    if not isinstance(data, dict):
        fail(f"segment {path} root must be a JSON object")
    run_status = data.get("run_status")
    if run_status not in VALID_RUN_STATUS:
        fail(
            f"segment {path} run_status must be one of "
            f"{sorted(VALID_RUN_STATUS)}, got {run_status!r}"
        )
    return data


def merge(segments):
    last = segments[-1]
    run_status = last["run_status"]
    if run_status == "aborted":
        return {
            "run_status": "aborted",
            "abort_reason": last.get("abort_reason", ""),
            "totals": tally([]),
            "cases": [],
        }
    cases = []
    for segment in segments:
        cases.extend(segment.get("cases", []))
    result = {"run_status": run_status, "totals": tally(cases), "cases": cases}
    if run_status == "paused":
        result["need_user_input"] = last.get("need_user_input", "")
    return result


def main(argv):
    parser = argparse.ArgumentParser(description="Assemble Playwright results JSON from segments.")
    parser.add_argument("segments", nargs="+")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    segments = [load_segment(path) for path in args.segments]
    result = merge(segments)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    totals = result["totals"]
    print(
        f"run_status={result['run_status']} | {totals['total']} total | "
        f"{totals['passed']} passed | {totals['adaptive']} passed (adaptive) | "
        f"{totals['failed']} failed | {totals['errored']} errored"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
