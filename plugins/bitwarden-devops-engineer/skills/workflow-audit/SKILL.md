---
name: workflow-audit
description: >
  Run the Bitwarden workflow linter (bwwl) against one or more repos and report findings.
  Strictly read-only — does not modify any files. Categorizes findings as mechanical or judgment
  using the bitwarden-workflow-linter-rules skill. Supports single repo, multiple repos, or
  single file/directory scope.

  <example>
  User: Run the workflow linter on the server repo
  Action: Trigger workflow-audit for that repo
  </example>

  <example>
  User: Lint the workflows across server, clients, and android
  Action: Trigger workflow-audit in multi-repo mode
  </example>
allowed-tools: Read, Glob, Grep, Skill, Bash(bwwl:*)
---

## Rules

- **This skill is strictly read-only.** Do not modify, create, or delete any files.
- **Flag uncertainty.** If a finding is ambiguous, note it in the report rather than guessing.

## Step 1: Verify Prerequisites

Check if `bwwl` is available:

```bash
bwwl --version
```

If the command is not found, stop and inform the user that `bwwl` must be installed before continuing. Do not attempt to install it.

## Step 2: Determine Scope

Parse the user's request to determine what to lint:

- **Single file or directory** (e.g., `.github/workflows/build.yml` or `.github/workflows/`): Operate on the current repo only.
- **Multiple repos** (e.g., "server, clients, android"): Operate on each repo sequentially. Ask the user for the base directory where their repos are cloned. For each repo, look for its local clone at `<base-dir>/<repo>`. If a clone is not found, inform the user and skip that repo.
- **No specific target**: Lint all files in `.github/workflows/` of the current directory.

## Step 3: Run the Linter

For each repo in scope, run:

```bash
bwwl lint -f .github/workflows/
```

Capture both stdout and stderr. If operating on multiple repos, announce which repo is being linted.

## Step 4: Parse and Categorize Findings

From the linter output, produce a structured list of findings. Group by file and rule. Consult the `bitwarden-workflow-linter-rules` skill to categorize each finding:

**Mechanical** (can be auto-fixed):

- `name_capitalized`, `permissions_exist`, `pinned_job_runner`, `step_pinned`, `underscore_outputs`, `job_environment_prefix`, `check_pr_target`
- Simple `run_actionlint` findings (single-line shell fixes)

**Judgment** (requires user input):

- `name_exists`, `step_approved`, complex `run_actionlint` findings

## Step 5: Report

Output a summary table per repo:

| File | Finding | Rule | Category |
| ---- | ------- | ---- | -------- |
| ...  | ...     | ...  | ...      |

Include totals: mechanical findings, judgment findings, and repos with no issues.

Inform the user that they can use the `workflow-fix` skill to apply fixes based on these findings.
