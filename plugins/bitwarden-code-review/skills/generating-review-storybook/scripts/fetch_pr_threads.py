#!/usr/bin/env python3
"""Fetch GitHub PR review threads and emit them in the storybook ``comments[]`` shape.

Each comment in each thread becomes one entry: ``{author, body, location, created_at}``.
``location`` is ``path:line`` (or just ``path`` when the line cannot be resolved).

Outdated threads are skipped by default — they point at lines that no longer
exist in the current diff and can't anchor. Resolved threads are included so
the reviewer can see "this was caught and fixed" context.

Usage:
    python scripts/fetch_pr_threads.py --repo bitwarden/android --pr 6863 \\
      --output threads.json

    # group by stack key (so you can drop the result straight into the stack item)
    python scripts/fetch_pr_threads.py --repo bitwarden/android --pr 6863 \\
      --key 6863 --output threads.json

Flags:
    --include-outdated     Include threads whose lines are no longer in the diff.
    --skip-resolved        Drop resolved threads (default: include them).
    --resolved-suffix STR  Append this string to bodies of comments in resolved
                           threads. Default: " _(resolved)_".
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

# Review threads are fetched a page at a time. A thread whose first page of
# comments is full is completed with COMMENTS_QUERY, addressed by its node id.
PAGE_SIZE = 100

COMMENT_FIELDS = """
  pageInfo { hasNextPage endCursor }
  nodes {
    body
    author { login }
    createdAt
  }
"""

THREADS_QUERY = f"""
query($owner: String!, $repo: String!, $pr: Int!, $cursor: String) {{
  repository(owner: $owner, name: $repo) {{
    pullRequest(number: $pr) {{
      reviewThreads(first: {PAGE_SIZE}, after: $cursor) {{
        pageInfo {{ hasNextPage endCursor }}
        nodes {{
          id
          isResolved
          isOutdated
          path
          line
          startLine
          diffSide
          comments(first: {PAGE_SIZE}) {{
            {COMMENT_FIELDS}
          }}
        }}
      }}
    }}
  }}
}}
"""

COMMENTS_QUERY = f"""
query($id: ID!, $cursor: String) {{
  node(id: $id) {{
    ... on PullRequestReviewThread {{
      comments(first: {PAGE_SIZE}, after: $cursor) {{
        {COMMENT_FIELDS}
      }}
    }}
  }}
}}
"""


def die(msg: str, code: int = 1) -> None:
    print(f"fetch_pr_threads.py: {msg}", file=sys.stderr)
    sys.exit(code)


def need(binary: str) -> None:
    if shutil.which(binary) is None:
        die(f"required binary not found on PATH: {binary}")


def graphql(query: str, variables: dict[str, str | int]) -> dict[str, Any]:
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for name, value in variables.items():
        # -F types integers; -f keeps strings (cursors, ids) as strings.
        flag = "-F" if isinstance(value, int) else "-f"
        cmd += [flag, f"{name}={value}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        die(f"gh api graphql failed: {result.stderr.strip()}")
    payload = json.loads(result.stdout)
    if payload.get("errors"):
        die(f"gh api graphql returned errors: {json.dumps(payload['errors'])}")
    return payload.get("data") or {}


def fetch_remaining_comments(thread: dict[str, Any]) -> None:
    """Append every comment page after the first to ``thread['comments']['nodes']``."""
    comments = thread.setdefault("comments", {})
    nodes = comments.setdefault("nodes", [])
    page_info = comments.get("pageInfo") or {}
    while page_info.get("hasNextPage"):
        data = graphql(COMMENTS_QUERY, {"id": thread["id"], "cursor": page_info["endCursor"]})
        page = ((data.get("node") or {}).get("comments")) or {}
        nodes.extend(page.get("nodes") or [])
        page_info = page.get("pageInfo") or {}


def fetch(repo: str, pr: int) -> list[dict[str, Any]]:
    """Every review thread on the PR, each with its complete comment list."""
    need("gh")
    owner, _, name = repo.partition("/")
    if not owner or not name:
        die(f"--repo must be 'owner/name', got: {repo}")
    threads: list[dict[str, Any]] = []
    variables: dict[str, str | int] = {"owner": owner, "repo": name, "pr": pr}
    while True:
        data = graphql(THREADS_QUERY, variables)
        pull = ((data.get("repository") or {}).get("pullRequest")) or {}
        page = pull.get("reviewThreads") or {}
        for thread in page.get("nodes") or []:
            fetch_remaining_comments(thread)
            threads.append(thread)
        page_info = page.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            return threads
        variables["cursor"] = page_info["endCursor"]


def thread_to_comments(thread: dict[str, Any], resolved_suffix: str) -> list[dict[str, Any]]:
    path = thread.get("path") or ""
    line = thread.get("line")
    if line is None:
        line = thread.get("startLine")
    location = f"{path}:{line}" if path and line else path
    is_resolved = bool(thread.get("isResolved"))
    out = []
    for c in (thread.get("comments") or {}).get("nodes", []):
        body = c.get("body") or ""
        if is_resolved and resolved_suffix:
            body = f"{body}{resolved_suffix}"
        out.append({
            "author": (c.get("author") or {}).get("login") or "unknown",
            "body": body,
            "location": location,
            "created_at": c.get("createdAt") or "",
        })
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch PR review threads in storybook comments[] shape.")
    parser.add_argument("--repo", required=True, help="GitHub repo in 'owner/name' form")
    parser.add_argument("--pr", required=True, type=int, help="PR number")
    parser.add_argument("--key", help="Wrap output as { key: [...comments] } (defaults to flat array)")
    parser.add_argument("--include-outdated", action="store_true", help="Include outdated threads (default: skip)")
    parser.add_argument("--skip-resolved", action="store_true", help="Drop resolved threads (default: include)")
    parser.add_argument(
        "--resolved-suffix",
        default=" _(resolved)_",
        help='Suffix appended to bodies of comments in resolved threads (default: " _(resolved)_")',
    )
    parser.add_argument("--output", type=Path, help="Write JSON to this file (default: stdout)")
    args = parser.parse_args()

    comments: list[dict[str, Any]] = []
    for t in fetch(args.repo, args.pr):
        if t.get("isOutdated") and not args.include_outdated:
            continue
        if t.get("isResolved") and args.skip_resolved:
            continue
        comments.extend(thread_to_comments(t, args.resolved_suffix))

    out: Any = comments if not args.key else {args.key: comments}
    text = json.dumps(out, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
