# Changelog

All notable changes to the `bitwarden-abacus` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-10-22

### Added

- `land.commit` mapped to the new `commit-message` skill, which follows `bitwarden-delivery-tools:committing-changes`, so each commit Abacus makes uses Bitwarden's commit format. When a bead has no Jira ticket, the prefix is `[NO-TICKET]`; pull request titles keep following `applying-pr-conventions`, which drops the bracket. Requires Abacus 0.13 or later.

## [0.1.0] - 2026-10-20

### Added

- Initial release of the `bitwarden-abacus` plugin: the Abacus profile for Bitwarden. Requires Abacus 0.11 or later.
- `land.pr` mapped to `bitwarden-delivery-tools:applying-pr-conventions`, so each draft PR Abacus opens carries Bitwarden's conventional title, PR template body and `t:` type label. See the plugin README for details.
