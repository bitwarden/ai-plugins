# Changelog

All notable changes to the `bitwarden-abacus` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-10-23

### Added

- `plan.source` mapped to `bitwarden-atlassian-tools:researching-jira-issues`, so "plan PM-1234" makes the Abacus planner read the Jira issue, its linked issues and Confluence pages, and draft beads from them. Requires Abacus 0.15 or later.

### Changed

- Minimum supported Abacus version is now 0.15, up from 0.13. On Abacus 0.13 or 0.14 the profile no longer applies, including `land.commit` and `land.pr`, so update Abacus along with this plugin.

## [0.2.0] - 2026-10-22

### Added

- `land.commit` mapped to the new `commit-message` skill, which follows `bitwarden-delivery-tools:committing-changes`, so each commit Abacus makes uses Bitwarden's commit format. When a bead has no Jira ticket, the commit drops the bracket, as `applying-pr-conventions` does for pull request titles, so the two agree. Every commit uses the full format; the followup-commit exemption in `committing-changes` doesn't apply to unattended landing.

### Changed

- Minimum supported Abacus version is now 0.13, up from 0.11. On Abacus 0.11 or 0.12 the profile no longer applies, including `land.pr`, so update Abacus along with this plugin.

## [0.1.0] - 2026-10-20

### Added

- Initial release of the `bitwarden-abacus` plugin: the Abacus profile for Bitwarden. Requires Abacus 0.11 or later.
- `land.pr` mapped to `bitwarden-delivery-tools:applying-pr-conventions`, so each draft PR Abacus opens carries Bitwarden's conventional title, PR template body and `t:` type label. See the plugin README for details.
