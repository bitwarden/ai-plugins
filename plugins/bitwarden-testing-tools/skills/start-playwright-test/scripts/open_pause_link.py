#!/usr/bin/env python3
"""Open the link from a paused test run in the user's default browser.

The orchestrator calls this instead of running `open` or `xdg-open` itself, so
the skill's `allowed-tools` grant is scoped to this one script rather than to
an opener that would accept any file, URL, or application. The script decides
what may be opened, so the grant's trailing wildcard cannot widen it. The link
comes from the runner's `need_user_input_url`, which is derived from Stripe
data, so it is checked here even though the orchestrator checks it too.

Usage:
  open_pause_link.py <url>

<url> is opened only when the whole string is a Stripe test-mode subscription
page: https://dashboard.stripe.com/test/subscriptions/sub_<letters and digits>,
with no query string, fragment, or extra path. To allow another kind of link,
widen LINK_REGEX here and the matching pattern in SKILL.md together.

The opener is chosen by platform: `open` on macOS, `xdg-open` on Linux. It runs
as a fixed argument list, never through a shell. On any other platform, or on
Linux without `xdg-open`, nothing is opened and the link stays in the
orchestrator's message for the user to click.

Exit codes: 0 the link was handed to the opener; 1 the opener failed; 2 usage
error or the link was refused; 3 skipped, because no opener is available on
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

LINK_REGEX = r"https://dashboard\.stripe\.com/test/subscriptions/sub_[A-Za-z0-9]+"
LINK_PATTERN = re.compile(LINK_REGEX)
OPENERS = {"darwin": "open", "linux": "xdg-open"}
OPENER_TIMEOUT_SECONDS = 10


def find_opener(platform, which):
    """Return the opener command for this platform, or None when there is none."""
    name = OPENERS.get(platform)
    if name is None:
        return None
    return which(name)


def main(argv, platform=sys.platform, which=shutil.which, run=subprocess.run):
    if len(argv) != 1:
        print("usage: open_pause_link.py <url>", file=sys.stderr)
        return EXIT_REFUSED

    link = argv[0]
    if not LINK_PATTERN.fullmatch(link):
        print(
            "open_pause_link.py: refusing to open: the link is not a Stripe test-mode "
            "subscription page",
            file=sys.stderr,
        )
        return EXIT_REFUSED

    opener = find_opener(platform, which)
    if opener is None:
        print(f"open_pause_link.py: skipped: no browser opener is available on {platform}")
        return EXIT_SKIPPED

    try:
        completed = run([opener, link], timeout=OPENER_TIMEOUT_SECONDS, check=False)
    except (OSError, subprocess.TimeoutExpired) as err:
        print(f"open_pause_link.py: {os.path.basename(opener)} failed: {err}", file=sys.stderr)
        return EXIT_OPENER_FAILED
    if completed.returncode != 0:
        print(
            f"open_pause_link.py: {os.path.basename(opener)} exited {completed.returncode}",
            file=sys.stderr,
        )
        return EXIT_OPENER_FAILED
    print(f"Opened {link}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
