# Modes

Loaded by the orchestrator in Step 1. Mode logic is orchestrator-only — it determines which diff-source commands run before subagents launch, and is **not** propagated to subagents.

Determine review mode from the invocation. Inspect both the slash-command argument and any natural-language framing the user provided. The four modes are mutually exclusive — if more than one seems to apply, invoke `AskUserQuestion` to disambiguate before proceeding rather than guessing.

## Mode 1 — PR mode

**Trigger:** the user supplied a GitHub pull request reference. Recognize a bare number (`123`), a `#`-prefixed reference (`#123`, `PR #123`), or a pull-request URL (`https://github.com/owner/repo/pull/123`).

**Diff sources:**

- Title & description: `gh pr view <number>`
- Changed files: `gh pr diff <number> --name-only`
- Diff: `gh pr diff <number>`

## Mode 2 — Local changes mode

**Trigger:** no PR reference, no commit-range framing, AND `git status --porcelain` returns non-empty (working tree has uncommitted changes).

**Diff sources:**

- Changed files: `git diff --name-only`
- Diff: `git diff` (combines staged + unstaged)

## Mode 3 — Branch comparison mode

**Trigger:** no PR reference, no commit-range framing, AND `git status --porcelain` returns empty (clean working tree).

**Diff sources:**

- Current branch: `git rev-parse --abbrev-ref HEAD` (needed for the Step 9 filename)
- Base ref: `git rev-parse --abbrev-ref origin/HEAD` (yields e.g. `origin/main`)
- Changed files: `git diff origin/HEAD --name-only`
- Diff: `git diff origin/HEAD`

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
   - **Explicit refs** → use them verbatim after validating each with `git rev-parse <ref>`.

3. **Confirm with the user before launching subagents.** Print the `<from>..<to>` range (with short SHAs), the commit count, and the changed-file list, then invoke `AskUserQuestion` to confirm before proceeding. Reason: the multi-agent pipeline is expensive — a wrong range wastes substantial tokens and time, and the natural-language inputs leave room for misinterpretation that subagents cannot recover from.

**Diff sources (after confirmation):**

- Commits in range (for context only, not validation): `git log <from>..<to> --oneline`
- Changed files: `git diff <from>..<to> --name-only`
- Diff (cumulative across the range): `git diff <from>..<to>`

**Interpretation of "introduced by this change" in commit-range mode:** "introduced" means present in the cumulative diff of `<from>..<to>`; "pre-existing" means present at the parent of `<from>`. Step 4 validation subagents must use this interpretation when applying the dismissal rules.
