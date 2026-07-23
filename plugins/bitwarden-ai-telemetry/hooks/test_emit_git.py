#!/usr/bin/env python3
"""Unit tests for emit_git._is_successful_commit and _is_successful_pr_create
— the pure success/eligibility decisions that gate the bw.commit and bw.pr
emits. Importing emit_git is safe: it guards its side effects behind
``if __name__ == "__main__"``.

Run with:  python3 -m unittest test_emit_git   (from the hooks/ dir)
      or:  python3 -m pytest test_emit_git.py
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from emit_git import _is_successful_commit, _is_successful_pr_create


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


if __name__ == "__main__":
    unittest.main()
