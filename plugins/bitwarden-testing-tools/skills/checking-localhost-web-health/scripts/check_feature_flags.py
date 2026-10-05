#!/usr/bin/env python3
"""Check that the running local Bitwarden Api reports each required feature flag
in the required state.

The running Api's GET /config response is the authority: its featureStates map
is what the web client loads, so one read answers for the server and the web
client. server/dev/secrets.json and the server source are read only to explain a
mismatch, and only the requested flag keys are looked up in them. secrets.json
also holds the Stripe test key, the SQL password, and the installation id and
key, so nothing else from it is ever printed.

Usage:
  check_feature_flags.py [--secrets-path <path>] [--server-src-path <path>]
                         -- <flag-key>=on|off [...]

Put `--` before the requirements so no value can be read as an option. The
running Api does not read secrets.json directly: it reads dotnet user-secrets,
which server/dev/setup_secrets.ps1 copies from secrets.json (Aspire runs it as
the setup-secrets resource). So every mismatch ends with one line saying to
refresh secrets and restart the dependent services.

--secrets-path defaults to server/dev/secrets.json and --server-src-path to
server/src, both relative to the current working directory (the bitwarden root,
where the pipeline runs). /config reports a flag only when a class marked
[FlagKeyCollection] under server/src declares it and a value is configured for
it, so when a required flag is missing from /config the script checks both
secrets.json and those classes and prints a Problem line for each one that
explains the gap.

Exit codes: 0 every flag is in the required state; 1 the Api's /config could not
be read; 2 usage error, including --help, so an option-shaped value never reads
as success; 3 at least one flag is in the wrong state.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

EXIT_OK = 0
EXIT_API = 1
EXIT_USAGE = 2
EXIT_MISMATCH = 3

# Hard-coded with no override, so the check can never be pointed at another host.
CONFIG_URL = "http://localhost:4000/config"
CONFIG_TIMEOUT_SECONDS = 10
DEFAULT_SECRETS_FILE = os.path.join("server", "dev", "secrets.json")
DEFAULT_SERVER_SRC = os.path.join("server", "src")
# The Bitwarden.Server.Sdk.Features source generator registers the keys of every
# class marked with this attribute, so only those files can declare a flag.
FLAG_KEY_COLLECTION_MARKER = "[FlagKeyCollection"
SKIPPED_SOURCE_DIRS = ("bin", "obj")
# Flag keys can originate in untrusted Jira text, so only the documented key
# shape is accepted before anything is looked up or printed.
REQUIREMENT_PATTERN = re.compile(r"([a-z0-9][a-z0-9.-]*)=(on|off)")
# Where flag values live in secrets.json, in precedence order. The server copies
# globalSettings.launchDarkly.flagValues into Features:FlagValues with TryAdd
# (ServerSdkCompatibilityExtensions), so a value under features.flagValues wins.
FLAG_SECTIONS = (
    ("features", "flagValues"),
    ("globalSettings", "launchDarkly", "flagValues"),
)
DEFAULT_FLAG_SECTION = ".".join(FLAG_SECTIONS[1])
FOLLOW_UP = "  Then refresh secrets and restart the dependent services."


class ApiError(Exception):
    """The running Api's /config response could not be read or used."""


def parse_requirement(arg):
    """Return (flag_key, required_on) for a '<flag-key>=on|off' argument."""
    match = REQUIREMENT_PATTERN.fullmatch(arg)
    if not match:
        raise ValueError(
            f"invalid requirement {arg!r}: expected <flag-key>=on|off, where "
            "<flag-key> is lowercase letters, digits, '.', and '-'"
        )
    return match.group(1), match.group(2) == "on"


def parse_requirements(args):
    """Parse every argument, refusing a flag listed more than once."""
    requirements = []
    seen = set()
    for arg in args:
        key, required_on = parse_requirement(arg)
        if key in seen:
            raise ValueError(f"flag {key!r} is listed more than once")
        seen.add(key)
        requirements.append((key, required_on))
    return requirements


def _as_bool(value):
    """Map a flag value to True, False, or None when it is not a boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.strip().lower() in ("true", "false"):
        return value.strip().lower() == "true"
    return None


def _get_ci(mapping, name):
    """Look up a key case-insensitively, as .NET configuration does."""
    if not isinstance(mapping, dict):
        return None
    lowered = name.lower()
    for key, value in mapping.items():
        if isinstance(key, str) and key.lower() == lowered:
            return value
    return None


def strip_jsonc(text):
    """Return `text` with JSONC extras removed so json.loads can parse it.

    Removes // line comments, /* */ block comments, and trailing commas. The
    scan is string-aware, so a // inside a value such as an https:// URL is kept.
    Copied from reading-mailcatcher-api's get_admin_email.py; skills do not
    share code, so each script carries its own copy.
    """
    out = []
    i, n = 0, len(text)
    in_string = False
    pending_comma = None  # index in `out` of a comma awaiting its next token
    while i < n:
        char = text[i]
        if in_string:
            out.append(char)
            if char == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if char == '"':
                in_string = False
            i += 1
            continue
        if char == '"':
            pending_comma = None
            in_string = True
            out.append(char)
            i += 1
            continue
        if char == "/" and i + 1 < n and text[i + 1] == "/":
            i += 2
            while i < n and text[i] != "\n":
                i += 1
            continue
        if char == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2  # skip the closing */
            continue
        if char.isspace():
            out.append(char)
            i += 1
            continue
        if char == ",":
            pending_comma = len(out)
            out.append(char)
            i += 1
            continue
        if char in "}]":
            if pending_comma is not None:
                out[pending_comma] = ""  # drop the trailing comma
            pending_comma = None
            out.append(char)
            i += 1
            continue
        pending_comma = None
        out.append(char)
        i += 1
    return "".join(out)


def _http_get(url):
    # An empty ProxyHandler keeps an http_proxy environment variable from
    # routing this localhost request anywhere else.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(url, timeout=CONFIG_TIMEOUT_SECONDS) as response:
        return response.read().decode("utf-8")


def fetch_feature_states(fetch):
    """Return the featureStates map from the running Api's /config."""
    try:
        body = fetch(CONFIG_URL)
        data = json.loads(body)
    except (urllib.error.URLError, OSError, UnicodeDecodeError) as err:
        raise ApiError(str(err))
    except ValueError as err:
        raise ApiError(f"response is not JSON: {err}")
    states = _get_ci(data, "featureStates")
    if not isinstance(states, dict):
        raise ApiError("response has no featureStates object")
    return states


def load_secrets(path, read_text):
    """Return (parsed secrets, problem). Never raises: a missing file is not fatal."""
    try:
        data = json.loads(strip_jsonc(read_text(path)))
    except FileNotFoundError:
        return None, f"{path} was not found"
    except (OSError, UnicodeDecodeError) as err:
        return None, f"{path} could not be read ({err.__class__.__name__})"
    except ValueError:
        return None, f"{path} could not be parsed"
    if not isinstance(data, dict):
        return None, f"{path} is not a JSON object"
    return data, None


def declares_flag(server_src_path, key, read_text):
    """Return True/False whether a [FlagKeyCollection] class declares key, or
    None when the source tree, or any file in it, could not be read."""
    if not os.path.isdir(server_src_path):
        return None
    quoted_key = f'"{key}"'
    for root, dirs, files in os.walk(server_src_path):
        dirs[:] = [d for d in dirs if d.lower() not in SKIPPED_SOURCE_DIRS]
        for name in files:
            if not name.endswith(".cs"):
                continue
            try:
                text = read_text(os.path.join(root, name))
            except (OSError, UnicodeDecodeError):
                return None
            if FLAG_KEY_COLLECTION_MARKER in text and quoted_key in text:
                return True
    return False


def configured_value(secrets, key):
    """Return (True/False/None, section) for key in the first section holding it."""
    for path in FLAG_SECTIONS:
        section = secrets
        for name in path:
            section = _get_ci(section, name)
        if not isinstance(section, dict):
            continue
        for name, value in section.items():
            if isinstance(name, str) and name.lower() == key:
                return _as_bool(value), ".".join(path)
    return None, None


def _state(value):
    return "on" if value else "off"


def secrets_problem(secrets, secrets_problem_text, key, required_on, secrets_path):
    """Return the secrets.json Problem for key, or None when it is set as required."""
    if secrets is None:
        return f"{secrets_problem_text}, so its value for this flag is unknown."
    configured, section = configured_value(secrets, key)
    if configured is required_on:
        return None
    wanted = "true" if required_on else "false"
    return (
        f'set "{key}": "{wanted}" under {section or DEFAULT_FLAG_SECTION} in '
        f"{secrets_path}."
    )


def declaration_problem(declared, server_src_path):
    """Return the server source Problem for a flag, or None when it is declared."""
    if declared is None:
        return (
            f"{server_src_path} could not be read, so whether a [FlagKeyCollection] "
            "class declares this flag is unknown."
        )
    if not declared:
        return (
            f"no [FlagKeyCollection] class under {server_src_path} declares this "
            "flag; check out a server branch that declares it."
        )
    return None


def evaluate(requirements, states, secrets, secrets_problem_text, secrets_path,
             is_declared, server_src_path=DEFAULT_SERVER_SRC):
    """Return (output lines, every flag matches).

    A flag /config does not report runs every check, so the output names every
    problem rather than only the first.
    """
    lines = []
    all_match = True
    for key, required_on in requirements:
        raw = _get_ci(states, key)
        reported = raw is not None
        running_on = _as_bool(raw) is True
        running = _state(running_on) if reported else "not reported (treated as off)"
        if running_on == required_on:
            lines.append(f"{key}: required {_state(required_on)}, running {running} — OK")
            continue
        all_match = False
        lines.append(f"{key}: required {_state(required_on)}, running {running} — MISMATCH")
        problems = [secrets_problem(secrets, secrets_problem_text, key, required_on, secrets_path)]
        if not reported:
            problems.append(declaration_problem(is_declared(key), server_src_path))
        problems = [problem for problem in problems if problem]
        if not problems:
            _configured, section = configured_value(secrets, key)
            wanted = "true" if required_on else "false"
            problems.append(
                f'{section} in {secrets_path} already sets it to "{wanted}", but the '
                "running Api has not picked it up."
            )
        lines.extend(f"  Problem: {problem}" for problem in problems)
        lines.append(FOLLOW_UP)
    return lines, all_match


def _read_text(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def main(argv, fetch=_http_get, read_text=_read_text):
    parser = argparse.ArgumentParser(
        prog="check_feature_flags.py",
        description="Check required feature flags against the running local Api.",
    )
    parser.add_argument("--secrets-path", default=DEFAULT_SECRETS_FILE)
    parser.add_argument("--server-src-path", default=DEFAULT_SERVER_SRC)
    parser.add_argument("requirements", nargs="+", metavar="<flag-key>=on|off")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        # Covers --help too: exit 0 would read as "every flag is as required".
        return EXIT_USAGE

    try:
        requirements = parse_requirements(args.requirements)
    except ValueError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return EXIT_USAGE

    try:
        states = fetch_feature_states(fetch)
    except ApiError as err:
        print(
            f"ERROR: could not read the running Api's feature flags from {CONFIG_URL}: "
            f"{err}. Make sure the Api is running.",
            file=sys.stderr,
        )
        return EXIT_API

    secrets, problem = load_secrets(args.secrets_path, read_text)
    lines, all_match = evaluate(
        requirements, states, secrets, problem, args.secrets_path,
        lambda key: declares_flag(args.server_src_path, key, read_text),
        args.server_src_path,
    )
    for line in lines:
        print(line)
    return EXIT_OK if all_match else EXIT_MISMATCH


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
