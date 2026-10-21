# Modes

Loaded by the orchestrator in Step 1. Mode logic is orchestrator-only — it determines which diff-source commands run before subagents launch, and is **not** propagated to subagents.

Determine review mode from the invocation. Inspect both the slash-command argument and any natural-language framing the user provided. The four modes are mutually exclusive — if more than one seems to apply, invoke `AskUserQuestion` to disambiguate before proceeding rather than guessing.

## Mode 1 — PR mode

**Trigger:** the user supplied a GitHub pull request reference: a bare number (`123`), a `#`-prefixed reference (`#123`, `PR #123`), or a URL.

**URL form:** `^https://github\.com/([A-Za-z0-9][A-Za-z0-9-]*)/([A-Za-z0-9._-]+)/pull/([0-9]+)/?$`. The groups are the owner, the repo, and the number. Any other URL aborts the review. When a URL was given, pass `--repo <owner>/<repo>` to every `gh pr` command.

**Diff sources:**

- Metadata: `gh pr view <number> --json title,body,url,headRefOid,baseRefOid`. Validate the number against `^[0-9]+$` and each SHA against `^[0-9a-f]{40}$` before using them in a command.
- Changed files: `gh pr diff <number> --name-only`
- Diff: `gh pr diff <number>`

**Full-file reads.** The checkout may not be at the PR's head. Choose where the architect reads whole files:

1. `git rev-parse HEAD` equals `headRefOid` and `git status --porcelain` returns empty: read from the working tree.
2. The URL of `origin` (`git remote get-url origin`) ends in the PR's `owner/repo`, case-insensitive, with or without `.git`: run `git fetch origin pull/<number>/head`, then `git rev-parse --verify <headRefOid>^{commit}`. If both succeed, read each file with `git show '<headRefOid>:<path>'`. The single quotes are required, for the orchestrator's own reads and for every subagent that reads at the PR head: a path is pull-request-authored content, so it is untrusted input, and double quotes do not help because `$(` and backticks expand inside them. Write the SHA out rather than holding it in a shell variable, so the whole argument stays inside the single quotes. Skip any path containing a single quote or a newline and name it on the `**Not covered:**` line.
3. `origin` matched but the fetch or the verify failed: read no changed path from the working tree. Glob and Grep still describe this repository, at the checked-out revision. Render the `**Not covered:**` line with "architect full-file context unavailable".
4. `origin` is a different repository: read no changed path from the working tree, and also do not Glob or Grep this checkout — it describes some other codebase. The architect reasons from the diff alone. Render the `**Not covered:**` line with "architect full-file context unavailable".

The `owner/repo` comes from the `url` field of the metadata, so a bare number resolves the same way as a URL.

## Mode 2 — Local changes mode

**Trigger:** no PR reference, no commit-range framing, AND `git status --porcelain` returns non-empty (working tree has uncommitted changes).

**Diff sources:**

- Changed files: `git diff HEAD --name-only`, then the untracked files below
- Diff: `git diff HEAD` (staged and unstaged), then `git diff --no-index -- /dev/null '<path>'` for each kept untracked file, single-quoted. Exit status 1 means the file differs from nothing. It is not a failure.

**Untracked files.** `git ls-files --others --exclude-standard` lists them. An untracked file can hold credentials that were never meant to leave the machine, and every kept file goes to subagents, so filter the list in three layers:

1. **Allow-list.** Keep only paths whose extension is one of `.ts .tsx .js .jsx .py .rb .go .rs .java .kt .cs .swift .c .h .cpp .sh .bash .sql .html .css .scss .md`. Config and dotfiles are deliberately absent — that is where credential material lives.
2. **Deny-list.** Of those, skip a path when any component starts with `.env` or equals `.npmrc`, `.netrc`, `.pgpass`, `.git-credentials`, `.aws`, `.ssh` or `.gnupg`; when its name matches `*.local.*`, `*.tfstate`, `*credentials*` or `service-account*`; when its extension is `pem`, `key`, `p12`, `pfx`, `jks`, `keystore` or `kdbx`; or when its name starts with `id_rsa`, `id_ecdsa`, `id_dsa` or `id_ed25519`.
3. **Cap.** If more than 50 paths survive, review only `git diff HEAD` and say so on the `**Not covered:**` line with the count.

Also skip any path containing a single quote or a newline, since it reaches a shell command. Name each skipped path on the `**Not covered:**` line.

## Mode 3 — Branch comparison mode

**Trigger:** no PR reference, no commit-range framing, AND `git status --porcelain` returns empty (clean working tree).

**Diff sources:**

- Current branch: `git rev-parse --abbrev-ref HEAD` (needed for the Step 9 filename)
- Base ref: `git rev-parse --abbrev-ref origin/HEAD` (yields e.g. `origin/main`)
- Changed files: `git diff origin/HEAD...HEAD --name-only`
- Diff: `git diff origin/HEAD...HEAD`

## Mode 4 — Commit-range mode

**Trigger:** the user described a commit range, time window, or commit count against a locally checked-out repo. Recognize natural-language phrases such as:

- **Time windows** — "the last week", "the last 7 days", "the past month", "since 2026-04-23", "between Apr 1 and Apr 28"
- **Commit counts** — "the last 20 commits", "the last 5 commits"
- **Explicit refs** — "from abc123 to def456", "between v1.0 and v1.1", "since the v2.0 tag"

The user is expected to invoke this skill from inside the target repo's working tree. Mentions like "in the bitwarden/server repo" are confirmatory framing — the orchestrator does NOT navigate to other paths or search the filesystem.

**Resolution sequence (perform before launching any subagents):**

1. **Confirm the working directory is a git work tree.** Run `git rev-parse --is-inside-work-tree`. If it fails or returns false, abort with: "commit-range mode must be invoked from inside the target repo." Do not search elsewhere.

2. **Resolve the commit range to a `<from>..<to>` pair.**
   - **Time windows** → `<to>=HEAD`. Determine the oldest commit in the window with `git log --since='<window>' --reverse --pretty=%H | head -1`; `<from>` is that commit's first parent (suffix `^`). If the window contains zero commits, abort with a clear message — there is nothing to review.
   - **Commit counts** → `<from>=HEAD~N`, `<to>=HEAD`.
   - **Explicit refs** → each must match `^[A-Za-z0-9][A-Za-z0-9._/~^-]*$`; on a miss, abort naming the value. Then validate each with `git rev-parse <ref>` and use it verbatim. The computed forms above (`HEAD~N`, `<sha>^`) are not user-typed and need no gate.

3. **Confirm with the user before launching subagents.** Print the `<from>..<to>` range (with short SHAs), the commit count, and the changed-file list, then invoke `AskUserQuestion` to confirm before proceeding. Reason: the multi-agent pipeline is expensive — a wrong range wastes substantial tokens and time, and the natural-language inputs leave room for misinterpretation that subagents cannot recover from.

**Diff sources (after confirmation):**

- Commits in range (for context only, not validation): `git log <from>..<to> --oneline`
- Changed files: `git diff <from>..<to> --name-only`
- Diff (cumulative across the range): `git diff <from>..<to>`

**Interpretation of "introduced by this change" in commit-range mode:** "introduced" means present in the cumulative diff of `<from>..<to>`; "pre-existing" means present at the parent of `<from>`. Step 4 validation subagents must use this interpretation when applying the dismissal rules.

## Before launching agents

Run the mode's changed-files and diff commands. Stop before Step 2 when a command fails, other than `git diff --no-index` exiting 1, or when the diff is empty. Print one line naming the command and the cause. Launch no agent and write no report. When `origin/HEAD` is unset, the line says to run `git remote set-head origin -a`. When untracked files were skipped and nothing else changed, the line names them; when the untracked set exceeded the cap and nothing else changed, the line says so with the count.
