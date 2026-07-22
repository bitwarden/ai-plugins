# Changelog

All notable changes to the Bitwarden Testmo Tools plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-22

### Added

- Initial plugin: Testmo REST API access for reading/analyzing the case repository and run history, and
  creating regression runs from reviewable filter specs
- `creating-regression-runs` skill documenting the dry-run-first workflow, filter-spec schema, and write
  guardrails (sandbox-first, idempotency, per-period milestone linkage)
- `testmo_create_run.py` script: filters cases by folder path/subtree, test-type/team intersection,
  automation-type include or exclude, and case state; prints a dry-run summary and run payload, and
  creates the run only with `--create`. Folder paths are resolved against the live tree and fail fast if
  unmatched
- Project 1 field-id reference (test types, automation types, teams, states, top-level folders) in the
  skill
- First captured spec `specs/web-password-manager-regression.json` (Web › Password Manager regression,
  202 cases as of 2026-07-22) plus filter-spec template
