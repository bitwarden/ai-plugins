# `/validate-ai` - Pull Request Claude Material Validation

## Overview

`/validate-ai` validates the Claude Code material changed in a pull request — plugins,
agents, skills, commands, hooks, `CLAUDE.md`, `.claude/` — and reports the result to that
pull request. It is the review the
[validate-ai](https://github.com/bitwarden/gh-actions/tree/main/validate-ai) GitHub
Action performs org-wide, expressed as a command so the action and a human get the same
review from the same source.

For your own uncommitted work, use [`/validate-ai-local`](../validate-ai-local/README.md).

## Usage

```bash
/validate-ai [PR#] | [PR URL]
```

### Arguments

- **`[PR#]`** (optional): pull request number, e.g. `123`
- **`[PR URL]`** (optional): full URL, e.g. `https://github.com/bitwarden/clients/pull/123`
- **No arguments**: uses the pull request for the current branch

### Examples

```bash
# Validate a specific pull request
/validate-ai 196

# By URL
/validate-ai https://github.com/bitwarden/ai-plugins/pull/196

# The pull request for the current branch
/validate-ai
```

## Two modes

The command detects its context and changes only where the report goes.

**Workflow mode** — a `STICKY COMMENT ID:` was supplied in the prompt, or
`GITHUB_ACTIONS` is set. The command writes `/tmp/validation-summary.md` and posts
nothing; the workflow replaces its sticky comment with that file's contents. This is how
the action drives it.

**Interactive mode** — anything else. The command writes the same file and then upserts
the sticky comment itself, matching on the `<!-- bitwarden-ai-validation -->` marker so
repeat runs update one comment instead of piling up new ones.

## What it covers

| Check                      | Source                              | Runs when                                                                |
| -------------------------- | ----------------------------------- | ------------------------------------------------------------------------ |
| Plugin components          | `plugin-dev:plugin-validator` agent | Any plugin directory changed                                             |
| Skill quality              | `plugin-dev:skill-reviewer` agent   | Any `SKILL.md` changed                                                   |
| Configuration and security | `reviewing-claude-config` skill     | Any agent, skill, command, hook, `CLAUDE.md`, or `.claude/` file changed |

Structure, marketplace, and version-bump validation are **not** run here. The workflow
runs those three shell scripts as dedicated steps before this review, and their results
reach the pull request through the job log and check status. The report's checks table
says so explicitly, so their absence is never read as a pass. To run them against a
checkout, use `/validate-ai-local`.

Scope rules, gating, and the report format are defined once in
[`reference/validate-ai-scope.md`](../../skills/reviewing-claude-config/reference/validate-ai-scope.md),
shared with `/validate-ai-local` and kept in step with the action.

## Where pull-request configuration is read from

`claude-code-action` treats pull-request-authored Claude configuration as untrusted,
because `.claude/settings.json`, `.mcp.json`, and hooks execute at CLI startup before any
tool-permission gating. Before the review runs it replaces these repository-root paths
with their base-branch versions:

`.claude/`, `CLAUDE.md`, `CLAUDE.local.md`, `.mcp.json`, `.claude.json`, `.gitmodules`,
`.ripgreprc`, `.husky`

It snapshots the pull request's versions to `.claude-pr/` first, preserving the original
layout, so the pull request's `.claude/CLAUDE.md` is available at
`.claude-pr/.claude/CLAUDE.md`.

The command therefore reads those paths from `.claude-pr/` whenever that directory exists
and reports them under their original repo-relative names. Reading them from the working
tree yields base-branch content, producing findings about lines the contributor never
wrote. Everything outside that list — `plugins/`, `.claude-plugin/`, `scripts/`, and
nested paths such as `plugins/foo/.claude/` — is read from the working tree.

If a config file changed, the run is in workflow mode, and no `.claude-pr/` snapshot
exists, the command says so in its report rather than silently reviewing base-branch
content.

## Output

`/tmp/validation-summary.md`, containing:

- Overall result and what was validated
- Findings grouped as critical, major, and minor, each with `file:line` and a fix
- A checks table showing what ran, what failed, and what was skipped and why

The file is always written, including when everything passes and when every section was
skipped — in workflow mode it is the only path results have to the pull request.

It ends with `<!-- validation-complete -->`. The action uses that marker to tell a finished
report from one abandoned mid-review: a report without it is quarantined rather than posted,
and the check fails. For the same reason the command writes the file once, at the very end,
and runs its subagents synchronously. A subagent still in flight when the turn ends is
killed in a headless run, and there is no retry step to recover from it.

Synchronous is not the same as one at a time. The plugin and skill reviews are dispatched
together in one message so they overlap, since the review is bounded by the job's timeout
rather than by its turn count.

## Requirements

- **GitHub CLI (`gh`)**, authenticated, with access to the repository
- **`plugin-dev` plugin** for the plugin and skill sections. Install it with
  `/plugin install plugin-dev@claude-code-plugins`, from the `claude-code-plugins`
  marketplace at `anthropics/claude-code`. Without it those sections are reported as
  skipped, not silently dropped.

## Permissions

The command pre-approves only read-only inspection: `gh pr view`, `gh pr diff`,
`git rev-parse`, `ls`, and reading `GITHUB_ACTIONS`. An `Edit(//tmp/validation-summary.md)`
rule scopes the one file the command produces, `/tmp/validation-summary.md` — the doubled
slash is permission-rule syntax for "absolute from the filesystem root", not part of the
path. It is an `Edit` rule rather than a `Write` one because Claude Code consults
`Edit(path)` and `Read(path)` rules only, and an `Edit` rule covers every built-in tool that
edits files; that needs Claude Code 2.1.210 or later. The `gh api`
calls that create or edit the sticky comment in interactive mode are left out on purpose,
so writing to a pull request is a decision you see and approve. Allowlist them yourself if
you run this often.

`/tmp/validation-summary.md` is a fixed path in a world-writable directory, and the `Edit`
rule pre-approves writing it. That is the right trade for the workflow this command serves,
where the `bitwarden/gh-actions` steps read that exact path and the runner is ephemeral and
single-tenant. On a shared host, the report is world-readable while it sits there. A
pre-planted symlink is not the same exposure: an allow rule applies only when the symlink
and its target both match, so one pointing anywhere else prompts rather than being followed.
Prefer `/validate-ai-local` on a multi-user machine; it writes under your own
`${CLAUDE_PLUGIN_DATA}`.

Reviewing a pull request means reading contributor-authored configuration, which is why
the grants stay narrow: a broad `Bash(gh api:*)` would prefix-match a `DELETE` just as
happily as a comment update.

## Related documentation

- [Claude Config Validator plugin README](../../README.md)
- [`reviewing-claude-config` skill](../../skills/reviewing-claude-config/SKILL.md)
- [`/validate-ai-local`](../validate-ai-local/README.md)
- [validate-ai action](https://github.com/bitwarden/gh-actions/tree/main/validate-ai)

## Troubleshooting

### "No pull request found"

The current branch has no open pull request. Pass a number or URL explicitly, or check
`gh pr status`.

### The sticky comment did not update

In workflow mode the command never posts — check that the workflow's comment step ran and
that `/tmp/validation-summary.md` was produced. In interactive mode, confirm `gh auth
status` and that the token can write pull request comments.

### Findings quote lines the contributor did not write

The `.claude-pr/` redirect was not applied. Confirm the snapshot exists at the repository
root and that the finding's path is one of the redirected root paths.
