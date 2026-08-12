---
argument-hint: "[PR#] | [PR URL] | (blank for the checked-out PR)"
allowed-tools: Read, Write(//tmp/validation-summary.md), Grep, Glob, Task, Skill, Bash(gh pr view:*), Bash(gh pr diff:*), Bash(gh pr list:*), Bash(git rev-parse:*), Bash(printenv GITHUB_ACTIONS), Bash(ls:*)
description: Validate the Claude Code material changed in a pull request (plugins, skills, agents, commands, hooks, CLAUDE.md, .claude/) and report results to the pull request
---

Validate the Claude Code material changed in a pull request. This is the review the
`bitwarden/gh-actions` [validate-ai](https://github.com/bitwarden/gh-actions/tree/main/validate-ai)
action performs; running the command directly performs the same review against a pull
request you name.

Read `${CLAUDE_PLUGIN_ROOT}/skills/reviewing-claude-config/reference/validate-ai-scope.md`
first. It defines which paths count as Claude material, how to bucket them, which
validations each bucket gates, and the report contract. Follow it exactly.

For a review of your own uncommitted work, use `/validate-ai-local` instead.

## 1. Establish context

Resolve, in this order:

- **Repository and pull request number.** From `REPO:` and `PR NUMBER:` lines in the
  surrounding prompt if present; else from `$ARGUMENTS`, accepting `123`,
  `PR #123`, or `https://github.com/org/repo/pull/123`; else from the checked-out branch
  via `gh pr view --json number,baseRefName,headRefName,url`. If none of these resolve a
  pull request, stop and ask which one to validate.
- **Sticky comment ID.** From a `STICKY COMMENT ID:` line in the surrounding prompt.
- **Mode.** You are in **workflow mode** when a sticky comment ID was supplied, or when
  `printenv GITHUB_ACTIONS` reports a value; otherwise **interactive mode**. The mode
  changes only step 6 (where the report goes).

  Workflow mode is the safe default: if the environment check cannot run and the pull
  request context arrived as `REPO:` / `PR NUMBER:` prompt lines rather than from
  `$ARGUMENTS` or the current branch, treat the run as workflow mode. A workflow run
  misread as interactive would post a comment the workflow is also about to post; the
  reverse only means the report waits in a file.

## 2. Collect changed files

If the surrounding prompt already lists the changed files and buckets (`Changed files:`,
`Changed plugins:`, `Agent files changed:`, and so on), that list is authoritative — use
it and do not re-derive it.

Otherwise get the pull request's changed paths with
`gh pr diff <PR> --name-only` and classify them with the scope reference.

If nothing matches, write the report saying no Claude-related files changed and go
straight to step 6.

## 3. Read pull-request-authored configuration from `.claude-pr/`

This rule protects against reviewing the wrong content. It applies whenever a
`.claude-pr/` directory exists at the repository root — which is what
`claude-code-action` creates in workflow mode.

`claude-code-action` replaces these repository-root paths with their base-branch
versions, because pull-request-authored config executes at CLI startup and so cannot be
trusted:

`.claude/`, `CLAUDE.md`, `CLAUDE.local.md`, `.mcp.json`, `.claude.json`, `.gitmodules`,
`.ripgreprc`, `.husky`

It first snapshots the pull request's versions to `.claude-pr/`, preserving the original
layout, specifically so a review agent can inspect them safely.

- Map each changed path at one of those locations by prefixing it: the pull request's
  `.claude/CLAUDE.md` is at `.claude-pr/.claude/CLAUDE.md`, and its root `CLAUDE.md` is
  at `.claude-pr/CLAUDE.md`.
- Quote line numbers and text from the `.claude-pr/` copy, and report the path in its
  original repo-relative form.
- Never quote the working-tree copy of those paths as the pull request's work — it is
  base-branch content, and doing so produces findings about code the contributor did not
  write. A path present in the working tree with no `.claude-pr/` counterpart was deleted
  by this pull request.
- Only those root paths are affected. Everything else — `plugins/`, `.claude-plugin/`,
  `scripts/`, and any nested path such as `plugins/foo/.claude/` — is untouched and is
  read from the working tree as normal.
- If a config file is listed as changed, you are in workflow mode, and `.claude-pr/` does
  not exist at all, stop treating the working tree as the pull request's content and say
  so in the report. That means this rule no longer matches the action's behavior.

In interactive mode with no `.claude-pr/` directory, the working tree is what you read —
so it has to be the pull request's head. Confirm that before reading anything:

```bash
gh pr view <PR> --json headRefOid --jq .headRefOid
git rev-parse HEAD
```

If they differ, stop and tell the user to check the pull request out
(`gh pr checkout <PR>`) before rerunning. Do not review the working tree against a
changed-file list from a different commit — every quoted line would be wrong, in the same
way the workflow-mode rule above guards against.

## 4. Run the validations

Run these in order, each gated as described in the scope reference. A section that
cannot run is recorded as skipped with its reason — never silently omitted.

### 4a. Plugin validation (plugin-validator agent from plugin-dev)

For each changed plugin, invoke the `plugin-dev:plugin-validator` agent via the Task
tool. It checks:

- `plugin.json` manifest correctness (name, version, required fields) and semantic versioning
- Directory structure and auto-discovery compliance
- Command frontmatter (description, argument-hint, allowed-tools)
- Agent frontmatter (name 3-50 chars lowercase hyphens, description with `<example>` blocks, valid model/color, system prompt > 20 chars)
- Hook JSON schema, event names, and `${CLAUDE_PLUGIN_ROOT}` usage in script paths
- MCP server configurations (valid types, HTTPS/WSS enforcement)
- File organization (README.md presence, no unnecessary files)
- No hardcoded credentials in any plugin file

Validate every changed plugin directory even when only some component types changed.

### 4b. Skill review (skill-reviewer agent from plugin-dev)

For each changed `SKILL.md`, invoke the `plugin-dev:skill-reviewer` agent. It evaluates:

- YAML frontmatter (required: `name`, `description`)
- Description quality: specific trigger phrases, third-person form, appropriate length
- Content quality: word count (target 1,000-3,000 words), imperative writing style
- Progressive disclosure: lean `SKILL.md`, details in `references/`, examples in `examples/`, scripts in `scripts/`
- All referenced files actually exist
- Anti-patterns: vague triggers, bloated `SKILL.md`, missing examples

### 4c. Configuration and security review (reviewing-claude-config)

The primary review for a repository's own `.claude/` directory and `CLAUDE.md`, and it
also applies to plugin repositories. Invoke
`Skill(claude-config-validator:reviewing-claude-config)` over every changed `CLAUDE.md`
and everything under `.claude/` — skills, agents, commands, hooks, settings — plus the
component files inside changed plugins. These are exactly the paths step 3 covers, so
read them from `.claude-pr/` when it exists. It covers:

- Committed secrets (API keys, tokens, passwords) and hardcoded credentials
- Permission scoping in settings files and dangerous command auto-approvals
- Overly broad file access and agent tool grants
- Malformed or non-compliant agent, command, and hook definitions
- CLAUDE.md clarity, structure, and duplication

### Structure, marketplace, and version-bump scripts

The `validate-plugin-structure.sh`, `validate-marketplace.sh`, and
`validate-version-bump.sh` checks are not run here — the workflow runs them as dedicated
steps before this review, and their results reach the pull request through the job log
and check status. Note that in the report's checks table so a reader does not read their
absence as a pass. To run them yourself against a local checkout, use
`/validate-ai-local`.

## 5. Write the report

Write the full report to `/tmp/validation-summary.md`, following the report contract in
the scope reference. Use a single Write call.

Writing this file is mandatory. Write it even when everything passed, and even when
every section above was skipped as not applicable. In workflow mode it is the only way
your results reach the pull request: the sticky comment is replaced with its contents.

## 6. Deliver the report

- **Workflow mode:** stop after writing the file. Do not post or edit pull request
  comments yourself — the workflow updates the sticky comment from
  `/tmp/validation-summary.md`.
- **Interactive mode:** upsert the sticky comment yourself. The `gh api` calls below are
  deliberately not pre-approved in this command's `allowed-tools`, so you will be asked
  to approve them — writing to someone's pull request should be a decision the user sees.
  Find the existing comment whose body contains the marker
  `<!-- bitwarden-ai-validation -->`:

  ```bash
  gh api "repos/<owner>/<repo>/issues/<pr>/comments" --paginate \
    --jq "[.[] | select(.body | contains(\"<!-- bitwarden-ai-validation -->\")) | .id] | first // empty"
  ```

  Update it with `gh api -X PATCH repos/<owner>/<repo>/issues/comments/<id>` if found,
  otherwise create one with `gh api -X POST repos/<owner>/<repo>/issues/<pr>/comments`.
  The body is the report followed by a blank line and the marker, so the next run finds
  it. Tell the user the comment URL.

# Final step (required)

Your task is not done until `/tmp/validation-summary.md` exists on disk. If a section did
not apply or a check could not run, still write the file and say so in it. If you have
not written this file, you have not completed the task, no matter what you reported in
your responses.
