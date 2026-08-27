#!/usr/bin/env python3
"""Print the Bitwarden dev admin email address(es) from server/dev/secrets.json.

Reads only the `adminSettings.admins` value and prints it; no other field of the
secrets file is ever emitted, so running this never surfaces the database,
Stripe, or other credentials the same file holds. This exists so the
reading-mailcatcher-api skill can learn the local admin address deterministically
without granting a broad file read over a secrets file.

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


def read_admins(path):
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        raise SecretsError(
            f"secrets file not found: {path}. Pass --secrets-file to point at "
            "your bitwarden/server checkout's dev/secrets.json."
        )
    except OSError as err:
        raise SecretsError(f"could not read {path}: {err}")
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
