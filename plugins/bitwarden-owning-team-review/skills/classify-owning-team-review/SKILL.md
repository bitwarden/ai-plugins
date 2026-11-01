---
name: classify-owning-team-review
argument-hint: "<PR#> [<PR#> ...] | <PR URL> | local [--base <ref>] (blank to be asked)"
allowed-tools: AskUserQuestion, Task, Bash(bash ${CLAUDE_PLUGIN_ROOT}/scripts/prepare-context.sh *)
description: Classify whether one or more pull requests need review from the team that owns the code they change, and report the results as a table. Use to check the current branch before opening a PR (`local`), to check an open PR before requesting review, or to backtest a module's INTENT.md against merged PRs - phrasings like "does this PR need the owning team", "classify PR 18231", "backtest our INTENT.md against these PRs", "which of these PRs would have needed us". Read-only. Never posts to GitHub and writes nothing in the repository.
---

# Classify owning-team review

This skill resolves the pull requests to classify, prepares a read-only context for each, runs the `owning-team-classifier` agent once per context, and reports the results as one table. The only command it runs is the plugin's `prepare-context.sh`. The agent itself has no shell.

## Step 1: Resolve the targets

Run from the root of a checkout of the repository the pull requests belong to.

- **`local`** classifies the current branch's committed changes against its merge base. `--base <ref>` names the base branch, and defaults to `origin/main`. The ref must match `^[A-Za-z0-9][A-Za-z0-9._/-]*$`. If it does not, do not run anything: report the value and ask again.
- **A number** such as `123` or `#123` classifies that pull request in this checkout's repository.
- **A URL** such as `https://github.com/<owner>/<repo>/pull/123` classifies pull request `123`, and names `<owner>/<repo>` as the repository it belongs to. Pass that repository to the script in Step 2, which stops when this checkout belongs to a different one. A URL never silently classifies another repository's pull request with the same number.
- If `$ARGUMENTS` has no target, use `AskUserQuestion` to ask for one. The agent runs as a subagent and cannot ask questions itself.

Every number must match `^[0-9]+$`, and every `<owner>/<repo>` must match `^[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9._-]+$`. If a value does not match, do not run anything. Report the value and ask again.

## Step 2: Prepare a context for each target

Run the plugin's script once per target, from the checkout root:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/prepare-context.sh pr <number> [<owner>/<repo>]
bash ${CLAUDE_PLUGIN_ROOT}/scripts/prepare-context.sh local [<ref>]
```

The script prints the path of a new context directory. It holds the diff, the changed files, CODEOWNERS, and an export of the base commit. It never fetches the pull request's title or body. If the script fails, report its message as that target's `no-verdict` row and continue with the others.

## Step 3: Run the agent

For each context, invoke the Task tool with `subagent_type: "bitwarden-owning-team-review:owning-team-classifier"`. The prompt is exactly one line:

```
CONTEXT: <context directory>
```

Launch the targets in parallel when there is more than one.

## Step 4: Report

Each agent prints its result as a single JSON object as its final message. Parse it from the first line that begins with `{`, ignoring any sentence before it. A missing or unparseable result is a `no-verdict` row. Report one table:

| PR  | Result | Files needing the owner | Kinds | Signals | Reason |
| --- | ------ | ----------------------- | ----- | ------- | ------ |

- **Result** is `owning-team-review`, `any-engineer`, or `no-verdict`.
- **Files needing the owner** lists the files on required entries, grouped by each entry's `owners`.
- **Kinds** lists the distinct change kinds across all entries.
- **Signals** lists the distinct signals on required entries.
- **Reason** is the `reason` of the first required entry, or the `no-verdict` reason.

For a backtest, add a final column, **Owner feedback in review**, and leave it empty for the tech lead to fill in. A row where the classifier said `any-engineer` and the owning team commented or asked for changes is a **miss**. Each miss is a candidate for a change to the module's `INTENT.md`.
