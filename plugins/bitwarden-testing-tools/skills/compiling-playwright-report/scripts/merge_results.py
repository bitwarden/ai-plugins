#!/usr/bin/env python3
# merge_results.py - Assemble the canonical Bitwarden Playwright results JSON
# from one or more playwright-test-runner segment files. Concatenates the per-segment
# cases in order, derives the run totals from the per-case statuses, validates
# the result, and writes it out. Stdlib only.
#
# Usage:
#   merge_results.py <segment.json> [<segment.json> ...] --output <path>
#
# The run_status of the assembled result is that of the LAST segment
# (complete | paused | aborted). Cases are concatenated across ALL segments
# regardless of the last segment's status, so an aborted resume still reports
# the work earlier segments completed. For a paused result, need_user_input is
# carried forward from the last segment, along with need_user_input_url when
# that segment supplied one as a string; for an aborted result, abort_reason is,
# along with error_details when that segment supplied a list.
# Totals are derived, never trusted from the runner.
#
# A case that recorded no setup or test steps was not run; its number is
# appended to the stdout summary as "| not_run=<n>[,<n>...]". A later segment
# may carry the same case number again to replace a not-run entry in place;
# repeating a case number whose earlier entry ran is an error.
#
# Exit codes: 0 written; 2 usage error; 3 invalid or malformed segment JSON,
# or a repeated case number whose earlier entry ran.

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
    cases = data.get("cases", [])
    if not isinstance(cases, list) or not all(isinstance(case, dict) for case in cases):
        fail(f"segment {path} 'cases' must be a list of objects")
    return data


def was_run(case):
    """A case ran when it recorded at least one setup or test step."""
    return bool(case.get("setup_steps")) or bool(case.get("test_steps"))


def not_run(cases):
    """Return the numbers of the cases that recorded no steps at all."""
    return [case.get("number") for case in cases if not was_run(case)]


def merge(segments):
    """Concatenate cases across every segment and take the last segment's status.

    An aborted last segment does NOT discard earlier segments. A run splits into
    segments at each [HUMAN] pause, and a resumed playwright-test-runner legitimately emits
    aborted when it cannot re-authenticate, having no memory of earlier segments.
    Dropping cases here silently threw away completed work and left the run with
    no report at all.

    A case number seen again in a later segment replaces the earlier entry in
    place, but only when that entry was not run, so re-running a skipped case
    never overwrites a real result. Any other repeat is rejected.
    """
    last = segments[-1]
    run_status = last["run_status"]
    cases = []
    position = {}
    for segment in segments:
        for case in segment.get("cases", []):
            number = case.get("number")
            if number in position:
                index = position[number]
                if was_run(cases[index]):
                    fail(f"case {number} appears more than once and its earlier entry ran")
                cases[index] = case
                continue
            if number is not None:
                position[number] = len(cases)
            cases.append(case)
    result = {"run_status": run_status, "totals": tally(cases), "cases": cases}
    if run_status == "aborted":
        result["abort_reason"] = last.get("abort_reason", "")
        if isinstance(last.get("error_details"), list):
            result["error_details"] = last["error_details"]
    if run_status == "paused":
        result["need_user_input"] = last.get("need_user_input", "")
        if isinstance(last.get("need_user_input_url"), str):
            result["need_user_input_url"] = last["need_user_input_url"]
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
    summary = (
        f"run_status={result['run_status']} | {totals['total']} total | "
        f"{totals['passed']} passed | {totals['adaptive']} passed (adaptive) | "
        f"{totals['failed']} failed | {totals['errored']} errored"
    )
    skipped = not_run(result["cases"])
    if skipped:
        summary += " | not_run=" + ",".join(str(number) for number in skipped)
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
