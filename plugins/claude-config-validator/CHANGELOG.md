# Changelog

All notable changes to the Claude Config Validator Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
