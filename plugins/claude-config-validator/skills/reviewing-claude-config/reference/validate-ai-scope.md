# Changeset Scope and Report Contract

Shared rules for validating a whole changeset of Claude Code material rather than a
single file. The `/validate-ai` and `/validate-ai-local` commands both read this file,
and both mirror the `bitwarden/gh-actions` [validate-ai](https://github.com/bitwarden/gh-actions/tree/main/validate-ai)
action, so the three stay in step.

## Which files count as Claude material

A changed path is in scope when it matches any of these patterns:

| Pattern                      | What it covers                                          |
| ---------------------------- | ------------------------------------------------------- |
| `^plugins/`                  | Anything inside a plugin directory                      |
| `(^\|/)\.claude-plugin/`     | Plugin and marketplace manifests                        |
| `(^\|/)\.claude/`            | Per-repo Claude configuration                           |
| `(^\|/)CLAUDE\.md$`          | Project, workspace, and directory-scoped guidance       |
| `(^\|/)agents/.*\.md$`       | Agents (`agents/<name>/AGENT.md` or `agents/<name>.md`) |
| `(^\|/)skills/.*/SKILL\.md$` | Skills                                                  |
| `(^\|/)commands/.*\.md$`     | Slash commands                                          |
| `(^\|/)hooks\.json$`         | Hook definitions                                        |
| `^scripts/validate-`         | Repository validation scripts                           |

If no changed path matches, there is nothing to validate — say so and stop.

## Buckets derived from the in-scope paths

Classify the in-scope paths into these buckets. They drive which validations run.

- **Agent files** — `(^|/)agents/.*\.md$`. Agents appear both as `agents/<name>/AGENT.md`
  and as `agents/<name>.md`, so match any Markdown file under an `agents/` directory.
- **Skill files** — `(^|/)skills/.*/SKILL\.md$`
- **Command files** — `(^|/)commands/.*\.md$`
- **Hook files** — `(^|/)hooks\.json$`
- **Config files** — `(^|/)CLAUDE\.md$` or `(^|/)\.claude/`
- **Changed plugins** — the first two path segments of every changed `plugins/` path,
  deduplicated (`plugins/<name>`)
- **Component plugins** — changed plugins that had an agent, skill, command, or hook
  file change. Version-bump enforcement applies to these only, so a docs-only edit
  under `plugins/<name>` does not force a version bump.
- **Marketplace changed** — any changed path under a root `.claude-plugin/`

**Components changed** means at least one of agent, skill, command, hook, or config
files is non-empty. That is the trigger for the AI-driven review.

## Gating

| Validation                    | Runs when                                                                           |
| ----------------------------- | ----------------------------------------------------------------------------------- |
| Plugin structure (script)     | Changed plugins is non-empty **and** the repo has `.claude-plugin/marketplace.json` |
| Marketplace (script)          | Changed plugins **or** marketplace changed, **and** the repo has that manifest      |
| Version bump (script)         | Component plugins is non-empty **and** the repo has that manifest                   |
| Plugin validation (AI)        | Changed plugins is non-empty                                                        |
| Skill review (AI)             | Skill files is non-empty                                                            |
| Configuration & security (AI) | Components changed                                                                  |

A repository with no `.claude-plugin/marketplace.json` never runs the script checks —
it may have a `plugins/` directory for unrelated reasons. It still gets the full
AI-driven review.

## Report contract

Write a single structured Markdown document. It is the only output that reaches the
reader, so it must exist even when every section was skipped and even when everything
passed.

- Categorize issues by severity: **critical**, **major**, **minor**
- Give the exact file path and line for each issue, in its original repo-relative form
- Provide specific remediation guidance for each violation
- Distinguish errors (must fix) from warnings (should fix)
- State explicitly which sections ran, which were skipped, and why
- When a check could not run (missing tool, unavailable plugin, denied permission), say
  so in the report rather than omitting the section — a silent omission reads as a pass
- If all checks pass, confirm with a summary of what was validated

Suggested structure:

```markdown
## Claude Code validation

**Result:** Pass | Issues found

[One or two sentences on what was validated and against what base.]

### Critical

- `path/to/file.md:12` — [Issue]. **Fix:** [Remediation].

### Major

- ...

### Minor

- ...

### Checks run

| Check                    | Status                            |
| ------------------------ | --------------------------------- |
| Plugin structure         | Passed / Failed / Skipped ([why]) |
| Marketplace              | ...                               |
| Version bump             | ...                               |
| Plugin validation (AI)   | ...                               |
| Skill review (AI)        | ...                               |
| Configuration & security | ...                               |
```

## Severity mapping

The AI-driven checks classify findings as CRITICAL / IMPORTANT / SUGGESTED / OPTIONAL
(see `reference/priority-framework.md`). Map them onto the report's three severities:

| Source classification | Report severity | Error or warning |
| --------------------- | --------------- | ---------------- |
| CRITICAL              | critical        | Error            |
| IMPORTANT             | major           | Error            |
| SUGGESTED             | minor           | Warning          |
| OPTIONAL              | minor           | Warning          |

A failing script check is always an error. Its severity is critical when it blocks
plugin loading (malformed manifest, missing required file) and major otherwise
(missing version bump, missing changelog entry).
