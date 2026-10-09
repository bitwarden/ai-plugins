#!/usr/bin/env python3
"""Open a start-playwright-test HTML report in the user's default browser.

The orchestrator calls this instead of running `open` or `xdg-open` itself, so
the skill's `allowed-tools` grant is scoped to this one script rather than to
an opener that would accept any file, URL, or application. The script decides
what may be opened, so the grant's trailing wildcard cannot widen it.

Usage:
  open_report.py <report-path>

<report-path> is absolute or relative to the current working directory (the
bitwarden root, where the pipeline runs). The report is opened only when its
real path, with `..` and symlinks resolved, is
<cwd>/.playwright-testing-artifacts/<slug>/report-YYYYMMDD-HHmm.html, and the
path given is a regular file rather than a symlink.

The opener is chosen by platform: `open` on macOS, `xdg-open` on Linux. It runs
as a fixed argument list, never through a shell. On any other platform, or on
Linux without `xdg-open`, nothing is opened and the report path stays in the
orchestrator's final summary for the user to open.

Exit codes: 0 the report was handed to the opener; 1 the opener failed; 2 usage
error or the path was refused; 3 skipped, because no opener is available on
this platform.
"""
import os
import re
import shutil
import subprocess
import sys

EXIT_OK = 0
EXIT_OPENER_FAILED = 1
EXIT_REFUSED = 2
EXIT_SKIPPED = 3

ARTIFACTS_DIR_NAME = ".playwright-testing-artifacts"
REPORT_NAME_PATTERN = re.compile(r"report-\d{8}-\d{4}\.html")
OPENERS = {"darwin": "open", "linux": "xdg-open"}
OPENER_TIMEOUT_SECONDS = 10


class Refused(Exception):
    """The path is not a report this script may open."""


def resolve_report(path, cwd):
    """Return the report's real path, or raise Refused naming the failed check."""
    given = os.path.join(cwd, path)
    if not REPORT_NAME_PATTERN.fullmatch(os.path.basename(given)):
        raise Refused(f"{path} is not named report-YYYYMMDD-HHmm.html")
    if os.path.islink(given):
        raise Refused(f"{path} is a symlink")
    if not os.path.isfile(given):
        raise Refused(f"{path} is not an existing file")
    real = os.path.realpath(given)
    artifacts_root = os.path.realpath(os.path.join(cwd, ARTIFACTS_DIR_NAME))
    slug_dir = os.path.dirname(real)
    if os.path.dirname(slug_dir) != artifacts_root:
        raise Refused(
            f"{path} is not directly inside a run folder under "
            f"{os.path.join(cwd, ARTIFACTS_DIR_NAME)}"
        )
    return real


def find_opener(platform, which):
    """Return the opener command for this platform, or None when there is none."""
    name = OPENERS.get(platform)
    if name is None:
        return None
    return which(name)


def main(argv, cwd=None, platform=sys.platform, which=shutil.which, run=subprocess.run):
    if len(argv) != 1:
        print("usage: open_report.py <report-path>", file=sys.stderr)
        return EXIT_REFUSED
    cwd = os.getcwd() if cwd is None else cwd

    try:
        report = resolve_report(argv[0], cwd)
    except Refused as err:
        print(f"open_report.py: refusing to open: {err}", file=sys.stderr)
        return EXIT_REFUSED

    opener = find_opener(platform, which)
    if opener is None:
        print(f"open_report.py: skipped: no browser opener is available on {platform}")
        return EXIT_SKIPPED

    try:
        completed = run([opener, report], timeout=OPENER_TIMEOUT_SECONDS, check=False)
    except (OSError, subprocess.TimeoutExpired) as err:
        print(f"open_report.py: {os.path.basename(opener)} failed: {err}", file=sys.stderr)
        return EXIT_OPENER_FAILED
    if completed.returncode != 0:
        print(
            f"open_report.py: {os.path.basename(opener)} exited {completed.returncode}",
            file=sys.stderr,
        )
        return EXIT_OPENER_FAILED
    print(f"Opened {report}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
