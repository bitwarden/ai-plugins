# Changelog

All notable changes to the bw-telemetry plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-01

### Added

- Initial release of the `bw-telemetry` plugin. See the [README](README.md) for what it emits and how to configure it.

### Notes

- `bw.commit` only fires on a genuinely successful `git commit` — not a dry run, a failed commit, or a read-only lookalike such as `git log --grep commit` or `git show`. Decision logic lives in the unit-tested `_is_successful_commit` helper (`hooks/test_emit_git.py`).
