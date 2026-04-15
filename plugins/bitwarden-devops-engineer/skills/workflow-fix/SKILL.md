---
name: workflow-fix
description: >
  Apply fixes for workflow linter findings identified by the workflow-audit skill. Applies mechanical
  fixes automatically, pauses for judgment calls, verifies with a re-lint, and creates draft PRs.
  Run the workflow-audit skill first to identify findings before using this skill.

  <example>
  User: Go ahead and fix the linter findings from the audit
  Action: Trigger workflow-fix to apply fixes and create PRs
  </example>

  <example>
  User: Fix the workflow linter issues in server and clients
  Action: Trigger workflow-fix for those repos
  </example>
allowed-tools: Read, Edit, Glob, Grep, Skill, Bash(bwwl:*), Bash(gh api --method GET *), Bash(git checkout:*), Bash(git add .github/:*), Bash(git commit:*), Bash(git push:*), Bash(git diff:*), Bash(git status:*), Bash(gh pr create:*)
---

## Rules

- **No mutating API calls without confirmation.** `gh api` GET requests are allowed freely. Any call using `-X POST`, `-X PUT`, `-X PATCH`, or `-X DELETE` must be shown to the user and approved before execution.
- **Never force-push, delete branches, or delete repositories.**
- **Only modify files under `.github/`.** Do not touch application code, scripts, or configuration outside of workflow files.
- **Show a diff and get confirmation before every commit.**
- **All PRs must be created as drafts.**
- **Flag uncertainty.** If a finding is ambiguous or a fix could break a workflow, stop and ask rather than guessing.

## Step 1: Verify Prerequisites

Check if `bwwl` is available:

```bash
bwwl --version
```

If the command is not found, stop and inform the user that `bwwl` must be installed before continuing. Do not attempt to install it.

## Step 2: Determine Scope

Parse the user's request to determine what to fix:

- **Single file or directory**: Operate on the current repo only.
- **Multiple repos** (e.g., "server, clients, android"): Operate on each repo sequentially. Ask the user for the base directory where their repos are cloned. For each repo, look for its local clone at `<base-dir>/<repo>`. If a clone is not found, inform the user and skip that repo.
- **No specific target**: Fix all findings in `.github/workflows/` of the current directory.

If the user has not run the `workflow-audit` skill first, run the linter now to identify findings before proceeding.

## Step 3: For Each Repo in Scope

Repeat Steps 4–7 for each repo. Announce which repo is being worked on.

## Step 4: Create a Fix Branch

Only create the fix branch if there are findings to fix:

```bash
git checkout -b fix/workflow-linter-findings
```

## Step 5: Apply Fixes

Consult the `bitwarden-workflow-linter-rules` skill for the correct fix for each rule.

**For mechanical findings:** Apply all fixes without prompting.

**Exception — `step_pinned`:** Before applying each hash pin, follow the `step_pinned` fix procedure from the `bitwarden-workflow-linter-rules` skill (resolve SHA via `gh api`, show verification link, wait for user confirmation).

**For judgment findings:** For each one, pause and present the finding clearly. Ask the user which option they want (per the `bitwarden-workflow-linter-rules` skill), then apply their choice.

## Step 6: Verify Fixes

Re-run the linter to confirm all findings are resolved:

```bash
bwwl lint -f .github/workflows/
```

If errors remain, analyze and fix them. Repeat until clean.

## Step 7: Review and Create PR

After all fixes are applied:

1. Show a `git diff` of all changes made.
2. Ask the user to confirm they want to proceed with a PR.
3. If confirmed:

```bash
git add .github/workflows/
git commit -m "Fix workflow linter findings"
gh pr create \
  --title "Fix workflow linter findings" \
  --body "Automated fixes for findings from the Bitwarden workflow linter (bwwl)." \
  --draft
```

## Step 8: Summary

After processing all repos, output a summary table:

| Repo | Findings Fixed | PRs Created | Skipped / Notes |
| ---- | -------------- | ----------- | --------------- |
| ...  | ...            | ...         | ...             |
