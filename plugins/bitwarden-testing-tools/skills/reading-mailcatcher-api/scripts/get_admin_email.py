#!/usr/bin/env python3
"""Print the Bitwarden dev admin email address(es) from server/dev/secrets.json.

Reads only the `adminSettings.admins` value and prints it; no other field of the
secrets file is ever emitted, so running this never surfaces the database,
Stripe, or other credentials the same file holds. This exists so the
reading-mailcatcher-api skill can learn the local admin address deterministically
without granting a broad file read over a secrets file.

The secrets file is JSONC by convention (Bitwarden's dev secrets.json carries
`//` and `/* */` comments and trailing commas), so it is parsed tolerantly.

Exit 0 on success (prints one address per line on stdout).
Exit 2: usage error (bad arguments).
Exit 3: secrets file not found, unreadable, invalid JSON, or missing the
        adminSettings.admins key.

Usage:
  get_admin_email.py [--secrets-file <path>] [--all]

--secrets-file defaults to server/dev/secrets.json, relative to the current
directory (run from the workspace root that holds your bitwarden/server
checkout). --all lists every configured admin address; the default prints only
the first, which is the Admin Portal login address.
"""
import argparse
import json
import os
import sys

DEFAULT_SECRETS_FILE = os.path.join("server", "dev", "secrets.json")

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_ERROR = 3


class SecretsError(Exception):
    """The secrets file could not be read or held no admin address."""


def extract_admins(data):
    """Return the admin addresses from parsed secrets JSON.

    The value lives at adminSettings.admins as a comma-separated string, e.g.
    "admin@localhost,owner@localhost". Only this key is read out; the rest of
    the parsed object is never touched, so no other secret can reach stdout.
    """
    if not isinstance(data, dict):
        raise SecretsError("secrets file is not a JSON object")
    admin_settings = data.get("adminSettings")
    if not isinstance(admin_settings, dict) or "admins" not in admin_settings:
        raise SecretsError("secrets file has no adminSettings.admins key")
    raw = admin_settings["admins"]
    if not isinstance(raw, str):
        raise SecretsError("adminSettings.admins is not a string")
    admins = [entry.strip() for entry in raw.split(",") if entry.strip()]
    if not admins:
        raise SecretsError("adminSettings.admins is empty")
    return admins


def strip_jsonc(text):
    """Return `text` with JSONC extras removed so json.loads can parse it.

    Removes `//` line comments, `/* */` block comments, and trailing commas
    (a comma whose next non-space token is `}` or `]`). The scan is
    string-aware: comment markers, commas, and braces inside string literals
    are left untouched, and backslash escapes inside strings are honored. This
    matters because Bitwarden's dev secrets.json holds values such as
    "bitwarden://premium-checkout-result" that a naive `//` strip would corrupt.
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


def read_admins(path):
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except FileNotFoundError:
        raise SecretsError(
            f"secrets file not found: {path}. Pass --secrets-file to point at "
            "your bitwarden/server checkout's dev/secrets.json."
        )
    except OSError as err:
        raise SecretsError(f"could not read {path}: {err}")
    try:
        data = json.loads(strip_jsonc(text))
    except ValueError as err:
        raise SecretsError(f"invalid JSON in {path}: {err}")
    return extract_admins(data)


def main(argv):
    parser = argparse.ArgumentParser(
        prog="get_admin_email.py",
        description="Print the Bitwarden dev admin email(s) from secrets.json.",
    )
    parser.add_argument("--secrets-file", default=DEFAULT_SECRETS_FILE)
    parser.add_argument("--all", action="store_true")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else EXIT_USAGE

    try:
        admins = read_admins(args.secrets_file)
    except SecretsError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return EXIT_ERROR

    for address in (admins if args.all else admins[:1]):
        print(address)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
