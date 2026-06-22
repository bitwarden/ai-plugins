# Changelog

All notable changes to the Bitwarden Test Engineer Plugin will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-15

### Added

- Initial release of the `bitwarden-test-engineer` plugin.
- `test-strategist` agent: classifies a change's inputs (Jira ticket, GitHub PR, tech breakdown, test-case CSV, plain-language description), fans out subagents to gather evidence, and presents a test recommendation.
- `assessing-test-coverage` skill: inventories what a change is already tested by, buckets observed tests by layer, cites them as stable GitHub permalinks, and writes a self-contained HTML coverage report.
- `analyzing-test-stack` skill: maps a change's testable behaviors to the cheapest sufficient test layer per platform, surfaces coverage gaps and shape-wrong tests, and emits a self-contained HTML report.
- Shared plugin-level `references/` and a `build-report.sh` script that splices the single shared stylesheet into each report so the two reports can't drift.
