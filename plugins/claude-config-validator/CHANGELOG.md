# Changelog

All notable changes to the Claude Config Validator Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.2] - 2026-08-21

### Fixed

- `security-scan.sh` reported a pass for the committed `settings.local.json` check whenever `git`'s output was long enough that `grep -q` exited first: under `pipefail` the pipeline took `git`'s SIGPIPE status. Load-dependent, so a small `.claude/` never showed it
- `security-scan.sh` ran `git ls-files` without `-C`, so the check read whatever repository the shell was in and reported a pass when the target sat outside one. It records the check as skipped now
- `security-scan.sh` counted the two permission checks as passed when there was no `settings.json` to read; both record as skipped, so the run reports as incomplete

### Added

- `scripts/security-scan.test.sh`, covering each of the above plus a clean configuration. Eight of its fifteen assertions fail without these fixes. Credential fixtures are assembled at run time, so the file holds no string a secret scanner should flag
## [2.0.1] - 2026-08-21

### Fixed

- `reviewing-claude-config` and `reviewing-command-definitions` failed to load: both quoted the literal bash-execution syntax, which Claude Code expands in any file it loads, in inline code spans and fenced blocks alike
- `reviewing-command-definitions` names the construct rather than reproducing it, and says why, so the syntax is not reintroduced

## [2.0.0] - 2026-08-19

### Added

- Scope fence: findings are limited to what a changeset introduced or worsened
- Filter step before reporting, dropping findings that are pre-existing, unspecific, unverified, already covered, or have no remediation
- Four targeted review skills: `reviewing-agent-definitions`, `reviewing-command-definitions`, `reviewing-runtime-configuration`, `reviewing-project-guidance`
- Settings pass for fields that execute or bypass: `defaultMode`, `additionalDirectories`, `apiKeyHelper`, `statusLine.command`, `enableAllProjectMcpServers`, `env`
- `security-scan.sh` Check 4 lists every string the configuration runs or auto-approves, with its location, instead of matching a pattern list against them
- Shell-execution pass for slash commands, covering `` !`cmd` `` blocks and argument interpolation
- Hook and settings severity tables in `priority-framework.md`

### Changed

- **Breaking**: `reviewing-claude-config` is a router; the `checklists/` and `examples/` directories are gone
- **Breaking**: `reviewing-claude-config` no longer reviews `SKILL.md` — `plugin-dev:skill-reviewer` owns it
- A run fails only on a CRITICAL finding or one that weakens security; other severities report without blocking
- IMPORTANT narrowed to functional defects and security regressions; readability moved to SUGGESTED
- Both commands state that the report is the deliverable and that re-validation pins the original baseline

### Fixed

- Permission examples use `Tool` or `Tool(specifier)` rules under `permissions.allow` / `deny`, replacing a top-level `autoApprovedTools` array Claude Code does not read
- `//` documented as the absolute path prefix, against a single leading `/` as relative to the settings file
- `security-scan.sh` and the documented detectors match the real schema and read `permissions.allow` rather than the whole file, so a hardening `deny` is not reported as a defect; placeholder exclusions anchor to the value rather than the file path
- The permission checks and the Check 4 inventory are counted and reported as skipped when they cannot run; a run with no findings but a skipped check exits 2 rather than claiming a pass
- A `settings.json` that does not parse is CRITICAL rather than silently emptying the checks that read it

### Removed

- Six `checklists/*.md` files, seven `examples/example-*-review.md` files, and the skill-level `README.md`

### Migration

- `bitwarden-code-review` routes changed `SKILL.md` files to `Skill(claude-config-validator:reviewing-claude-config)`, which declines them from 2.0.0. That pipeline does not invoke `plugin-dev:skill-reviewer`, so skill-only changesets get a stated omission rather than a review. Updating it needs its own version bump and is tracked as a follow-up

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
