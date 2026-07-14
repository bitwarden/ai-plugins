#!/usr/bin/env python3
# Reads a PostToolUse hook JSON on stdin and emits git-linkage telemetry that
# ties a Claude session to the code it produced. Three signals:
#
#   Edit | MultiEdit | Write | NotebookEdit  -> bw.edit   ("Claude touched file F")
#   Bash running `git commit`                 -> bw.commit ("Claude authored SHA")
#   Bash running `gh pr create`               -> bw.pr     ("Claude opened PR N")
#
# Captures git METADATA ONLY -- repo slug, branch, commit SHA, file PATH. NEVER
# file contents or diffs. NEVER fails the session: git calls are guarded and
# time-boxed; always exits 0.
import json
import os
import re
import subprocess
import sys

from emit import emit  # sibling module; script dir is on sys.path[0]

EDIT_TOOLS = {"Edit", "MultiEdit", "Write", "NotebookEdit"}

# A real `git commit` INVOCATION: the `git` program (optionally with global flags
# like `-C <dir>`) followed by the `commit` SUBCOMMAND. Anchored to the start of a
# command segment so it never matches `commit` as an argument to a read-only
# subcommand (git log --grep commit, git log -- commit, git help commit) or a
# non-git program (echo git commit). The `commit` token must be a whole word so
# `git commit-tree` etc. don't false-positive; `[^\n|&;]*?` lets global flags but
# not another subcommand precede it.
_GIT_COMMIT_RE = re.compile(
    r"(?:^|[\n|&;]|\&\&|\|\|)\s*git\b(?:\s+-[^\s]+(?:\s+[^\s-][^\s]*)?)*\s+commit\b"
)
# `--dry-run` turns a commit into a no-op preview: no SHA is produced, so it must
# never emit bw.commit even though the subcommand IS `commit`.
_DRY_RUN_RE = re.compile(r"(?<![\w-])--dry-run(?![\w-])")

# `gh pr create` markers for a FAILED invocation. The most common failure is a
# PR already existing for the branch, which `gh` reports on stderr along with
# the EXISTING PR's URL - matching that URL without this gate would attribute
# someone else's PR to the current session.
_PR_CREATE_FAILURE_MARKERS = ("already exists", "error", "failed", "fatal",
                              "could not", "must be authenticated")


def _is_successful_commit(command, tool_response):
    """Pure predicate: did this Bash `command` + PostToolUse `tool_response`
    represent a real `git commit` that actually succeeded?

    Two independent gates, BOTH required:
      1. The command is a genuine `git commit` INVOCATION (the commit subcommand,
         optionally after global flags) and is NOT a `--dry-run` preview. Read-only
         lookalikes (git log --grep commit, git show, git help commit) fail here.
      2. The tool_response indicates success — no interrupt, no non-zero exit, and
         no failure text on stderr (mirrors how the gh-pr branch reads its
         response). Absent any signal we stay conservative and return False rather
         than fabricate an authored commit from the prior HEAD.
    """
    if not _GIT_COMMIT_RE.search(command or ""):
        return False
    if _DRY_RUN_RE.search(command or ""):
        return False
    if not isinstance(tool_response, dict):
        return False
    if tool_response.get("interrupted"):
        return False
    exit_code = tool_response.get("exit_code", tool_response.get("exitCode"))
    if exit_code is not None and exit_code != 0:
        return False
    stdout = (tool_response.get("stdout") or "").strip()
    stderr = (tool_response.get("stderr") or "").lower()
    # A successful commit prints a "[<branch> <sha>] <summary>" summary to stdout.
    # Failures ("nothing to commit", rejecting pre-commit hook) leave stdout empty
    # and put the reason on stderr. Require a positive stdout signal and no failure
    # marker so an empty/error response never fabricates a commit.
    if any(marker in stderr for marker in ("nothing to commit", "error", "failed",
                                           "fatal", "rejected", "aborting")):
        return False
    return bool(stdout)


def _is_successful_pr_create(tool_response):
    """Pure predicate: did this `gh pr create` invocation actually succeed?

    Mirrors _is_successful_commit's gate. A successful `gh pr create` prints
    the new PR's URL to stdout; a failed one (most commonly a PR already
    existing for the branch) reports the error, along with the EXISTING PR's
    URL, on stderr. Callers must only search stdout for the PR number, and
    only once this returns True.
    """
    if not isinstance(tool_response, dict):
        return False
    if tool_response.get("interrupted"):
        return False
    exit_code = tool_response.get("exit_code", tool_response.get("exitCode"))
    if exit_code is not None and exit_code != 0:
        return False
    stdout = (tool_response.get("stdout") or "").strip()
    stderr = (tool_response.get("stderr") or "").lower()
    if any(marker in stderr for marker in _PR_CREATE_FAILURE_MARKERS):
        return False
    # Require a positive stdout signal, same as _is_successful_commit, so an
    # empty/ambiguous response never fabricates a PR.
    return bool(stdout)


def _git(cwd, *args):
    """Run a git command in cwd, returning trimmed stdout or "" on any failure."""
    try:
        out = subprocess.run(["git", "-C", cwd, *args],
                             capture_output=True, text=True, timeout=1)
        return out.stdout.strip() if out.returncode == 0 else ""
    except Exception:
        return ""


def _repo_full(cwd):
    """Normalize the origin remote to an ``owner/name`` slug (matches GitHub)."""
    url = _git(cwd, "remote", "get-url", "origin")
    m = re.search(r"[:/]([^/:]+/[^/]+?)(?:\.git)?/?$", url)
    return m.group(1) if m else ""


def _repo_rel(cwd, path):
    """Make an edited file path relative to the repo root, so it joins against
    GitHub's repo-root-relative ``files[].filename``."""
    if not path:
        return ""
    top = _git(cwd, "rev-parse", "--show-toplevel")
    try:
        ap = path if os.path.isabs(path) else os.path.join(cwd, path)
        # realpath both sides: on macOS /var -> /private/var symlinks otherwise
        # leave the two paths divergent and relpath produces "../../.." noise.
        ap = os.path.realpath(ap)
        top = os.path.realpath(top) if top else top
        return os.path.relpath(ap, top) if top else os.path.basename(ap)
    except Exception:
        return os.path.basename(path)


def handle_edit(h, tin, cwd, session):
    path = tin.get("file_path") or tin.get("notebook_path") or ""
    if not path:
        return
    emit("bw.edit", {
        "event.name": "bw.edit",
        "session.id": session,
        "bw.repo_full": _repo_full(cwd),
        "bw.branch": _git(cwd, "rev-parse", "--abbrev-ref", "HEAD"),
        "bw.base_sha": _git(cwd, "rev-parse", "HEAD"),
        "bw.file": _repo_rel(cwd, path),
        "bw.tool": h.get("tool_name", ""),
        "bw.hook": h.get("hook_event_name", ""),
    })


def handle_bash(h, tin, cwd, session):
    cmd = tin.get("command") or ""
    # git commit: the hook fires AFTER the command, so HEAD already points at the
    # new commit. Re-reading HEAD is deterministic and avoids parsing stdout, but
    # only once a real commit has been confirmed to have succeeded. A loose match
    # would let `git commit --dry-run`, a failed commit (nothing staged / rejected
    # pre-commit hook), or a read-only lookalike (git log --grep commit, git show,
    # git help commit) emit the PRIOR HEAD as a fabricated authored commit.
    if _is_successful_commit(cmd, h.get("tool_response") or {}):
        sha = _git(cwd, "rev-parse", "HEAD")
        if sha:
            emit("bw.commit", {
                "event.name": "bw.commit",
                "session.id": session,
                "bw.repo_full": _repo_full(cwd),
                "bw.branch": _git(cwd, "rev-parse", "--abbrev-ref", "HEAD"),
                "bw.commit_sha": sha,
                "bw.hook": h.get("hook_event_name", ""),
            })
    # gh pr create: pull the new PR's number from stdout, only on success.
    # A failed invocation (most commonly a PR already existing for the
    # branch) reports the EXISTING PR's URL on stderr; only stdout can be
    # trusted to name a PR this session actually created.
    if re.search(r"\bgh\b[^\n|&;]*\bpr\b[^\n|&;]*\bcreate\b", cmd):
        resp = h.get("tool_response") or {}
        if _is_successful_pr_create(resp):
            stdout = resp.get("stdout") or ""
            m = re.search(r"/pull/(\d+)", stdout)
            if m:
                emit("bw.pr", {
                    "event.name": "bw.pr",
                    "session.id": session,
                    "bw.repo_full": _repo_full(cwd),
                    "bw.branch": _git(cwd, "rev-parse", "--abbrev-ref", "HEAD"),
                    "bw.pr_number": m.group(1),
                    "bw.hook": h.get("hook_event_name", ""),
                })


def main():
    try:
        h = json.load(sys.stdin)
    except Exception:
        return
    tin = h.get("tool_input") or {}
    cwd = h.get("cwd") or os.getcwd()
    session = h.get("session_id", "")
    tool = h.get("tool_name", "")
    if tool in EDIT_TOOLS:
        handle_edit(h, tin, cwd, session)
    elif tool == "Bash":
        handle_bash(h, tin, cwd, session)


if __name__ == "__main__":
    main()
    sys.exit(0)
