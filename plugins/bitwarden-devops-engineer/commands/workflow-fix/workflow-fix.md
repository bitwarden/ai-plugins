---
description: Fix GitHub Actions workflow linter findings in one or more workflow files
argument-hint: [file-or-dir] | --repos <repo1,repo2,...>
allowed-tools: Read, Edit, Glob, Grep, Skill, Bash(python3 -m venv:*), Bash(pip install:*), Bash(bwwl:*), Bash(git checkout:*), Bash(git switch:*), Bash(git add:*), Bash(git commit:*), Bash(git push:*), Bash(git diff:*), Bash(git status:*), Bash(gh pr create:*), Bash(gh api:*)
---

## Step 1: Determine Scope

Parse the arguments to determine what to lint and fix:

- **Single file or directory** (e.g., `.github/workflows/build.yml` or `.github/workflows/`): Operate on the current repo only.
- **`--repos <repo1,repo2,...>`** (e.g., `--repos server,clients,android`): Operate on multiple repos sequentially. For each repo, look for its local clone at `~/Documents/Repositories/bitwarden/<repo>`. If a clone is not found there, inform the user and skip that repo.
- **No arguments**: Lint all files in `.github/workflows/` of the current directory.

## Step 2: Set Up Linter

Check if `bwwl` is available:

```bash
bwwl --version
```

If not available, set it up:

```bash
python3 -m venv /tmp/bwwl-venv
source /tmp/bwwl-venv/bin/activate
pip install bitwarden_workflow_linter --quiet
```

## Step 3: For Each Repo in Scope

Repeat Steps 4–9 for each repo. If operating on multiple repos, announce which repo you are currently working on.

## Step 4: Run the Linter

Run `bwwl lint` against all workflow files in scope:

```bash
bwwl lint -f .github/workflows/
```

After the linter runs, remove the files it downloads into the repo directory:

```bash
rm -f actionlint download-actionlint.bash
```

If there are no findings, announce that the repo is already compliant and move to the next repo.

## Step 5: Create a Fix Branch

Only create the fix branch if there are findings to fix:

```bash
git checkout -b fix/workflow-linter-findings
```

## Step 6: Group and Triage Findings

Group findings by rule. Separate them into two categories:

**Mechanical (apply automatically):**
- `name_capitalized`
- `permissions_exist`
- `pinned_job_runner`
- `step_pinned`
- `underscore_outputs`
- `job_environment_prefix`
- `check_pr_target`
- Simple `run_actionlint` findings (single-line shell fixes)

**Judgment required (pause and ask):**
- `step_approved`
- Complex `run_actionlint` findings

## Step 7: Apply Fixes

**For mechanical findings:** Apply all fixes without prompting. Use the `bitwarden-workflow-linter-rules` skill for the correct fix for each rule.

**Exception — `step_pinned`:** Before applying each hash pin:
1. Resolve the SHA via `gh api repos/{owner}/{repo}/commits/{ref} --jq '.sha'`
2. Show the user: the action name, resolved SHA, and verification link (`https://github.com/{owner}/{repo}/commit/{sha}`)
3. Wait for confirmation. If the user provides a different SHA, use that one.

**For judgment findings:** For each one, pause and present the finding clearly. Ask the user which option they want (per the `bitwarden-workflow-linter-rules` skill), then apply their choice.

## Step 8: Review and Create PR

After all fixes are applied:

1. Show a `git diff` of all changes made.
2. Ask the user to confirm they want to proceed with a PR.
3. If confirmed, commit and create the PR:

```bash
git add .github/workflows/
git commit -m "Fix workflow linter findings"
gh pr create \
  --title "Fix workflow linter findings" \
  --body "Automated fixes for findings from the Bitwarden workflow linter (bwwl)." \
  --draft
```

PRs are created as drafts so the user can review before marking ready.

## Step 9: Summary

After processing all repos, output a summary table:

| Repo | Findings Fixed | PRs Created | Skipped / Notes |
|------|---------------|-------------|-----------------|
| ...  | ...           | ...         | ...             |
