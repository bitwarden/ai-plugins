# Changelog

All notable changes to the bitwarden-ai-telemetry plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-09-17

### Added

- A `systemMessage` warning when a record does not reach the collector. Errors were swallowed to keep a session safe and then discarded, so usage going entirely unrecorded was invisible. The usual cause is ZScaler Private Access not having re-authenticated; a bad managed-settings push is the other.
- Delivery is judged on the collector's `202`, not on the request failing to raise, because ZScaler can answer a sign-in page with `200` and that would otherwise read as success.

### Notes

- One warning per fault class per hour, and none at all if that state cannot be written: a warning on every edit is worse than silence.
- The hooks still exit 0, so nothing is blocked or interrupted.
- Delivery past the collector is out of reach. A record it accepts returns 202 regardless of what becomes of it afterwards.

## [1.1.1] - 2026-09-17

### Fixed

- `bw.edit` resolves repo, branch, base SHA and path from the edited file's own location. Resolving them against the session's starting directory mislabelled every edit made in a worktree or a sibling checkout, and left `bw.file` escaping the repo root, so the event described a repository the edit never touched.
- `bw.commit` reports the commit the command produced, resolved from the directory it ran in and confirmed against the SHA git printed. Reading HEAD from the starting directory reported a real but unrelated commit as this session's work. Where the two disagree, nothing is emitted.
- `bw.pr` takes its repo from the URL `gh pr create` prints. Opening a pull request from a session started elsewhere paired the new number with the wrong repository slug.
- Events with no repository to name are no longer sent. A commit SHA, pull request number or file path is meaningful only within one repository, so a plan file, a memory file, something under `/tmp`, or a checkout with no origin remote produces a record that identifies nothing.

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
