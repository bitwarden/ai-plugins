# Changelog

All notable changes to the bitwarden-devops-engineer plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.3] - 2026-05-08

### Fixed

- Updated `bitwarden-workflow-linter-rules` skill to correctly document the `step_pinned` rule with its two-tier model: internal `bitwarden/` actions must pin to `@main` (with a `sm-action` path exception that allows any ref), external actions must pin to a full 40-char SHA with an inline version comment. Previously the rule described `@main` as non-compliant, contradicting `action-audit`.
- Updated `action-audit` skill to remove its embedded copy of the pin compliance rules and instead read `bitwarden-workflow-linter-rules` as the single source of truth at runtime, eliminating drift between the two skills.
- Updated `action-remediate` skill to add a **pin to main** remediation path for internal `bitwarden/` actions, closing a gap where following the documented audit→remediate flow would incorrectly SHA-pin internal actions.

## [0.1.2] - 2026-04-16

### Changed

- Updated `action-audit` skill to apply Bitwarden's two-rule pin compliance model: internal `bitwarden/` actions must be pinned to `@main`; third-party actions must be pinned to a full 40-char SHA with an inline version comment. Previously the skill treated all non-hash refs as non-compliant, which incorrectly flagged valid internal action references.

## [0.1.1] - 2026-04-15

### Changed

- Apply prettier formatting to markdown files

## [0.1.0] - 2026-04-14

### Added

- Initial release of the bitwarden-devops-engineer plugin
- Workflow linting audit and fix skills
- Org-wide GitHub Actions action usage auditing and remediation skills
- Linter rules reference covering all 10 bwwl rules
