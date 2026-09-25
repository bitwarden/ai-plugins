# Changelog

All notable changes to the Bitwarden Eval Tools plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-17

### Added

- Initial release of the `bitwarden-eval-tools` plugin: a reusable trigger-rate
  eval runner for Bitwarden skills. See the [README](README.md) for what it
  does and how to use it.
- Real-work bail: a run ends once the model reaches for a real-work tool without
  having reached the skill under test. Read-only `gh` and `git` lookups are
  scanned past unless something is chained onto them.
- A sub-agent dispatch naming the skill under test counts as a trigger.
- Per-case `timeouts`.
- `scripts/tests/test_trigger_eval.py`.

### Fixed

- Triggers in an exited child's final output chunk were discarded, scoring short
  sessions as non-triggers regardless of what they did.
- A `Read` counts only on the component's own `SKILL.md` or `AGENT.md`, not any
  path containing the token.

### Notes

- Isolated-mode runs are serialized per skill under test, so concurrent
  `--num-workers` never leave more than one clone of that skill visible at
  once. See `scripts/trigger_eval.py`.

---

## Version Format

Plugin version tracks eval-runner and skill changes:

- **Major version**: Breaking changes to the CLI, report schema, or skill structure.
- **Minor version**: New flags, report fields, or reference documentation.
- **Patch version**: Bug fixes, clarifications, documentation improvements.
