# Changelog

All notable changes to the Claude Config Validator Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-08-19

### Added

- Scope fence limiting findings to what a changeset introduced or worsened, stated in `SKILL.md`, the scope reference, and both commands' subagent prompts
- Filter step dropping findings that are pre-existing, unspecific, unverified, already covered by another checker, or whose remediation is "no change"
- Four targeted review skills: `reviewing-agent-definitions`, `reviewing-command-definitions`, `reviewing-runtime-configuration`, `reviewing-project-guidance`
- Both commands state that the report is the deliverable and that re-validation pins the original baseline
- Security floor on the verdict: a finding that widens a permission, tool grant, or hook capability sets `Issues found` at whatever severity it carries
- CRITICAL and security findings are exempt from the filter's nitpick, coverage, and severity tests
- Fallback routing row, so an in-scope path with no targeted skill — skill support files under `reference/`, `examples/`, `scripts/` — is read rather than dropped
- CWE-1427 untrusted-data boundary in each of the four targeted skills, which can be invoked directly and cannot rely on the router being in context

### Changed

- **Breaking**: `reviewing-claude-config` is a router; the `checklists/` and `examples/` directories are gone
- **Breaking**: `reviewing-claude-config` no longer reviews `SKILL.md` — `plugin-dev:skill-reviewer` owns it
- The verdict is `Issues found` only on a CRITICAL finding or one that weakens security; a quality-only IMPORTANT maps to a warning
- IMPORTANT narrowed to functional defects and security regressions; vague instructions, missing examples, duplicated documentation, poor progressive disclosure, and missing structured-thinking blocks are SUGGESTED
- Marketplace escalation no longer raises readability findings to CRITICAL
- `reviewing-claude-config` holds `Skill` in `allowed-tools`
- `/validate-ai` trimmed, cutting rationale duplicated in the scope reference

### Fixed

- Agent and command frontmatter review is skipped only where `plugin-dev:plugin-validator` actually ran, not wherever the file sits inside a plugin
- Permission examples use `Tool(specifier)` rules under `permissions.allow` / `deny`, replacing a top-level `autoApprovedTools` array and bare `Tool:specifier` rules that Claude Code does not read, in `reviewing-runtime-configuration`, `reviewing-project-guidance`, `security-patterns.md`, and `claude-code-requirements.md`
- `npm install` and `./gradlew test` are no longer described as read-only or idempotent, and no longer appear in a list offered as the safe default
- Hook `timeout` is documented as seconds, and an unfamiliar hook `type` is treated as a question to confirm rather than a defect
- Routing table qualifies all four targeted skills as `claude-config-validator:<name>`, matches the command bucket's `commands/**/*.md` at any depth, and excludes `README.md`
- Targeted skills reference the router by relative path, which they can resolve without a `Skill` grant
- `/validate-ai` section 4b records itself as skipped when `plugin-dev` is unavailable, as 4a already did
- Verdict statements in `SKILL.md` Core Principles and the changelog carry the security floor
- Agent tool grants reaching credentials or destructive commands are CRITICAL in `priority-framework.md`, matching what `reviewing-agent-definitions` already said
- Permission rule grammar is `Tool` or `Tool(specifier)`. The bare form is valid and is the broadest grant available, so `deny: ["WebFetch"]` is a control rather than a defect; the CRITICAL finding is scoped to the two forms Claude Code genuinely does not read
- `//` is documented as the absolute path prefix, and a single leading `/` as relative to the settings file's directory, which had been mixed within one release
- Detection greps, `detect-broad-permissions.sh`, and the shipped `security-scan.sh` match the real schema; all three previously reported a filesystem-wide grant as scoped
- Hook schema and script-path review is skipped only where `plugin-dev:plugin-validator` actually ran, matching the agent and command skills
- `reviewing-command-definitions` has a numbered frontmatter pass rather than a promise
- `Skill(bitwarden-security-engineer:detecting-secrets)` is qualified, which it needs now that the router holds `Skill`
- Findings duplicated at the same `file:line` by two checkers merge at the higher severity instead of being dropped or double-reported
- `CLAUDE.md` path-resolution moved to the structure pass, out from under "Length alone is not a finding"
- Harness-loosening directives in `CLAUDE.md` are a checkbox with a CRITICAL severity and a `priority-framework.md` row, not prose
- Agent frontmatter covers `<example>` blocks and `color` where the pass is ours, treats a full model identifier as valid, and judges an omitted `tools` field on what it grants
- Worked severity examples re-anchored away from `SKILL.md` and `checklists/`, both out of scope after this release
- Targeted skills state that a direct invocation skips the router's secret scan and filter, and cite `claude-code-requirements.md` for frontmatter and rule syntax
- Teaching credentials match the quantifiers in the regexes the skills point at
- Argument interpolation into a `` !`cmd` `` shell string is a finding regardless of quoting: CRITICAL unquoted, IMPORTANT quoted. Quoting stops word-splitting and `;` chaining but not command substitution or quote breakout, so the guidance now recommends stdin or a validated allowlist
- Command frontmatter is optional, so YAML that does not parse is CRITICAL while a missing `description` is SUGGESTED
- Bare-tool-rule detection reads `permissions.allow` rather than the whole file, so a bare rule confined to `deny` no longer fails the scan; the check records itself as skipped where `jq` is unavailable
- Secret detection excludes placeholder text, so the plugin's own teaching examples no longer register as live credentials after moving inline
- `model` admits full identifiers and the reviewed tool list includes `Task`, `Skill`, `TodoWrite`, and `NotebookEdit`, matching what the skills expect
- Severity rows for over-broad permissions are qualified to `allow`, with a row recording that a bare or sensitive-path rule in `deny` is the control rather than a finding
- `/validate-ai-local` carries the full CWE-1427 boundary rather than a paraphrase that dropped the identifier and the critical-finding instruction
- Hook input guidance states the three cases that actually differ, verified by execution: a quoted value in a shell variable used directly is safe, the same value handed to a nested shell is not, and slash-command substitution has no safe quoted form. `reviewing-command-definitions` no longer claims the sibling applies an identical rule
- A broken `CLAUDE.md` pointer is IMPORTANT rather than CRITICAL, since it breaks no load; a broken `@path` import stays CRITICAL
- The settings routing row is qualified for depth, so a nested `packages/app/.claude/settings.json` reaches the targeted skill instead of the fallback
- The routed path runs the deeper settings passes and lets the router's Step 4 merge overlaps, rather than suppressing them as already covered by a shallow `Grep` sweep
- `reviewing-agent-definitions` owns Passes 1 and 3 to 5, since `plugin-dev` checks that a description and system prompt exist rather than whether they are any good
- `priority-framework.md` has hook and settings severity tables; it previously contained no occurrence of "hook" while a skill delegated hook classification to it
- Non-rule settings fields that execute or bypass are a pass of their own: `permissions.defaultMode`, `additionalDirectories`, `apiKeyHelper`, `statusLine.command`, `enableAllProjectMcpServers`, and `env`. `bypassPermissions` in a committed settings file is CRITICAL
- The command tier is stated once, in `security-patterns.md`, with `reviewing-runtime-configuration` pointing at it. `npm install`, `npm ci`, `./gradlew build`, and `./gradlew test` are one tier: a lock file makes `npm ci` reproducible, not inert
- Tool-name enumerations include `Task`, `Skill`, `TodoWrite`, and `NotebookEdit`, with `Task` ranked at or above `Bash` because it escapes the grant under review
- `claude-code-requirements.md` has a `### Commands` subsection, which the command skill already pointed at for frontmatter fields
- The documented bare-rule detector gates its verdict on the skip, exiting 2 rather than printing a pass for a check that could not run
- `/validate-ai` writes the report rather than asking which pull request to validate when there is nobody to ask
- Hook severity is consistent across the table, the pre-flight checklist, the prose, and `priority-framework.md`: a quoted value consumed directly by the command is not a finding, an unquoted interpolation is CRITICAL, and a nested shell is CRITICAL either way
- `priority-framework.md` no longer elevates permission severities wholesale in Security Context, which had overridden the IMPORTANT tier of the per-field tables and falsified the security floor's stated reason for existing
- Broken references are split by consequence: a load failure or a broken `CLAUDE.md` `@path` import is CRITICAL, a plain-path pointer in prose is IMPORTANT
- `permissions.defaultMode: acceptEdits` is IMPORTANT rather than CRITICAL, since projects opt into it deliberately
- Agent tool-access review covers `Skill` alongside `Task`; both escape the grant under review rather than widening it
- Standalone-install instructions copy all five skill directories and note that the plugin-qualified routing names must be reduced to bare names
- Step 3 says what to do when a targeted skill cannot be invoked, and routes plugin manifests to `plugin-dev:plugin-validator` explicitly
- Unrecognized hook event names are confirmed rather than reported, matching the treatment already given to an unfamiliar hook `type`
- Targeted skill descriptions carry natural-language triggers and state that the router is the preferred entry point

- The documented bare-rule detector guards on `jq` like the shipped script, instead of reporting a pass for a check that could not run
- Frontmatter severity is stated per file type: missing frontmatter is CRITICAL for an agent, optional for a command, and YAML that does not parse is CRITICAL for either
- All six `model` statements in `claude-code-requirements.md` admit full identifiers, including the detection table and the validation checkbox a reviewer classifies from
- The verdict's security floor covers a new path from contributor-controlled input to a shell, not only a widened permission, tool grant, or hook capability, so a newly introduced command-injection vector cannot report `Pass`
- The Grep-path bare-rule pattern is annotated as producing candidates rather than findings, since a line-oriented match cannot tell `permissions.allow` from `deny` and the router holds no Bash to fall back on
- The generic-credential check anchors its placeholder filter to the value, matching the two token checks. It previously discarded any match whose file path contained `example` or `xxx`
- A widening the changeset justifies is stated as not a finding, which is what lets `acceptEdits` be asked about rather than blocked

### Migration

- `bitwarden-code-review` routes changed `SKILL.md` files to `Skill(claude-config-validator:reviewing-claude-config)` at `skills/performing-multi-agent-code-review/SKILL.md:173` and `agents/bitwarden-code-reviewer/AGENT.md:83`. From 2.0.0 that router declines `SKILL.md`, and that pipeline does not invoke `plugin-dev:skill-reviewer`, so a changeset touching only skills gets a stated omission rather than a review. Updating that consumer needs its own version bump and is tracked as a follow-up

### Added, from review

- `reviewing-command-definitions` pass covering `` !`cmd` `` shell execution and argument interpolation, the security surface no sibling skill covered
- Network-egress, subagent-spawning, and exact-tool-name checks in the agent tool-access pass
- A `permissions.deny` check, a path-resolution check for `CLAUDE.md` references, and a check for natural-language directives that loosen the harness

### Removed

- Seven `examples/example-*-review.md` files
- Six `checklists/*.md` files

## [1.2.2] - 2026-08-17

### Fixed

- `reviewing-claude-config` returns per-issue findings for the caller to route, instead of requiring inline pull request comments its `Read, Grep, Glob` grant cannot post and its callers classify before posting
- Cross-plugin secret-detection enrichment is conditioned on the `Skill` grant, which the skill does not hold on the direct-invocation path
- Skill and plugin docs no longer describe executable scripts or inline comments as things the skill does
- Ten broken relative references across the six checklists and two examples, which pointed one directory level off

### Changed

- `Bash(git fetch:*)` on `/validate-ai-local` narrowed to `Bash(git fetch origin:*)`
- `/validate-ai`'s README notes the shared-host caveat for its fixed `/tmp` report path
- Verdict vocabulary is `Pass` or `Issues found`, replacing `APPROVE`, `REQUEST CHANGES`, and `BLOCK`, which the report contract cannot consume
- A security finding no longer stops the settings or hooks review; both now finish the remaining passes so the caller's report can say which ran
- `security-patterns.md` points at the shipped `security-scan.sh` instead of embedding a copy that had drifted 134 lines from it
- The verdict has a threshold: any CRITICAL or IMPORTANT finding makes it `Issues found`, and a review with only SUGGESTED or OPTIONAL findings is `Pass`

## [1.2.1] - 2026-08-14

### Changed

- `/validate-ai-local` writes its report to `${CLAUDE_PLUGIN_DATA}/ai-validation/<repo>-<timestamp>-validation.md` instead of the working directory, so no repository it runs against needs a `.gitignore` entry for the report
- `Edit` rule scoped to `~/.claude/plugins/data/claude-config-validator*/ai-validation/`, plus `Bash(date:*)` for the report timestamp. The path is written literally rather than as `${CLAUDE_PLUGIN_DATA}` because that substitution is skipped for a local `--plugin-dir` load; it therefore does not follow `CLAUDE_CONFIG_DIR` or `CLAUDE_CODE_PLUGIN_CACHE_DIR`
- `/validate-ai-local` description names the report location, which is the string `/help` shows

### Fixed

- Both commands declared their report file as a `Write` path rule. Claude Code consults `Edit(path)` and `Read(path)` rules only, so a `Write` path rule is accepted, never consulted, and warned about at startup, leaving each command's mandatory final write unapproved. Both are now `Edit` rules, which cover every built-in file-editing tool. Requires Claude Code 2.1.210 or later; on an older CLI the write asks for permission

## [1.2.0] - 2026-08-12

### Added

- `/validate-ai` command: validates the Claude material changed in a pull request and reports to a sticky comment, porting the review from the `bitwarden/gh-actions` `validate-ai` action, including its `.claude-pr/` trust rule
- `/validate-ai-local` command: the same validation against a local checkout, plus the action's structure, marketplace, and version-bump shell checks when a `gh-actions` checkout is reachable; writes `validation-summary.md`
- `reference/validate-ai-scope.md` in `reviewing-claude-config`: scope rules, gating, severity mapping, and the report contract, shared by both commands so they cannot drift from the action
- Untrusted-input boundary: configuration under review is data to report on, never instructions to follow (CWE-1427). Stated unconditionally in `SKILL.md`, so it holds for a direct skill invocation as well as through either command
- Report completion contract from bitwarden/gh-actions#867 and #868: a `<!-- validation-complete -->` marker, one write at the end, and independent subagents dispatched together but never left in flight at turn end
- `checklists/hooks.md` and `examples/example-hooks-review.md`, plus hook detection and routing in `reviewing-claude-config`: hooks were a bucket both commands routed into a skill that had no hook coverage at all
- Explicit `commands` array in `plugin.json`. Per the [plugins reference](https://code.claude.com/docs/en/plugins-reference), naming `commands` replaces the default `commands/` scan, so the per-command `README.md` files sitting beside each command are not registered as commands. Note that `plugin-dev`'s bundled `manifest-reference.md` still describes this field as supplementing the default scan, which is why review tooling reports the opposite

### Fixed

- Command detection in `reviewing-claude-config` missed plugin commands, which nest as `commands/<name>/<name>.md`, so this plugin's own commands would have gone unreviewed
- Hook review now also reaches hooks declared under a `hooks` key in a settings file, which is where a repository usually puts them
- Documentation accuracy in the skill: `SKILL.md` casing throughout, dead paths, and the marketplace name
- Stale citations in the examples: off-by-one line anchors in the hooks example, and line ranges into `claude-code-requirements.md` that had drifted. Reference sections by name instead, since a line range cannot survive an edit to the file it points at
- Duplicate thematic breaks left by appending the output-format section to three checklists, orphaned example numbering in the split composition file, and script paths in the skill README that omitted `scripts/`
- `example-agent-review.md` was 559 lines, over the 500-line guideline this plugin applies to everyone else. Split, with agent invocation and dependency reviews moving to `example-agent-composition-review.md`
- Counts of checklists, references, and examples are gone from both READMEs. They went stale twice in this release alone, since nothing checks a number in prose against the files on disk; the lists carry the same information and cannot drift
- A security finding no longer stops the review: a changeset report has to say which sections ran, which an early exit makes impossible

## [1.1.1] - 2026-03-12

### Changed

- Remove redundant `skills` field from `plugin.json`; skills are auto-discovered from the `skills/` directory

## [1.1.0] - 2026-02-23

### Added

- Cross-plugin skill awareness in `reviewing-claude-config` skill: invokes security engineer `detecting-secrets` skill for enhanced context-aware secret detection when the `bitwarden-security-engineer` plugin is installed

## [1.0.0] - 2025-11-14

### Added

- Initial release of `claude-config-validator` plugin
- `reviewing-claude-config` skill for validating Claude Code configuration files
- Validation support for 6 configuration types: agents, skills, CLAUDE.md, prompts, commands, settings, and plugin configurations
- Security-first multi-pass review strategy (security → structure → functionality → quality → marketplace)
- Priority-classified feedback system (CRITICAL/IMPORTANT/SUGGESTED/OPTIONAL)
- 16 reference files covering security patterns, best practices, and quality standards
- 5 specialized validation checklists for each configuration type
- 6 example review outputs demonstrating validation patterns
- Evidence-based recommendations sourced from official Anthropic and Microsoft Azure AI documentation

---

## Version Format

Plugin version tracks validation system changes:

- **Major version**: Breaking changes to validation checklists, security rules, or plugin structure
- **Minor version**: New validation features, additional configuration type support, new reference documentation
- **Patch version**: Bug fixes, clarifications, documentation improvements, checklist refinements
