#!/usr/bin/env python3
"""Capture diffs for a stack of PRs or commits as base64 strings.

Emits a JSON map suitable for inlining into the scaffold config under each
stack item's ``diff_b64`` field, or for piping straight into a config patcher.

Examples:
    # PRs from a Bitwarden repo
    python scripts/capture_diffs.py --repo bitwarden/ios pr 2573 2576 2577

    # Commits from the cwd
    python scripts/capture_diffs.py commit a1b2c3 d4e5f6

    # Write the map to a file
    python scripts/capture_diffs.py --output diffs.json --repo bitwarden/server pr 1234

The script shells out to ``gh`` (for PRs) and ``git`` (for commits). It does
not fetch reviews, comments, or metadata — only the unified diff text.
"""
from __future__ import annotations

import argparse
import base64
import json
import shutil
import subprocess
import sys
from pathlib import Path


def die(msg: str, code: int = 1) -> None:
    print(f"capture_diffs.py: {msg}", file=sys.stderr)
    sys.exit(code)


def need(binary: str) -> None:
    if shutil.which(binary) is None:
        die(f"required binary not found on PATH: {binary}")


def gh_pr_diff(repo: str | None, pr: str) -> str:
    need("gh")
    cmd = ["gh", "pr", "diff", pr]
    if repo:
        cmd += ["--repo", repo]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        die(f"gh pr diff failed for {pr}: {result.stderr.strip()}")
    return result.stdout


def git_show(commit: str, cwd: Path | None = None) -> str:
    need("git")
    cmd = ["git", "show", "--no-color", commit]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        die(f"git show failed for {commit}: {result.stderr.strip()}")
    return result.stdout


def encode(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture diffs as base64.")
    parser.add_argument("--repo", help="GitHub repo in 'owner/name' form (PR mode)")
    parser.add_argument("--cwd", type=Path, help="Working directory for git commands")
    parser.add_argument(
        "--output",
        type=Path,
        help="Write the JSON map to this file. Defaults to stdout.",
    )
    sub = parser.add_subparsers(dest="kind", required=True)

    pr_p = sub.add_parser("pr", help="Capture PR diffs via gh")
    pr_p.add_argument("numbers", nargs="+", help="PR numbers")

    commit_p = sub.add_parser("commit", help="Capture commit diffs via git show")
    commit_p.add_argument("shas", nargs="+", help="Commit SHAs (any length)")

    args = parser.parse_args()

    diffs: dict[str, str] = {}
    if args.kind == "pr":
        for number in args.numbers:
            text = gh_pr_diff(args.repo, number)
            diffs[number] = encode(text)
    else:
        for sha in args.shas:
            text = git_show(sha, cwd=args.cwd)
            # Use the short SHA as the key; the caller can rename in their config.
            key = sha[:12]
            diffs[key] = encode(text)

    payload = json.dumps(diffs, indent=2)
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
