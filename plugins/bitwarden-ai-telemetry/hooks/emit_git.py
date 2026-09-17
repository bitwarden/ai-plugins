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

from emit import emit, flush_warning  # sibling module; script dir is on sys.path[0]

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

# `git commit` announces its result as "[<branch> <sha>] <summary>", with
# "(root-commit)" interposed on a repo's first commit and the words "detached
# HEAD" in place of a branch. This is the authoritative record of WHAT was
# committed, because the directory the hook can reach is not necessarily the
# one the commit happened in.
_COMMIT_SUMMARY_RE = re.compile(
    r"^\[(?P<branch>[^\]]+?)\s+(?:\(root-commit\)\s+)?(?P<sha>[0-9a-f]{7,40})\]",
    re.MULTILINE,
)
# The URL `gh pr create` prints names the repo outright, so bw.pr never has to
# infer it from a directory. Host-agnostic, since Enterprise serves the same
# shape.
_PR_URL_RE = re.compile(r"https?://[^/\s]+/([^/\s]+/[^/\s]+)/pull/\d+")
# A command can move before it acts. An explicit `git -C <dir>` is definitive;
# otherwise a `cd` that PRECEDES the git call is what moved it.
# An unquoted directory stops at a shell separator. Matching \S+ instead would
# swallow the separator itself — `cd /wt; git commit` yields "/wt;" and
# `cd /wt&&git commit` yields "/wt&&" — and git would then fail on a directory
# that does not exist, silently costing the event.
_UNQUOTED_DIR = r"[^\s;|&]+"
_GIT_DASH_C_RE = re.compile(
    r"\bgit\b[^\n|&;]*?\s-C\s+(?P<dir>\"[^\"]+\"|'[^']+'|" + _UNQUOTED_DIR + r")"
)
_CD_RE = re.compile(
    r"(?:^|[\n|;]|\&\&)\s*cd\s+(?P<dir>\"[^\"]+\"|'[^']+'|" + _UNQUOTED_DIR + r")"
)
# The `git` PROGRAM at the start of a command segment, as opposed to the three
# letters appearing anywhere. Paths carry them routinely, so anchoring matters.
_GIT_INVOCATION_RE = re.compile(r"(?:^|[\n|&;])\s*(?P<cmd>git)\b")


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


def _commit_summary(stdout):
    """``(branch, sha)`` as `git commit` itself reported them, or None.

    The SHA may be abbreviated; callers resolve it against a real HEAD rather
    than emitting it directly. A detached HEAD yields an empty branch instead
    of the literal words, so nothing downstream joins "detached HEAD" against
    a pull request's head ref.
    """
    m = _COMMIT_SUMMARY_RE.search(stdout or "")
    if not m:
        return None
    branch = m.group("branch").strip()
    if branch.lower() == "detached head":
        branch = ""
    return branch, m.group("sha")


def _pr_url_repo(stdout):
    """``owner/repo`` from the PR URL `gh pr create` printed, else ""."""
    m = _PR_URL_RE.search(stdout or "")
    return m.group(1) if m else ""


def _command_git_dir(cwd, command):
    """The directory a Bash command actually operated in.

    Commands routinely move before acting, via `git -C <dir>` or `cd <dir> &&
    ...`, while the hook payload's cwd stays wherever the session started.
    Relative directives resolve against cwd. A `cd` after the git call cannot
    have moved it, so only text preceding the git call is considered.

    The git call is located at a command-segment boundary, not by any "git"
    in the string: directory names contain it often enough (a worktree at
    .../verify-hook-git-context) that a bare word match would cut the prefix
    mid-path and yield a directory that does not exist.
    """
    cmd = command or ""

    def _resolve(raw):
        d = raw[1:-1] if len(raw) > 1 and raw[0] == raw[-1] and raw[0] in "\"'" else raw
        return d if os.path.isabs(d) else os.path.normpath(os.path.join(cwd, d))

    m = _GIT_DASH_C_RE.search(cmd)
    if m:
        return _resolve(m.group("dir"))
    git_call = _GIT_INVOCATION_RE.search(cmd)
    prefix = cmd[:git_call.start("cmd")] if git_call else cmd
    cds = list(_CD_RE.finditer(prefix))
    if cds:
        return _resolve(cds[-1].group("dir"))
    return cwd


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


def _abs_path(cwd, path):
    """Absolute, symlink-resolved form of a tool payload's file path.

    A relative path in the payload is relative to the session cwd, so that one
    step still anchors on cwd. Everything after it anchors on the file.
    realpath matters on macOS, where /var -> /private/var otherwise leaves a
    path and a repo root divergent and makes relpath produce "../../.." noise.
    """
    try:
        ap = path if os.path.isabs(path) else os.path.join(cwd, path)
        return os.path.realpath(ap)
    except Exception:
        return path


def _git_context_dir(cwd, abs_path):
    """The directory whose git metadata describes this edit: the file's own.

    A session's cwd says nothing about where an edited file lives. Working in
    a worktree or a sibling checkout while Claude runs from one repo root is
    routine, and resolving git against cwd stamps those edits with the cwd
    repo's slug and branch. Attribution joins bw.branch against the PR's head
    ref and bw.file against the PR's changed paths, so a cwd-derived event
    cannot match the PR it belongs to, and its branch may collide with an
    unrelated one.

    Walks up to the nearest existing directory, since a Write can name a file
    that does not exist yet, and falls back to cwd only when nothing resolves.
    """
    try:
        d = os.path.dirname(abs_path)
        while d and not os.path.isdir(d):
            parent = os.path.dirname(d)
            if parent == d:
                return cwd
            d = parent
        return d or cwd
    except Exception:
        return cwd


def _repo_rel(git_dir, abs_path):
    """Path relative to the root of the repo that owns the file, so it joins
    against GitHub's repo-root-relative ``files[].filename``.

    Expects the already-absolute, realpath'd form from _abs_path. A file in no
    repo degrades to its bare filename rather than a "../" path, which is the
    honest answer: nothing on the PR side can match either, and a relative
    escape reads as though it belonged to whichever repo cwd happened to be.
    """
    if not abs_path:
        return ""
    top = _git(git_dir, "rev-parse", "--show-toplevel")
    try:
        top = os.path.realpath(top) if top else top
        return os.path.relpath(abs_path, top) if top else os.path.basename(abs_path)
    except Exception:
        return os.path.basename(abs_path)


def _has_joinable_repo(repo):
    """Whether an event naming this repo slug can ever be read.

    Every tier of attribution keys on the repo: a commit SHA or pull request
    number is matched within one, and a file path is matched against one
    pull request's changed files. A slug is absent when the file sits outside
    any repository (a plan file, a memory file, something under /tmp) or when
    the repository has no origin remote to name. Either way nothing downstream
    can join the event, so emitting it would spend a sampled slot on a record
    no reader can use.
    """
    return bool(repo)


def handle_edit(h, tin, cwd, session):
    path = tin.get("file_path") or tin.get("notebook_path") or ""
    if not path:
        return
    abs_path = _abs_path(cwd, path)
    git_dir = _git_context_dir(cwd, abs_path)
    repo = _repo_full(git_dir)
    if not _has_joinable_repo(repo):
        return
    emit("bw.edit", {
        "event.name": "bw.edit",
        "session.id": session,
        "bw.repo_full": repo,
        "bw.branch": _git(git_dir, "rev-parse", "--abbrev-ref", "HEAD"),
        "bw.base_sha": _git(git_dir, "rev-parse", "HEAD"),
        "bw.file": _repo_rel(git_dir, abs_path),
        "bw.tool": h.get("tool_name", ""),
        "bw.hook": h.get("hook_event_name", ""),
    })


def handle_bash(h, tin, cwd, session):
    cmd = tin.get("command") or ""
    resp = h.get("tool_response") or {}
    # git commit: the command's own output says WHAT was committed, the
    # directory it ran in says WHERE. Both are needed, and they have to agree.
    #
    # Reading HEAD from cwd alone was wrong for any commit made outside it, in
    # a worktree or a sibling checkout, because cwd's untouched HEAD is still a
    # real SHA and would be reported as work this session authored — landing on
    # whichever pull request happens to contain it. Requiring HEAD to match the
    # SHA git printed drops those rather than guessing, in the same spirit as
    # _is_successful_commit refusing to fabricate a commit from an ambiguous
    # response. `--dry-run`, failed commits and read-only lookalikes are gated
    # out before this point.
    if _is_successful_commit(cmd, resp):
        summary = _commit_summary(resp.get("stdout") or "")
        if summary:
            branch, printed_sha = summary
            git_dir = _command_git_dir(cwd, cmd)
            head = _git(git_dir, "rev-parse", "HEAD")
            repo = _repo_full(git_dir)
            if head and head.startswith(printed_sha) and _has_joinable_repo(repo):
                emit("bw.commit", {
                    "event.name": "bw.commit",
                    "session.id": session,
                    "bw.repo_full": repo,
                    "bw.branch": branch or _git(git_dir, "rev-parse",
                                                "--abbrev-ref", "HEAD"),
                    # The resolved full SHA, since attribution matches it
                    # against a pull request's commit list by equality.
                    "bw.commit_sha": head,
                    "bw.hook": h.get("hook_event_name", ""),
                })
    # gh pr create: pull the new PR's number from stdout, only on success.
    # A failed invocation (most commonly a PR already existing for the
    # branch) reports the EXISTING PR's URL on stderr; only stdout can be
    # trusted to name a PR this session actually created. The same URL names
    # the repo, which beats inferring it from a directory; the directory is
    # only the fallback, and the source of the head branch.
    if re.search(r"\bgh\b[^\n|&;]*\bpr\b[^\n|&;]*\bcreate\b", cmd):
        if _is_successful_pr_create(resp):
            stdout = resp.get("stdout") or ""
            m = re.search(r"/pull/(\d+)", stdout)
            if m:
                git_dir = _command_git_dir(cwd, cmd)
                repo = _pr_url_repo(stdout) or _repo_full(git_dir)
                if not _has_joinable_repo(repo):
                    return
                emit("bw.pr", {
                    "event.name": "bw.pr",
                    "session.id": session,
                    "bw.repo_full": repo,
                    "bw.branch": _git(git_dir, "rev-parse", "--abbrev-ref", "HEAD"),
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
    # After main(), so a warning reports what this invocation actually found.
    # Prints at most one throttled systemMessage and still exits 0.
    flush_warning()
    sys.exit(0)
