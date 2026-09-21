#!/usr/bin/env python3
"""Unit tests for emit_git: the success/eligibility decisions that gate the
bw.commit and bw.pr emits, and the git context an edit resolves to. Importing
emit_git is safe: it guards its side effects behind ``if __name__ ==
"__main__"``.

Run with:  python3 -m unittest test_emit_git   (from the hooks/ dir)
      or:  python3 -m pytest test_emit_git.py
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import emit_git
from emit_git import (_command_git_dir, _commit_summary, _is_successful_commit,
                     _is_successful_pr_create, _pr_url_repo)

# Fixtures: a stub session id and a fabricated abbreviated SHA.
# cspell:ignore sess deadbee


def _ok(stdout="", stderr=""):
    """A tool_response for a command that exited cleanly."""
    return {"stdout": stdout, "stderr": stderr, "interrupted": False}


class IsSuccessfulCommitTest(unittest.TestCase):
    # --- real, successful git commit invocations -> True -------------------
    def test_real_commit_with_message(self):
        self.assertTrue(_is_successful_commit(
            'git commit -m "fix the thing"',
            _ok(stdout="[main a1b2c3d] fix the thing\n 1 file changed, 2 insertions(+)"),
        ))

    def test_commit_all_flag(self):
        self.assertTrue(_is_successful_commit(
            "git commit -am 'wip'",
            _ok(stdout="[feature 9f8e7d6] wip\n 1 file changed"),
        ))

    def test_commit_with_global_flags_before_subcommand(self):
        self.assertTrue(_is_successful_commit(
            'git -C /repo commit -m "scoped"',
            _ok(stdout="[main abc1234] scoped\n 1 file changed"),
        ))

    def test_commit_no_verify(self):
        self.assertTrue(_is_successful_commit(
            'git commit --no-verify -m "skip hooks"',
            _ok(stdout="[main 1234abc] skip hooks"),
        ))

    # --- dry-run is not a commit -> False ---------------------------------
    def test_dry_run_long(self):
        self.assertFalse(_is_successful_commit(
            'git commit --dry-run -m "nope"',
            _ok(stdout="On branch main\nChanges to be committed:"),
        ))

    def test_dry_run_short(self):
        self.assertFalse(_is_successful_commit(
            "git commit -n --dry-run",
            _ok(stdout="nothing staged"),
        ))

    # --- failed commit -> False -------------------------------------------
    def test_failed_nothing_staged(self):
        self.assertFalse(_is_successful_commit(
            'git commit -m "empty"',
            {"stdout": "", "stderr": "nothing to commit, working tree clean",
             "interrupted": False},
        ))

    def test_failed_precommit_hook_rejected(self):
        self.assertFalse(_is_successful_commit(
            'git commit -m "rejected"',
            {"stdout": "", "stderr": "pre-commit hook failed", "interrupted": False},
        ))

    def test_interrupted(self):
        self.assertFalse(_is_successful_commit(
            'git commit -m "cancelled"',
            {"stdout": "", "stderr": "", "interrupted": True},
        ))

    def test_explicit_nonzero_exit(self):
        self.assertFalse(_is_successful_commit(
            'git commit -m "boom"',
            {"stdout": "", "stderr": "error", "exit_code": 1, "interrupted": False},
        ))

    # --- read-only / lookalike subcommands -> False -----------------------
    def test_log_grep_commit(self):
        self.assertFalse(_is_successful_commit(
            "git log --grep commit",
            _ok(stdout="commit abc123\nAuthor: someone"),
        ))

    def test_git_show(self):
        self.assertFalse(_is_successful_commit(
            "git show",
            _ok(stdout="commit abc123\ndiff --git a/x b/x"),
        ))

    def test_git_help_commit(self):
        self.assertFalse(_is_successful_commit(
            "git help commit",
            _ok(stdout="GIT-COMMIT(1)  Manual"),
        ))

    def test_git_commit_as_pathspec_in_log(self):
        # "commit" appearing only as an argument, not the subcommand.
        self.assertFalse(_is_successful_commit(
            "git log -- commit",
            _ok(stdout="commit abc123"),
        ))

    def test_non_git_command(self):
        self.assertFalse(_is_successful_commit(
            "echo git commit",
            _ok(stdout="git commit"),
        ))

    # --- defensive: malformed tool_response --------------------------------
    def test_non_dict_tool_response(self):
        self.assertFalse(_is_successful_commit('git commit -m "x"', "some string"))

    def test_empty_tool_response(self):
        # No positive success signal at all -> do not fabricate a commit.
        self.assertFalse(_is_successful_commit('git commit -m "x"', {}))


class IsSuccessfulPrCreateTest(unittest.TestCase):
    # --- real, successful `gh pr create` -> True ---------------------------
    def test_real_pr_create(self):
        self.assertTrue(_is_successful_pr_create(
            _ok(stdout="https://github.com/owner/repo/pull/124"),
        ))

    # --- PR already exists for the branch -> False -------------------------
    def test_pr_already_exists(self):
        # gh reports the EXISTING PR's URL on stderr; must not be attributed
        # to this session.
        self.assertFalse(_is_successful_pr_create({
            "stdout": "",
            "stderr": ('a pull request for branch "feature/x" into branch '
                       '"main" already exists:\nhttps://github.com/owner/repo/pull/123'),
            "interrupted": False,
        }))

    # --- other failure modes -> False ---------------------------------------
    def test_auth_failure(self):
        self.assertFalse(_is_successful_pr_create({
            "stdout": "", "stderr": "must be authenticated to run this command",
            "interrupted": False,
        }))

    def test_interrupted(self):
        self.assertFalse(_is_successful_pr_create({
            "stdout": "https://github.com/owner/repo/pull/124",
            "stderr": "", "interrupted": True,
        }))

    def test_explicit_nonzero_exit(self):
        self.assertFalse(_is_successful_pr_create({
            "stdout": "", "stderr": "", "exit_code": 1, "interrupted": False,
        }))

    # --- defensive: malformed tool_response --------------------------------
    def test_non_dict_tool_response(self):
        self.assertFalse(_is_successful_pr_create("some string"))

    def test_empty_tool_response(self):
        self.assertFalse(_is_successful_pr_create({}))


def _run(cwd, *args):
    subprocess.run(args, cwd=cwd, check=True,
                   capture_output=True, text=True)


def _init_repo(path, origin, branch="main"):
    """A repo with one commit, an origin slug, and a named branch."""
    os.makedirs(path, exist_ok=True)
    _run(path, "git", "init", "-b", branch)
    _run(path, "git", "config", "user.email", "t@example.com")
    _run(path, "git", "config", "user.name", "T")
    _run(path, "git", "remote", "add", "origin",
         f"https://github.com/{origin}.git")
    with open(os.path.join(path, "seed.txt"), "w") as fh:
        fh.write("seed\n")
    _run(path, "git", "add", ".")
    _run(path, "git", "commit", "-m", "seed")
    return path


class EditGitContextTest(unittest.TestCase):
    """An edit's repo, branch and file path must come from the file's own
    location, never from the session's cwd. A session started in one checkout
    routinely edits files in a worktree or a sibling repo, and resolving git
    against cwd mislabels every one of those with the cwd repo's slug and
    branch plus a ``../`` path that matches nothing on the PR side.
    """

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="emit_git_ctx_")
        cls.repo_a = _init_repo(os.path.join(cls.tmp, "a"), "acme/alpha")
        cls.repo_b = _init_repo(os.path.join(cls.tmp, "b"), "acme/bravo",
                                branch="feat/bee")
        # A worktree of repo A on its own branch, the shape that breaks today.
        cls.worktree = os.path.join(cls.tmp, "a-wt")
        _run(cls.repo_a, "git", "worktree", "add", "-b", "feat/wt",
             cls.worktree)
        cls.outside = os.path.join(cls.tmp, "loose")
        os.makedirs(cls.outside, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def _emit_for(self, cwd, file_path):
        """Run handle_edit and return the attributes it would have emitted."""
        captured = {}

        def fake_emit(name, attrs):
            captured["name"] = name
            captured["attrs"] = attrs

        real = emit_git.emit
        emit_git.emit = fake_emit
        try:
            emit_git.handle_edit(
                {"tool_name": "Edit", "hook_event_name": "PostToolUse"},
                {"file_path": file_path}, cwd, "sess-1",
            )
        finally:
            emit_git.emit = real
        return captured.get("attrs", {})

    def _touch(self, repo, name):
        p = os.path.join(repo, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as fh:
            fh.write("x\n")
        return p

    def test_file_in_sibling_repo_reports_that_repo(self):
        f = self._touch(self.repo_b, "src/thing.py")
        a = self._emit_for(self.repo_a, f)
        self.assertEqual(a["bw.repo_full"], "acme/bravo")
        self.assertEqual(a["bw.branch"], "feat/bee")
        self.assertEqual(a["bw.file"], "src/thing.py")

    def test_file_in_worktree_reports_the_worktree_branch(self):
        f = self._touch(self.worktree, "pkg/mod.py")
        a = self._emit_for(self.repo_a, f)
        self.assertEqual(a["bw.repo_full"], "acme/alpha")
        self.assertEqual(a["bw.branch"], "feat/wt")
        self.assertEqual(a["bw.file"], "pkg/mod.py")

    def test_file_path_never_escapes_the_repo_root(self):
        f = self._touch(self.repo_b, "deep/nested/leaf.md")
        a = self._emit_for(self.repo_a, f)
        self.assertNotIn("..", a["bw.file"])

    def test_file_in_the_session_repo_still_works(self):
        f = self._touch(self.repo_a, "lib/keep.py")
        a = self._emit_for(self.repo_a, f)
        self.assertEqual(a["bw.repo_full"], "acme/alpha")
        self.assertEqual(a["bw.branch"], "main")
        self.assertEqual(a["bw.file"], "lib/keep.py")

    def test_relative_path_resolves_against_cwd(self):
        self._touch(self.repo_a, "rel/here.py")
        a = self._emit_for(self.repo_a, "rel/here.py")
        self.assertEqual(a["bw.repo_full"], "acme/alpha")
        self.assertEqual(a["bw.file"], "rel/here.py")

    def test_file_outside_any_repo_is_not_emitted(self):
        """An event with no repository to key on identifies nothing."""
        f = self._touch(self.outside, "scratch.py")
        self.assertEqual(self._emit_for(self.repo_a, f), {})

    def test_repo_without_an_origin_remote_is_not_emitted(self):
        """A branch and SHA are only meaningful within a repository, and an
        origin remote is the only thing that names one."""
        anon = os.path.join(self.tmp, "anon")
        os.makedirs(anon, exist_ok=True)
        _run(anon, "git", "init", "-b", "main")
        _run(anon, "git", "config", "user.email", "t@example.com")
        _run(anon, "git", "config", "user.name", "T")
        with open(os.path.join(anon, "seed.txt"), "w") as fh:
            fh.write("seed\n")
        _run(anon, "git", "add", ".")
        _run(anon, "git", "commit", "-m", "seed")
        f = self._touch(anon, "thing.py")
        self.assertEqual(self._emit_for(self.repo_a, f), {})

    def test_new_file_in_existing_dir_resolves(self):
        """Write creates the file after the hook reads the payload in some
        flows, so a path that does not exist yet must still resolve."""
        f = os.path.join(self.repo_b, "src", "not_written_yet.py")
        a = self._emit_for(self.repo_a, f)
        self.assertEqual(a["bw.repo_full"], "acme/bravo")
        self.assertEqual(a["bw.file"], "src/not_written_yet.py")

    def test_base_sha_is_the_files_repo_head(self):
        f = self._touch(self.worktree, "sha.py")
        a = self._emit_for(self.repo_a, f)
        head = subprocess.run(["git", "-C", self.worktree, "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
        self.assertEqual(a["bw.base_sha"], head)


class CommitSummaryTest(unittest.TestCase):
    """`git commit` names the branch and the new SHA on stdout. That is the
    only authoritative statement of what was committed, since the directory
    the hook can reach may not be the one the commit happened in."""

    def test_plain_commit(self):
        self.assertEqual(_commit_summary("[main a1b2c3d] fix the thing\n 1 file changed"),
                         ("main", "a1b2c3d"))

    def test_slashed_branch(self):
        self.assertEqual(_commit_summary("[feat/bee 9f8e7d6] wip"),
                         ("feat/bee", "9f8e7d6"))

    def test_root_commit(self):
        self.assertEqual(_commit_summary("[main (root-commit) abc1234] seed"),
                         ("main", "abc1234"))

    def test_full_length_sha(self):
        sha = "a" * 40
        self.assertEqual(_commit_summary(f"[main {sha}] big"), ("main", sha))

    def test_detached_head_has_no_branch(self):
        branch, sha = _commit_summary("[detached HEAD abc1234] wip")
        self.assertEqual(branch, "")
        self.assertEqual(sha, "abc1234")

    def test_summary_not_on_first_line(self):
        self.assertEqual(_commit_summary("husky: running hooks\n[main deadbee] ok"),
                         ("main", "deadbee"))

    def test_no_summary(self):
        self.assertIsNone(_commit_summary("On branch main\nnothing to commit"))

    def test_empty(self):
        self.assertIsNone(_commit_summary(""))


class PrUrlRepoTest(unittest.TestCase):
    """`gh pr create` prints the new PR's URL, which names the repo outright,
    so the repo never has to be guessed from a directory."""

    def test_plain_url(self):
        self.assertEqual(_pr_url_repo("https://github.com/bitwarden/server/pull/8362\n"),
                         "bitwarden/server")

    def test_url_among_other_output(self):
        self.assertEqual(
            _pr_url_repo("Warning: 3 uncommitted changes\n"
                         "https://github.com/acme/alpha-beta/pull/12\n"),
            "acme/alpha-beta")

    def test_enterprise_host(self):
        self.assertEqual(_pr_url_repo("https://git.example.com/acme/alpha/pull/7"),
                         "acme/alpha")

    def test_no_url(self):
        self.assertEqual(_pr_url_repo("created something"), "")

    def test_empty(self):
        self.assertEqual(_pr_url_repo(""), "")


class CommandGitDirTest(unittest.TestCase):
    """Where a Bash command actually operated. A session's cwd is only the
    answer when the command didn't say otherwise."""

    def test_no_directive_is_cwd(self):
        self.assertEqual(_command_git_dir("/base", 'git commit -m "x"'), "/base")

    def test_git_dash_c_absolute(self):
        self.assertEqual(_command_git_dir("/base", 'git -C /other commit -m "x"'),
                         "/other")

    def test_git_dash_c_relative(self):
        self.assertEqual(_command_git_dir("/base", "git -C sub/tree commit -m x"),
                         "/base/sub/tree")

    def test_git_dash_c_quoted_path_with_space(self):
        self.assertEqual(_command_git_dir("/base", 'git -C "/a b/repo" commit -m x'),
                         "/a b/repo")

    def test_leading_cd(self):
        self.assertEqual(_command_git_dir("/base", "cd /other && git commit -m x"),
                         "/other")

    def test_leading_cd_relative(self):
        self.assertEqual(_command_git_dir("/base", "cd wt && git commit -m x"),
                         "/base/wt")

    def test_dash_c_wins_over_cd(self):
        self.assertEqual(
            _command_git_dir("/base", "cd /one && git -C /two commit -m x"), "/two")

    def test_cd_in_later_segment_is_ignored(self):
        """Only a cd that precedes the git call can have moved it."""
        self.assertEqual(_command_git_dir("/base", "git commit -m x && cd /other"),
                         "/base")

    def test_path_containing_the_word_git(self):
        """A directory named ...-git-... must not be mistaken for the git call
        and truncate the cd target mid-path. A worktree whose own name carried
        the word silently suppressed every bw.commit made in it, because the
        resolved directory did not exist."""
        self.assertEqual(
            _command_git_dir("/base", "cd /repos/verify-hook-git-context && git commit -m x"),
            "/repos/verify-hook-git-context")

    def test_path_containing_git_as_a_whole_segment(self):
        self.assertEqual(
            _command_git_dir("/base", "cd /srv/git/repo && git commit -m x"),
            "/srv/git/repo")

    def test_cd_terminated_by_a_semicolon(self):
        """An unquoted directory stops at the separator. Swallowing it yields
        a path that does not exist, and the event is lost."""
        self.assertEqual(_command_git_dir("/base", "cd /wt; git commit -m x"),
                         "/wt")

    def test_cd_with_no_space_before_the_separator(self):
        self.assertEqual(_command_git_dir("/base", "cd /wt&&git commit -m x"),
                         "/wt")

    def test_dash_c_terminated_by_a_semicolon(self):
        self.assertEqual(_command_git_dir("/base", "git -C /wt; echo done"),
                         "/wt")

    def test_cd_inside_a_subshell(self):
        """`(cd /wt && git commit ...)` acts in a worktree without moving the
        session, so the paren has to open a segment like any other separator."""
        self.assertEqual(_command_git_dir("/base", "(cd /wt && git commit -m x)"),
                         "/wt")

    def test_gh_command_with_a_cd_still_resolves(self):
        """No git call at all, so the whole command is eligible prefix."""
        self.assertEqual(
            _command_git_dir("/base", "cd /other && gh pr create --fill"), "/other")


class BashGitContextTest(unittest.TestCase):
    """bw.commit and bw.pr must describe the repo the command ran in, and
    bw.commit must never report a SHA the command did not produce. Reading
    HEAD from the session's cwd did both: a commit made in a worktree was
    reported as the cwd repo's untouched HEAD, which is a real SHA belonging
    to some other pull request."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="emit_git_bash_")
        cls.repo_a = _init_repo(os.path.join(cls.tmp, "a"), "acme/alpha")
        cls.repo_b = _init_repo(os.path.join(cls.tmp, "b"), "acme/bravo",
                                branch="feat/bee")
        cls.worktree = os.path.join(cls.tmp, "a-wt")
        _run(cls.repo_a, "git", "worktree", "add", "-b", "feat/wt", cls.worktree)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def _commit_in(self, repo, name):
        """Make a real commit and return (full_sha, branch, git's stdout)."""
        with open(os.path.join(repo, name), "w") as fh:
            fh.write("x\n")
        _run(repo, "git", "add", ".")
        _run(repo, "git", "commit", "-m", f"add {name}")
        sha = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"],
                             capture_output=True, text=True).stdout.strip()
        branch = subprocess.run(
            ["git", "-C", repo, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True).stdout.strip()
        return sha, branch, f"[{branch} {sha[:7]}] add {name}\n 1 file changed"

    def _emit_for(self, cwd, command, stdout):
        captured = {}

        def fake_emit(name, attrs):
            captured[name] = attrs

        real = emit_git.emit
        emit_git.emit = fake_emit
        try:
            emit_git.handle_bash(
                {"tool_name": "Bash", "hook_event_name": "PostToolUse",
                 "tool_response": {"stdout": stdout, "stderr": "",
                                   "interrupted": False}},
                {"command": command}, cwd, "sess-1",
            )
        finally:
            emit_git.emit = real
        return captured

    def test_commit_in_worktree_reports_the_worktree(self):
        sha, branch, out = self._commit_in(self.worktree, "wt.txt")
        got = self._emit_for(self.repo_a,
                             f"cd {self.worktree} && git commit -m 'add wt.txt'",
                             out)
        a = got["bw.commit"]
        self.assertEqual(a["bw.commit_sha"], sha)
        self.assertEqual(a["bw.branch"], "feat/wt")
        self.assertEqual(a["bw.repo_full"], "acme/alpha")

    def test_commit_in_sibling_repo_reports_that_repo(self):
        sha, branch, out = self._commit_in(self.repo_b, "sib.txt")
        got = self._emit_for(self.repo_a,
                             f"git -C {self.repo_b} commit -m 'add sib.txt'", out)
        a = got["bw.commit"]
        self.assertEqual(a["bw.commit_sha"], sha)
        self.assertEqual(a["bw.branch"], "feat/bee")
        self.assertEqual(a["bw.repo_full"], "acme/bravo")

    def test_commit_in_cwd_still_works(self):
        sha, branch, out = self._commit_in(self.repo_a, "own.txt")
        got = self._emit_for(self.repo_a, "git commit -m 'add own.txt'", out)
        a = got["bw.commit"]
        self.assertEqual(a["bw.commit_sha"], sha)
        self.assertEqual(a["bw.branch"], "main")
        self.assertEqual(a["bw.repo_full"], "acme/alpha")

    def test_sha_the_command_did_not_produce_is_not_emitted(self):
        """The bug that shipped: a commit made somewhere the hook cannot see
        must not be reported as the cwd repo's current HEAD."""
        got = self._emit_for(self.repo_a, "git commit -m 'made elsewhere'",
                             "[some-branch 0123456] made elsewhere\n 1 file changed")
        self.assertNotIn("bw.commit", got)

    def test_commit_in_a_repo_without_an_origin_is_not_emitted(self):
        anon = os.path.join(self.tmp, "anon-commit")
        os.makedirs(anon, exist_ok=True)
        _run(anon, "git", "init", "-b", "main")
        _run(anon, "git", "config", "user.email", "t@example.com")
        _run(anon, "git", "config", "user.name", "T")
        sha, branch, out = self._commit_in(anon, "x.txt")
        got = self._emit_for(self.repo_a, f"git -C {anon} commit -m x", out)
        self.assertNotIn("bw.commit", got)

    def test_commit_without_a_summary_is_not_emitted(self):
        got = self._emit_for(self.repo_a, "git commit -m x", "committed, probably")
        self.assertNotIn("bw.commit", got)

    def test_pr_repo_comes_from_the_url_not_the_cwd(self):
        got = self._emit_for(
            self.repo_a, "gh pr create --fill",
            "https://github.com/acme/bravo/pull/77\n")
        a = got["bw.pr"]
        self.assertEqual(a["bw.repo_full"], "acme/bravo")
        self.assertEqual(a["bw.pr_number"], "77")

    def test_pr_falls_back_to_the_command_directory(self):
        got = self._emit_for(self.repo_a, f"gh -R x pr create --fill",
                             "created: /pull/91\n")
        a = got["bw.pr"]
        self.assertEqual(a["bw.repo_full"], "acme/alpha")
        self.assertEqual(a["bw.pr_number"], "91")

    def test_pr_branch_comes_from_the_command_directory(self):
        got = self._emit_for(
            self.repo_a, f"cd {self.repo_b} && gh pr create --fill",
            "https://github.com/acme/bravo/pull/78\n")
        self.assertEqual(got["bw.pr"]["bw.branch"], "feat/bee")


if __name__ == "__main__":
    unittest.main()
