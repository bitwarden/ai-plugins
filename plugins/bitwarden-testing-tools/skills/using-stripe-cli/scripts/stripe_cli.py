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
`stripe login` are used, and the CLI defaults to test mode without --live. But
the CLI never checks that its test-mode key is actually a test key: a live key
typed into `stripe login --interactive` or `stripe config --set
test_mode_api_key` is used without --live. So before every call check_key
resolves the key the CLI would use (STRIPE_API_KEY, else the active profile's
test-mode key in the CLI config, per Stripe CLI v1.35 GetAPIKey() in
pkg/config/profile.go), refuses anything that is not a test key, and pins the
checked key for the call. Pinning goes through STRIPE_API_KEY itself, because
the CLI reads that variable ahead of every other source, including --api-key.
A config the wrapper cannot verify is refused, not passed through.

Two operations, both read-only except the single permitted test-clock advance:
  stripe_cli.py read --path /v1/<resource> [--param k=v ...]
  stripe_cli.py advance-clock --clock <clock_id> --days <n>

advance-clock is the single permitted write: advancing an ALREADY-ATTACHED test
clock. Everything else that creates, updates, or deletes Stripe state is out of
scope and unreachable through this script.

Exit codes: 0 ok; 1 the Stripe CLI failed; 2 usage error; 20 disallowed path or
malformed test clock id; 21 the key the CLI would use is live, missing, or
cannot be verified as a test key.
"""
import argparse
import functools
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
TEST_KEY_PREFIXES = ("sk_test_", "rk_test_")
# Stripe CLI v1.35 test-mode key fields, in the order GetAPIKey() consults them:
# the legacy secret_key and api_key aliases win whenever they are present.
KEY_FIELDS = ("secret_key", "api_key", "test_mode_api_key")
# Stripe test clock ids are 'clock_' followed by an alphanumeric token. Anything
# else is rejected before it can be interpolated into a request path.
CLOCK_ID_PATTERN = re.compile(r"clock_[A-Za-z0-9]+")
CLOCK_POLL_DELAY = 2
CLOCK_POLL_LIMIT = 60
SECONDS_PER_DAY = 86400
# A single advance polls up to CLOCK_POLL_LIMIT * CLOCK_POLL_DELAY seconds per
# simulated day, so a batch larger than this cannot finish inside the Bash
# tool's 600000 ms (10 minute) ceiling before it is killed mid-advance. Reject
# the oversized batch up front rather than let it die partway in a state that
# is hard to diagnose. See SKILL.md, "The one permitted write".
MAX_ADVANCE_DAYS = 4


class GuardError(Exception):
    """A request rejected by policy, carrying its documented exit code."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def _key_error(message):
    return GuardError(EXIT_KEY, message)


def _fold_case(table, where):
    """Lower-case a TOML table's keys the way viper does, refusing collisions."""
    folded = {}
    for name, value in table.items():
        lowered = name.lower()
        if lowered in folded:
            raise _key_error(
                f"{where} has keys that differ only by case ('{lowered}'); the "
                "Stripe CLI would merge them, so the key cannot be verified."
            )
        folded[lowered] = value
    return folded


def config_path(env):
    """The config file the Stripe CLI reads (pkg/config/config.go)."""
    base = env.get("XDG_CONFIG_HOME")
    if not base:
        home = env.get("HOME") or env.get("USERPROFILE")
        if not home:
            raise _key_error(
                "cannot locate the Stripe CLI config: neither XDG_CONFIG_HOME, "
                "HOME, nor USERPROFILE is set."
            )
        base = os.path.join(home, ".config")
    return os.path.join(base, "stripe", "config.toml")


def resolve_test_key(env):
    """Return (key, source) for the key the Stripe CLI would use in test mode.

    key is None when nothing is configured; source then says what was missing.
    Every variable is read from env, and an empty value counts as unset.
    """
    key = (env.get("STRIPE_API_KEY") or "").strip()
    if key:
        return key, "STRIPE_API_KEY"

    path = config_path(env)
    try:
        import tomllib
    except ImportError:
        raise _key_error(
            "Python 3.11+ is required to verify the Stripe CLI config; set "
            "STRIPE_API_KEY to a test key or use a newer python3."
        )
    try:
        with open(path, "rb") as handle:
            data = tomllib.load(handle)
    except FileNotFoundError:
        return None, f"no Stripe CLI config at {path}"
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as err:
        raise _key_error(
            f"could not read the Stripe CLI config at {path} to verify the key "
            f"is a test key: {err}"
        )

    top = _fold_case(data, path)
    profile = env.get("STRIPE_PROJECT_NAME") or top.get("project-name") or "default"
    if not isinstance(profile, str):
        raise _key_error(f"project-name in {path} is not a string.")
    profile = profile.lower()

    table = None
    nested = top.get("profiles")
    if isinstance(nested, dict):
        table = _fold_case(nested, f"[profiles] in {path}").get(profile)
    if table is None:
        table = top.get(profile)
    if table is None:
        return None, f"no `{profile}` profile in {path}"
    if not isinstance(table, dict):
        raise _key_error(f"`{profile}` in {path} is not a table.")

    fields = _fold_case(table, f"the `{profile}` profile in {path}")
    for name in KEY_FIELDS:
        if name in fields:
            value = fields[name]
            source = f"the `{profile}` profile's `{name}` in {path}"
            if not isinstance(value, str):
                raise _key_error(f"{source} is not a string.")
            return value.strip() or None, source
    return None, f"the `{profile}` profile in {path} has no test-mode key"


def check_key(env):
    """Return the test-mode key the Stripe CLI would use, or refuse with exit 21.

    The CLI validates only a key's sk_/rk_ prefix, never its mode, so a live key
    in STRIPE_API_KEY or in the profile's test-mode slot would reach live data.
    This allows only sk_test_/rk_test_ keys, and fails closed on a missing or
    unverifiable config. The caller pins the returned key via STRIPE_API_KEY,
    so the key checked here is the key the CLI uses.
    """
    key, source = resolve_test_key(env)
    if not key:
        raise _key_error(
            f"no Stripe test-mode key found ({source}); run 'stripe login' (or "
            "set STRIPE_API_KEY to an sk_test_ key)."
        )
    if key.startswith(LIVE_KEY_PREFIXES):
        raise _key_error(
            f"{source} holds a LIVE key. Every command would run against live "
            "data. Restore a test-mode key (for example, 'stripe login') and retry."
        )
    if not key.startswith(TEST_KEY_PREFIXES):
        raise _key_error(
            f"{source} is not a test-mode key (expected sk_test_ or rk_test_)."
        )
    return key


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


def run_cli(argv, key):
    """Execute the Stripe CLI with key pinned and return stdout.

    Raises GuardError on failure.
    """
    try:
        completed = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "STRIPE_API_KEY": key},
        )
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


def _run_json(argv, run):
    """Run the CLI, parse its JSON, and surface an API-level error as GuardError.

    The Stripe CLI returns exit 0 with a top-level {"error": {...}} body for
    API-level failures (a bad id, a rejected advance), so run_cli does not raise
    on them. Left unchecked on an internal clock call, a rejected advance would
    masquerade as success: the loop would see the clock still 'ready' at its old
    frozen_time and report an advance that never happened. Detect the error body
    here and raise EXIT_CLI so the failure is loud. The read command keeps its
    pass-through behavior on purpose (see SKILL.md, "Interpreting responses").
    """
    body = run(argv)
    try:
        data = json.loads(body)
    except ValueError as err:
        raise GuardError(EXIT_CLI, f"unparseable Stripe response: {err}")
    if isinstance(data, dict) and isinstance(data.get("error"), dict):
        error = data["error"]
        detail = error.get("message") or error.get("type") or "unknown error"
        raise GuardError(EXIT_CLI, f"Stripe API error: {detail}")
    return data


def _clock(clock_id, run):
    return _run_json(build_get_clock_argv(clock_id), run)


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
            _run_json(build_advance_argv(clock_id, frozen), run)
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
        run = functools.partial(run_cli, key=check_key(env))
        if args.command == "read":
            check_path(args.path)
            sys.stdout.write(run(build_read_argv(args.path, args.param)))
        else:
            check_clock_id(args.clock)
            if args.days < 1:
                raise GuardError(EXIT_USAGE, "--days must be at least 1")
            if args.days > MAX_ADVANCE_DAYS:
                raise GuardError(
                    EXIT_USAGE,
                    f"--days must be at most {MAX_ADVANCE_DAYS}: a single call "
                    "cannot advance more simulated days than fit inside the Bash "
                    "tool's 10-minute ceiling before it is killed mid-advance. "
                    f"Split it into batches of at most {MAX_ADVANCE_DAYS} days, "
                    "re-reading the clock status between them.",
                )
            frozen = advance_clock(args.clock, args.days, run, time.sleep)
            print(f"test clock {args.clock} advanced to frozen_time={frozen}")
    except GuardError as err:
        print(f"ERROR: {err.message}", file=sys.stderr)
        return err.code
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], os.environ))
