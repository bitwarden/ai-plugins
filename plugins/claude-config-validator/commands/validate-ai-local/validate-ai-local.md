---
argument-hint: "[base-ref] (defaults to the repository default branch)"
allowed-tools: Read, Write(validation-summary.md), Grep, Glob, Task, Skill, Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git fetch:*), Bash(git rev-parse:*), Bash(git symbolic-ref:*), Bash(git ls-files:*), Bash(ls:*)
description: Validate the Claude Code material you changed locally (plugins, skills, agents, commands, hooks, CLAUDE.md, .claude/) and write the report to a local file
---

Validate the Claude Code material changed in this checkout, the same way the
`bitwarden/gh-actions` [validate-ai](https://github.com/bitwarden/gh-actions/tree/main/validate-ai)
action validates a pull request — but against your working tree, and writing the report
to a local file instead of a pull request comment.

Read `${CLAUDE_PLUGIN_ROOT}/skills/reviewing-claude-config/reference/validate-ai-scope.md`
first. It defines which paths count as Claude material, how to bucket them, which
validations each bucket gates, and the report contract. Follow it exactly.

**Never post anything to GitHub from this command.** Output is local files only.

## 1. Determine the base ref

- If `$ARGUMENTS` is provided, use it as the base ref.
- Otherwise resolve the default branch:
  `git symbolic-ref --quiet refs/remotes/origin/HEAD` → strip `refs/remotes/`; fall back
  to `origin/main` if that fails, and to `main` if there is no `origin` remote.
- Best-effort `git fetch origin <branch>` so the comparison is against current base.
  If the fetch fails (offline, no remote), continue with what is local and note it in
  the report.
- If the resolved base ref does not exist (`git rev-parse --verify`), stop and tell the
  user which ref you tried.

## 2. Collect changed files

Local review covers committed **and** uncommitted work — this is the point of running it
before you push. Take the union of:

```bash
git diff --name-only <base-ref>...HEAD    # committed on this branch
git diff --name-only HEAD                 # staged and unstaged, tracked files
git ls-files --others --exclude-standard  # untracked files
```

Deduplicate, then classify with the scope reference. Report the file counts you found so
the user can see what was in scope.

If nothing matches, write the report saying no Claude-related files changed, tell the
user, and stop.

## 3. Run the bundled script checks

These live in `bitwarden/gh-actions` at
[`validate-ai/scripts/`](https://github.com/bitwarden/gh-actions/tree/main/validate-ai/scripts) —
that directory is their sole source of truth, so never vendor or reimplement them.

Skip this whole section when the repository has no `.claude-plugin/marketplace.json`.

Locate the scripts, in order:

1. `$BW_GH_ACTIONS_PATH/validate-ai/scripts`
2. A sibling checkout: `<repo-root>/../gh-actions/validate-ai/scripts`
3. Neither found — tell the user you need a `gh-actions` checkout, and offer to shallow
   clone it: `git clone --depth 1 https://github.com/bitwarden/gh-actions <tmpdir>`.
   Ask before cloning. If the user declines, skip the script checks and record them as
   skipped in the report.

Cloning and running these scripts is deliberately not pre-approved in this command's
`allowed-tools`, so both will be asked for. They execute shell code that lives outside
this repository; that is worth a prompt, and a user who runs this often can allowlist the
exact commands themselves.

Run each applicable check from the scope reference's gating table, with `REPO_ROOT` set
to this repository (without it the scripts inspect the `gh-actions` checkout and fail on
a path that isn't there):

```bash
REPO_ROOT=<repo-root> bash <scripts>/validate-plugin-structure.sh <changed plugins>
REPO_ROOT=<repo-root> bash <scripts>/validate-marketplace.sh <changed plugins>
REPO_ROOT=<repo-root> bash <scripts>/validate-version-bump.sh <base-ref> <component plugins>
```

Capture each script's exit status and output; a non-zero exit is a failing check, not a
reason to stop. Run every remaining check, then report them all together.

**Local caveat to state in the report when the version-bump check runs:** it reads the
current version from the working tree, so an uncommitted bump counts, but it detects the
changelog entry with `git diff <base-ref>...HEAD`, so an uncommitted `CHANGELOG.md` edit
is not seen and will be reported as missing until you commit it.

## 4. Plugin validation (plugin-validator agent from plugin-dev)

Runs when any plugin directory changed. For each changed plugin, invoke the
`plugin-dev:plugin-validator` agent via the Task tool. It checks:

- `plugin.json` manifest correctness (name, version, required fields) and semantic versioning
- Directory structure and auto-discovery compliance
- Command frontmatter (description, argument-hint, allowed-tools)
- Agent frontmatter (name 3-50 chars lowercase hyphens, description with `<example>` blocks, valid model/color, system prompt > 20 chars)
- Hook JSON schema, event names, and `${CLAUDE_PLUGIN_ROOT}` usage in script paths
- MCP server configurations (valid types, HTTPS/WSS enforcement)
- File organization (README.md presence, no unnecessary files)
- No hardcoded credentials in any plugin file

Validate every changed plugin directory even when only some component types changed.

If the `plugin-dev` plugin is not installed, record this section as skipped with that
reason — do not silently approximate it.

## 5. Skill review (skill-reviewer agent from plugin-dev)

Runs when any `SKILL.md` changed. Invoke the `plugin-dev:skill-reviewer` agent for each
modified skill. It evaluates:

- YAML frontmatter (required: `name`, `description`)
- Description quality: specific trigger phrases, third-person form, appropriate length
- Content quality: word count (target 1,000-3,000 words), imperative writing style
- Progressive disclosure: lean `SKILL.md`, details in `references/`, examples in `examples/`, scripts in `scripts/`
- All referenced files actually exist
- Anti-patterns: vague triggers, bloated `SKILL.md`, missing examples

Same rule as above if `plugin-dev` is unavailable.

## 6. Configuration and security review (reviewing-claude-config)

Runs whenever any component changed. This is the primary review for a repository's own
`.claude/` directory and `CLAUDE.md`, and it also applies to plugin repositories.

Invoke `Skill(claude-config-validator:reviewing-claude-config)` over every changed
`CLAUDE.md` and everything under `.claude/` — skills, agents, commands, hooks, settings —
plus the component files inside changed plugins. It covers:

- Committed secrets (API keys, tokens, passwords) and hardcoded credentials
- Permission scoping in settings files and dangerous command auto-approvals
- Overly broad file access and agent tool grants
- Malformed or non-compliant agent, command, and hook definitions
- CLAUDE.md clarity, structure, and duplication

Unlike a pull request review, the working tree here **is** the change: read every file
directly from the working tree. There is no `.claude-pr/` snapshot to redirect to.

## 7. Write the report

Write the full report to `validation-summary.md` in the current working directory,
following the report contract in the scope reference. Writing it is mandatory — write it
even when everything passed and even when every section was skipped.

Then print a short console summary: the overall result, the count of critical/major/minor
findings, and the path to the report. If any check failed, say plainly that validation
failed and which check failed.
