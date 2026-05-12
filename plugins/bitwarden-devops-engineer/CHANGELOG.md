# Changelog

All notable changes to the bitwarden-devops-engineer plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.3] - 2026-05-08

### Changed

- Updated `action-audit` skill to apply Bitwarden's two-tier pin compliance model: internal `bitwarden/` actions must be pinned to `@main`; third-party actions must be pinned to a full 40-char SHA with an inline version comment. Previously the skill treated all non-hash refs as non-compliant, which incorrectly flagged valid internal action references.

### Fixed

- Updated `bitwarden-workflow-linter-rules` skill to correctly document the `step_pinned` rule with its two-tier model: internal `bitwarden/` actions must pin to `@main` (with a `bitwarden/sm-action` exception that allows any ref), external actions must pin to a full 40-char SHA with an inline version comment. Previously the rule described `@main` as non-compliant, contradicting `action-audit`.
- Updated `action-audit` skill to reference `bitwarden-workflow-linter-rules` as the single source of truth via `${CLAUDE_PLUGIN_ROOT}` path, eliminating both cross-skill drift and a runtime path-resolution failure in marketplace deployments.
- Updated `action-audit` skill to restore the incident mode replacement-action branch in Step 4, which was incorrectly dropped — a compromised-action response that names a replacement now routes to SHA resolution for the replacement rather than the compromised action.
- Updated `action-audit` skill to treat SHA-pinned internal actions as informational rather than non-compliant, requiring user confirmation before recommending a change to `@main`.
- Updated `action-remediate` skill to add a **pin to main** remediation path for internal `bitwarden/` actions, closing a gap where following the documented audit→remediate flow would incorrectly SHA-pin internal actions.

## [0.1.1] - 2026-04-15

### Changed

- Apply prettier formatting to markdown files

## [0.1.0] - 2026-04-14

### Added

- Initial release of the bitwarden-devops-engineer plugin
- Workflow linting audit and fix skills
- Org-wide GitHub Actions action usage auditing and remediation skills
- Linter rules reference covering all 10 bwwl rules
