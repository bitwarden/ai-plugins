# Changelog

All notable changes to the bitwarden-doc-parity plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2026-10-12

### Changed

- README Layer 4 no longer says `bitwarden-code-review` integration is planned, since `bitwarden-code-review` 2.4.0 now implements it.

## [1.0.0] - 2026-08-04

### Added

- Initial release of the `bitwarden-doc-parity` plugin, enforcing the documentation standard's base obligations to monitor for drift between code and documentation. Operates within-repo only when fired as a stop-hook and includes out-of-repo validation against contributing-docs when being executed in a PR review.
- Behavior evals for `verifying-doc-parity` against the bitwarden/server Seeder subsystem as the first ground-truth corpus.
