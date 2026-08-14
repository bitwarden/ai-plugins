# `/validate-ai-local` - Local Claude Material Validation

## Overview

`/validate-ai-local` runs the [validate-ai](https://github.com/bitwarden/gh-actions/tree/main/validate-ai)
review against your local checkout instead of a pull request. It finds the Claude Code
material you changed — plugins, agents, skills, commands, hooks, `CLAUDE.md`, `.claude/` —
runs the same checks CI runs, and writes the report to the plugin's own data directory.
Nothing is posted to GitHub.

Use it before you push, so a version bump you forgot or an agent frontmatter mistake
shows up on your machine rather than as a red check.

## Usage

```bash
/validate-ai-local [base-ref]
```

### Arguments

- **`[base-ref]`** (optional): Git ref to compare against, e.g. `origin/main` or a tag.
- **No arguments**: resolves the repository's default branch via
  `git symbolic-ref refs/remotes/origin/HEAD`, falling back to `origin/main`.

### Examples

```bash
# Validate everything changed on this branch, plus uncommitted work
/validate-ai-local

# Compare against a specific base
/validate-ai-local origin/release/2026.8
```

## What it covers

| Check                      | Source                                      | Runs when                                                                      |
| -------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------ |
| Plugin structure           | `validate-plugin-structure.sh` (gh-actions) | A `plugins/` directory changed and the repo has a marketplace manifest         |
| Marketplace consistency    | `validate-marketplace.sh` (gh-actions)      | A plugin or the root `.claude-plugin/` changed, and the repo has that manifest |
| Version bump and changelog | `validate-version-bump.sh` (gh-actions)     | Component files changed inside `plugins/`, and the repo has that manifest      |
| Plugin components          | `plugin-dev:plugin-validator` agent         | Any plugin directory changed                                                   |
| Skill quality              | `plugin-dev:skill-reviewer` agent           | Any `SKILL.md` changed                                                         |
| Configuration and security | `reviewing-claude-config` skill             | Any agent, skill, command, hook, `CLAUDE.md`, or `.claude/` file changed       |

Scope rules, gating, and the report format are defined once in
[`reference/validate-ai-scope.md`](../../skills/reviewing-claude-config/reference/validate-ai-scope.md),
shared with `/validate-ai` and kept in step with the action.

## Change detection

Local review deliberately covers more than a pull request diff. The changed-file set is
the union of:

- `git diff --name-only <base-ref>...HEAD` — committed on this branch
- `git diff --name-only HEAD` — staged and unstaged tracked files
- `git ls-files --others --exclude-standard` — untracked files

## Requirements

- **`git`**, with the base ref fetchable or already local.
- **`plugin-dev` plugin** for the plugin and skill validation sections. Install it with
  `/plugin install plugin-dev@claude-code-plugins`, from the `claude-code-plugins`
  marketplace at `anthropics/claude-code`. Without it those sections are reported as
  skipped, not silently dropped.
- **A `bitwarden/gh-actions` checkout** for the three shell checks. The command looks at
  `$BW_GH_ACTIONS_PATH/validate-ai/scripts`, then a sibling `../gh-actions` checkout, and
  otherwise offers to shallow-clone the repository to a temporary directory. Decline and
  those checks are recorded as skipped.
- **`jq`**, used by the bundled scripts.

The scripts are never vendored into this repository —
[`validate-ai/scripts/`](https://github.com/bitwarden/gh-actions/tree/main/validate-ai/scripts)
in `bitwarden/gh-actions` is their sole source of truth, and they are invoked with
`REPO_ROOT` pointed at your checkout.

## Permissions

The command pre-approves read-only inspection only — `git diff`, `git fetch`,
`git rev-parse`, `git symbolic-ref`, `git ls-files`, `date`, `ls` — plus a `Write` scoped
to `~/.claude/plugins/data/*/ai-validation/`, the only directory it writes to. Cloning
`gh-actions` and running its scripts are left out on purpose and will be asked for: that
step executes shell code from outside this repository, and a blanket `Bash(bash:*)` grant
would pre-approve arbitrary commands on the one path that fetches code from the network.
If you run this often, allowlist the exact script invocations yourself.

The `Write` grant is written home-relative rather than as `${CLAUDE_PLUGIN_DATA}/...`
because a permission pattern is only filesystem-absolute in its `~/` or `//` form — the
single leading slash `${CLAUDE_PLUGIN_DATA}` expands to would anchor the rule at your
current directory and never match. Two consequences. The `*` standing in for the plugin's
data directory means the pattern spans any plugin's `ai-validation/` directory rather than
this one's; naming a single directory would require hardcoding the plugin identifier, which
embeds the marketplace you installed from and so differs between installs. And the pattern
is written against `~/.claude`, so if you have relocated that tree with
`CLAUDE_CONFIG_DIR`, the final write asks for permission.

## Known local caveat

`validate-version-bump.sh` reads the current plugin version from your working tree, so an
uncommitted version bump counts. It detects the changelog entry with
`git diff <base-ref>...HEAD`, so an **uncommitted** `CHANGELOG.md` edit is not visible to
it and gets reported as missing until you commit. The command states this in the report
whenever that check runs.

## Output

`${CLAUDE_PLUGIN_DATA}/ai-validation/<repo>-<timestamp>-validation.md`, containing:

- Overall result and what was validated against which base
- Findings grouped as critical, major, and minor, each with `file:line` and a fix
- A checks table showing what ran, what failed, and what was skipped and why

`${CLAUDE_PLUGIN_DATA}` resolves to this plugin's directory under
`~/.claude/plugins/data/`. Reports land there rather than in the checkout you validated,
which can be any repository — so no repository needs a `.gitignore` entry for them, and
reports from different checkouts do not overwrite each other. The trade-off is that they
accumulate somewhere you have to go looking for; the command prints the path it wrote each
time. `claude plugin uninstall <plugin>` deletes that directory unless you pass
`--keep-data`.

The file is always written, including when everything passes and when every section was
skipped, and it ends with `<!-- validation-complete -->` so a local report matches what
`/validate-ai` produces. In CI that marker is what tells the action a report is finished.

## Differences from `/validate-ai`

|                          | `/validate-ai-local`                                              | `/validate-ai`                                                                       |
| ------------------------ | ----------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| Input                    | Working tree + branch commits                                     | A pull request                                                                       |
| Shell script checks      | Runs them                                                         | Left to the workflow's own steps                                                     |
| `.claude-pr/` trust rule | Not applicable                                                    | Applied when the snapshot exists                                                     |
| Output                   | A timestamped report under `${CLAUDE_PLUGIN_DATA}/ai-validation/` | `/tmp/validation-summary.md`, plus a sticky pull request comment in interactive mode |

## Related documentation

- [Claude Config Validator plugin README](../../README.md)
- [`reviewing-claude-config` skill](../../skills/reviewing-claude-config/SKILL.md)
- [validate-ai action](https://github.com/bitwarden/gh-actions/tree/main/validate-ai)

## Troubleshooting

### "Invalid base ref"

The ref could not be resolved. Fetch it first (`git fetch origin main`) or pass an
explicit ref: `/validate-ai-local origin/main`.

### Script checks always skipped

No `gh-actions` checkout was found and the clone was declined. Set
`BW_GH_ACTIONS_PATH` to your checkout, or clone `bitwarden/gh-actions` next to this
repository.

### "Plugin directory not found" from a script

`REPO_ROOT` did not reach the script. Each script defaults `REPO_ROOT` to the parent of
its own `scripts/` directory — `validate-ai/` inside `gh-actions` — so it must be
overridden to point at the repository being validated.

### Plugin or skill sections reported as skipped

The `plugin-dev` plugin is not installed. Install it with
`/plugin install plugin-dev@claude-code-plugins`.
