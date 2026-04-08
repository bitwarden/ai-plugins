# Changelog

All notable changes to the bitwarden-devops-engineer plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-19

### Added

- Initial release of bitwarden-bre plugin
- `/bre-workflow-fix` command for fixing Bitwarden workflow linter findings
  - Runs `bwwl lint` and applies mechanical fixes automatically
  - Handles judgment calls interactively (unapproved actions, complex actionlint findings)
  - Supports single file, directory, or multi-repo (`--repos`) scope
  - Creates draft PRs per repo
- `/bre-action-audit` command for org-wide action usage auditing and remediation
  - `incident` mode for targeted action search during security events
  - `audit` mode for sweeping all unpinned action references org-wide
  - Hash resolution with verification links before applying any changes
  - Creates draft PRs per repo after user confirmation
- `bitwarden-workflow-linter-rules` skill with reference knowledge for all 10 linter rules
