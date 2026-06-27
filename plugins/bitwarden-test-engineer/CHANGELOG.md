# Changelog

All notable changes to the Bitwarden Test Engineer Plugin will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-15

### Added

- Initial release of the `bitwarden-test-engineer` plugin.
- `assessing-test-coverage` skill: inventories what a change is already tested by — scoped to the change surface, PRs-first then a targeted lookup — buckets each observed test by layer (unit / integration / E2E), cites 1–3 representative tests per behavior as stable GitHub permalinks, flags untested behaviors as gaps, and writes a self-contained markdown coverage report to `test-engineer-report-<slug>-<date>/coverage.md`.
