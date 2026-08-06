# Changelog

All notable changes to the bitwarden-ai-telemetry plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-07-31

### Added

- `UserPromptExpansion` hook, so skills invoked by slash command (`/plugin:skill`) are recorded. These were previously invisible: Claude Code expands a slash invocation into the prompt rather than dispatching the Skill tool, so `PostToolUse` never fires and `tool_input.skill` never exists. `UserPromptExpansion.command_name` is the only signal that carries the name.
- `event.timestamp` on every emitted record — ISO-8601 UTC with millisecond precision, matching native Claude Code's shape. Consumers previously had no client clock on these events and fell back to collector ingest time. A caller supplying its own non-empty value keeps it.

### Fixed

- Per-skill usage counts were understated for anyone who invokes skills by slash. Measured before this change: one user had 37 native skill activations, only 13 of which were Skill tool calls, so roughly two thirds of their skill usage produced no telemetry at all.

### Notes

- A slash expansion is recorded with `bw.tool = "Skill"` even though no tool ran, so it matches the same `@bw.tool:Skill` queries as the tool path. `bw.hook` distinguishes the origin (`UserPromptExpansion` vs `PostToolUse`).
- `command_name` may name a plugin _command_ rather than a skill. The two are deliberately not distinguished.
- Expansion types other than `slash_command` are suppressed rather than emitted, since they carry no skill identity and would otherwise write content-free `bw.identity` rows.

## [1.0.0] - 2026-07-01

### Added

- Initial release of the `bitwarden-ai-telemetry` plugin. See the [README](README.md) for what it emits and how to configure it.

### Notes

- `bw.commit` only fires on a genuinely successful `git commit` — not a dry run, a failed commit, or a read-only lookalike such as `git log --grep commit` or `git show`. Decision logic lives in the unit-tested `_is_successful_commit` helper (`hooks/test_emit_git.py`).
