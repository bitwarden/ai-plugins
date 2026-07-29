#!/usr/bin/env python3
"""Print the first Bitwarden dev admin email from server/dev/secrets.json.

Prints ONLY that one value. The dev secrets file also carries the Stripe test
mode API key, the SQL password, and the installation id and key; a whole-file
Read pulls all of it into agent context and from there into transcripts and
session logs. This script exists so only the one address the pipeline needs
crosses that boundary.

Usage:
  read_admin_email.py --secrets-path <path to server/dev/secrets.json>

Exit codes: 0 printed; 2 usage error; 4 file missing, unreadable, or carrying
no usable 'admins' entry.
"""
import argparse
import json
import sys

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_NO_ADMIN = 4


def first_admin(path):
    """Return the first non-empty string under the 'admins' key."""
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("secrets root must be a JSON object")
    admins = data.get("admins")
    if not isinstance(admins, list) or not admins:
        raise ValueError("secrets file has no 'admins' entries")
    first = admins[0]
    if not isinstance(first, str) or not first.strip():
        raise ValueError("first 'admins' entry is not a non-empty string")
    return first.strip()


def main(argv):
    parser = argparse.ArgumentParser(
        prog="read_admin_email.py",
        description="Print the first dev admin email from a Bitwarden dev secrets file.",
    )
    parser.add_argument("--secrets-path", required=True)
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else EXIT_USAGE

    try:
        print(first_admin(args.secrets_path))
    except FileNotFoundError:
        print(f"ERROR: secrets file not found: {args.secrets_path}", file=sys.stderr)
        return EXIT_NO_ADMIN
    except (json.JSONDecodeError, ValueError, OSError) as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return EXIT_NO_ADMIN
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
