---
name: classify-owning-team-review
argument-hint: "<PR#> [<PR#> ...] | <PR URL> | local [--base <ref>] (blank to be asked)"
allowed-tools: AskUserQuestion, Task, Read
description: Classify whether one or more pull requests need review from the team that owns the code they change, and report the results as a table. Use to check the current branch before opening a PR (`local`), to check an open PR before requesting review, or to backtest a module's INTENT.md against merged PRs - phrasings like "does this PR need the owning team", "classify PR 18231", "backtest our INTENT.md against these PRs", "which of these PRs would have needed us". Read-only. Writes one result file per PR and never posts to GitHub.
---

# Classify owning-team review

This skill resolves the pull requests to classify, runs the `owning-team-classifier` agent once per PR, and reports the results as one table. It does not run `gh` or `git` itself. The agent holds those grants.

## Step 1: Resolve the targets

- `local` classifies the current branch's committed changes against its merge base. `--base <ref>` names the base branch, defaulting to `origin/main`. The ref must match `^[A-Za-z0-9][A-Za-z0-9._/-]*$`. If it does not, do not launch the agent: report the value and ask again.

- Take every PR reference from `$ARGUMENTS`. `123`, `#123`, and `https://github.com/<org>/<repo>/pull/123` each yield the bare number `123`.
- If `$ARGUMENTS` has no PR reference, use `AskUserQuestion` to ask for the PR numbers as free text. The agent runs as a subagent and cannot ask questions itself.
- Every number must match `^[0-9]+$`. If one does not, do not launch any agent. Report the value and ask again.
- Run from the root of a checkout of the repository the PRs belong to. The agent reads intent from each PR's base commit in this checkout.

## Step 2: Run the agent

For each PR, invoke the Task tool with `subagent_type: "bitwarden-owning-team-review:owning-team-classifier"`. The prompt is exactly one line for a pull request, or two lines for local changes:

```
TARGET: PR #<number>
```

```
TARGET: local changes
BASE: <ref>
```

Launch the PRs in parallel when there is more than one. Each run writes `owning-team-review-<number>.json` in the working directory, so runs do not collide.

## Step 3: Report

Read each pull request's result file, `owning-team-review-<number>.json`. For local changes, read the JSON from the agent's final message, since local mode writes no file. A missing or unparseable file is a `no-verdict` row. Report one table:

| PR  | Result | Files needing the owner | Kinds | Signals | Reason |
| --- | ------ | ----------------------- | ----- | ------- | ------ |

- **Result** is `owning-team-review`, `any-engineer`, or `no-verdict`.
- **Files needing the owner** lists the files on required entries. The owning team for each is the one `CODEOWNERS` names.
- **Kinds** lists the distinct change kinds across all entries.
- **Signals** lists the distinct signals on required entries.
- **Reason** is the `reason` of the first required entry, or the `no-verdict` reason.

For a backtest, add a final column, **Owner feedback in review**, and leave it empty for the tech lead to fill in. A row where the classifier said `any-engineer` and the owning team commented or asked for changes is a **miss**. Each miss is a candidate for a change to the module's `INTENT.md`.
