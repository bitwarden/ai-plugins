#!/usr/bin/env python3
"""Policy-guarded Stripe CLI access for the bitwarden-testing-tools plugin.
The only sanctioned way for a skill or automated test run to reach Stripe.

A Bash grant of the shape Bash(stripe get:*) cannot exclude a flag, so it can
never block --live; the official permissions documentation calls
argument-constraining patterns fragile for exactly this reason. This wrapper
moves the control to the transport: every argv is built from scratch and no
caller-supplied flag is ever forwarded, so a caller-supplied --live can never
be interpreted as a flag by the CLI.

No environment variable is required. The CLI's own credentials from
`stripe login` are used, and the CLI defaults to test mode without --live.
Pinning --api-key would not help: the CLI reads STRIPE_API_KEY in GetAPIKey()
(pkg/config/profile.go) ahead of other sources, so a live value there would win
over a pinned flag. Hence check_environment refuses to run at all when the
environment points the CLI at live mode.

Two operations, both read-only except the single permitted test-clock advance:
  stripe_cli.py read --path /v1/<resource> [--param k=v ...]
  stripe_cli.py advance-clock --clock <clock_id> --days <n>

advance-clock is the single permitted write: advancing an ALREADY-ATTACHED test
clock. Everything else that creates, updates, or deletes Stripe state is out of
scope and unreachable through this script.

Exit codes: 0 ok; 1 the Stripe CLI failed; 2 usage error; 20 disallowed path or
malformed test clock id; 21 the environment points the CLI at live mode.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

EXIT_OK = 0
EXIT_CLI = 1
EXIT_USAGE = 2
EXIT_PATH = 20
EXIT_KEY = 21

LIVE_KEY_PREFIXES = ("sk_live_", "rk_live_")
# Stripe test clock ids are 'clock_' followed by an alphanumeric token. Anything
# else is rejected before it can be interpolated into a request path.
CLOCK_ID_PATTERN = re.compile(r"clock_[A-Za-z0-9]+")
CLOCK_POLL_DELAY = 2
CLOCK_POLL_LIMIT = 60
SECONDS_PER_DAY = 86400


class GuardError(Exception):
    """A request rejected by policy, carrying its documented exit code."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def check_environment(env):
    """Refuse to run when the environment points the CLI at live mode.

    The Stripe CLI reads STRIPE_API_KEY in GetAPIKey() (pkg/config/profile.go)
    ahead of its own config, so a live value there applies to every command this
    wrapper issues. Passing --api-key would not override it, which is why this is
    a refusal rather than a pin. Nothing needs to be set for the normal case: the
    credentials from `stripe login` are used and the CLI defaults to test mode.
    """
    key = (env.get("STRIPE_API_KEY") or "").strip()
    if key.startswith(LIVE_KEY_PREFIXES):
        raise GuardError(
            EXIT_KEY,
            "STRIPE_API_KEY is set to a LIVE key. The Stripe CLI reads that "
            "variable in preference to its own configuration, so every command "
            "would run against live data. Unset it and retry; this skill uses "
            "the test mode credentials from 'stripe login'.",
        )


def check_path(path):
    """Reject anything that is not a bare /v1/ resource path."""
    if not path.startswith("/v1/"):
        raise GuardError(EXIT_PATH, f"path must start with /v1/, got: {path}")
    if any(char.isspace() for char in path):
        raise GuardError(EXIT_PATH, f"path may not contain whitespace: {path}")
    if "-" == path[4:5] or "--" in path:
        raise GuardError(EXIT_PATH, f"path may not contain flag-like segments: {path}")


def check_clock_id(clock_id):
    """Reject anything that is not a bare Stripe test clock id.

    The read path has check_path; the clock id had nothing, yet it is
    interpolated straight into /v1/test_helpers/test_clocks/<id>[/advance],
    which is the only Stripe write this wrapper permits. Flag injection is not
    reachable, since argv is a list and no shell is involved, but a value like
    'clock_1/../../customers' would traverse to another resource, and the id
    ultimately comes from plan content that can originate in untrusted Jira
    text. Allowing only the documented id shape closes that.
    """
    if not CLOCK_ID_PATTERN.fullmatch(clock_id or ""):
        raise GuardError(
            EXIT_PATH,
            "--clock must be a Stripe test clock id of the form "
            f"clock_<alphanumeric>, got: {clock_id!r}",
        )


def build_read_argv(path, params):
    """argv for a read. Built from scratch, so no caller flag is ever forwarded."""
    argv = ["stripe", "get", path]
    for param in params or []:
        argv.extend(["-d", param])
    return argv


def build_get_clock_argv(clock_id):
    return ["stripe", "get", f"/v1/test_helpers/test_clocks/{clock_id}"]


def build_advance_argv(clock_id, frozen_time):
    return [
        "stripe",
        "post",
        f"/v1/test_helpers/test_clocks/{clock_id}/advance",
        "-d",
        f"frozen_time={frozen_time}",
    ]


def run_cli(argv):
    """Execute the Stripe CLI and return stdout. Raises GuardError on failure."""
    try:
        completed = subprocess.run(argv, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        raise GuardError(
            EXIT_CLI,
            "the 'stripe' CLI is not installed or not on PATH. Install it and run "
            "'stripe login'; do not improvise another data source.",
        )
    if completed.returncode != 0:
        raise GuardError(
            EXIT_CLI,
            f"stripe CLI failed ({completed.returncode}): {completed.stderr.strip()}",
        )
    return completed.stdout


def _clock(clock_id, run):
    body = run(build_get_clock_argv(clock_id))
    try:
        return json.loads(body)
    except ValueError as err:
        raise GuardError(EXIT_CLI, f"unparseable test clock response: {err}")


def advance_clock(clock_id, days, run, sleep):
    """Advance an already-attached test clock one day at a time.

    One day per step is deliberate: Stripe's smart retry policy fires a payment
    retry per simulated day, which is what drives a subscription to unpaid after
    eight failures. Each step waits for status to return to 'ready' before the
    next, because Stripe rejects an advance on a clock that is still advancing.
    """
    check_clock_id(clock_id)
    response = _clock(clock_id, run)
    try:
        frozen = int(response["frozen_time"])
    except (KeyError, TypeError, ValueError):
        # A response missing, nulling, or non-numerically typing frozen_time
        # would otherwise escape as a traceback: main() only catches GuardError,
        # so the operator would lose the documented exit code.
        raise GuardError(
            EXIT_CLI,
            f"test clock {clock_id} response has no usable 'frozen_time': "
            f"{response!r}",
        )
    completed = 0
    for _ in range(days):
        frozen += SECONDS_PER_DAY
        try:
            run(build_advance_argv(clock_id, frozen))
            for _attempt in range(CLOCK_POLL_LIMIT):
                if _clock(clock_id, run).get("status") == "ready":
                    break
                sleep(CLOCK_POLL_DELAY)
            else:
                raise GuardError(
                    EXIT_CLI,
                    f"test clock {clock_id} did not return to 'ready' after "
                    f"{CLOCK_POLL_LIMIT * CLOCK_POLL_DELAY}s",
                )
        except GuardError as err:
            # A multi-day advance can run long enough to be interrupted (see
            # the Bash-timeout note in SKILL.md). Annotate whatever failed with
            # how far it got, so the caller can re-read frozen_time and resume
            # instead of reissuing the full day count, and preserve the
            # original exit code.
            raise GuardError(
                err.code,
                f"{err.message} (advanced {completed} of {days} day(s) before "
                f"failing; last attempted frozen_time={frozen})",
            ) from err
        completed += 1
    return frozen


def main(argv, env):
    parser = argparse.ArgumentParser(
        prog="stripe_cli.py",
        description="Policy-guarded Stripe CLI access (test mode only).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    read = sub.add_parser("read", help="GET a /v1/ resource")
    read.add_argument("--path", required=True)
    read.add_argument("--param", action="append", default=[])

    advance = sub.add_parser("advance-clock", help="advance an attached test clock")
    advance.add_argument("--clock", required=True)
    advance.add_argument("--days", type=int, required=True)

    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else EXIT_USAGE

    try:
        check_environment(env)
        if args.command == "read":
            check_path(args.path)
            sys.stdout.write(run_cli(build_read_argv(args.path, args.param)))
        else:
            check_clock_id(args.clock)
            if args.days < 1:
                raise GuardError(EXIT_USAGE, "--days must be at least 1")
            frozen = advance_clock(args.clock, args.days, run_cli, time.sleep)
            print(f"test clock {args.clock} advanced to frozen_time={frozen}")
    except GuardError as err:
        print(f"ERROR: {err.message}", file=sys.stderr)
        return err.code
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], os.environ))
