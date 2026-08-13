# Changelog

All notable changes to the Claude Config Validator Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-08-12

### Added

- `/validate-ai` command: validates the Claude Code material changed in a pull request and reports to a sticky pull request comment. Ports the review prompt from the `bitwarden/gh-actions` `validate-ai` action, including the `.claude-pr/` trust rule for pull-request-authored configuration, so the action and a human run the same review
- `/validate-ai-local` command: runs the same validation against a local checkout (branch commits plus uncommitted and untracked work) and writes the report to `validation-summary.md`. Also runs the `validate-plugin-structure.sh`, `validate-marketplace.sh`, and `validate-version-bump.sh` checks from a `bitwarden/gh-actions` checkout when one is available
- Explicit `commands` array in `plugin.json`, matching the convention in
  `bitwarden-code-review` and `bitwarden-init`: the per-command `README.md` files sit
  inside `commands/`, so without it they would be auto-discovered as commands
- Report completion contract, matching the `validate-ai` action as of
  bitwarden/gh-actions#867: the report ends
  with a `<!-- validation-complete -->` marker, is written exactly once at the end with no
  interim versions, and is written only after every subagent has returned. The action
  discards a report without the marker and fails the check, and a headless run kills any
  subagent still in flight when the turn ends
- `reference/validate-ai-scope.md` in the `reviewing-claude-config` skill: changed-file classification rules, validation gating, report contract, and the mapping from the skill's CRITICAL/IMPORTANT/SUGGESTED/OPTIONAL priorities onto the report's critical/major/minor severities. Shared by both commands so they cannot drift from each other or from the action

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
