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


def _strip_jsonc(text):
    """Strip // line comments and /* */ block comments from JSONC text.

    server/dev/secrets.json is JSONC: the .NET config loader tolerates comments,
    so the file carries commented-out settings (e.g. //"databaseProvider": ...).
    Python's json.loads does not, so strip comments first. String contents are
    preserved verbatim so a // or /* inside a value (like an https:// URL) is
    never mistaken for a comment.
    """
    out = []
    i = 0
    n = len(text)
    in_string = False
    while i < n:
        ch = text[i]
        if in_string:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_string = False
            i += 1
            continue
        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "/":
            i += 2
            while i < n and text[i] not in "\r\n":
                i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def first_admin(path):
    """Return the first non-empty admin email under the 'admins' key.

    In server/dev/secrets.json 'admins' is a comma-separated string
    (e.g. "admin@localhost,owner@localhost"); a JSON list is also accepted.
    """
    with open(path, encoding="utf-8") as handle:
        data = json.loads(_strip_jsonc(handle.read()))
    if not isinstance(data, dict):
        raise ValueError("secrets root must be a JSON object")
    # 'admins' lives under 'adminSettings' in server/dev/secrets.json; accept a
    # top-level key too in case the layout differs.
    section = data.get("adminSettings")
    if isinstance(section, dict) and "admins" in section:
        admins = section.get("admins")
    else:
        admins = data.get("admins")
    if isinstance(admins, str):
        entries = [part.strip() for part in admins.split(",")]
    elif isinstance(admins, list):
        entries = [part.strip() for part in admins if isinstance(part, str)]
    else:
        raise ValueError("secrets file has no usable 'admins' entry")
    entries = [entry for entry in entries if entry]
    if not entries:
        raise ValueError("secrets file has no 'admins' entries")
    return entries[0]


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
