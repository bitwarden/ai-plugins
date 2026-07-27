# Changelog

All notable changes to the Bitwarden Testmo Tools plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-07-27

### Changed

- Simplified regression run names to the bare domain/area. Run names no longer encode the platform, the
  word "Regression", or the release period, since the release is conveyed by the linked milestone and the
  platform variant by the run's Testmo Configuration (`config_id`). Examples: `Web Regression — Password
Manager (<period>)` → `Password Manager`; `Directory Connector (BWDC) Regression (<period>)` →
  `Directory Connector (BWDC)`. Both mobile specs are now named just `Mobile`, distinguished by
  configuration (Android=1, iOS=3). Updated all captured specs, the spec template, and the SKILL.md naming
  guidance accordingly. The `--period`/`<period>` substitution mechanism is unchanged for any spec that
  still uses the placeholder.

## [0.1.0] - 2026-07-22

### Added

- Initial plugin: Testmo REST API access for reading/analyzing the case repository and run history, and
  creating regression runs from reviewable filter specs
- `creating-regression-runs` skill documenting the dry-run-first workflow, filter-spec schema, and write
  guardrails (sandbox-first, idempotency, per-period milestone linkage)
- `testmo_create_run.py` script: filters cases by Testmo tag (server-side), folder path/subtree,
  test-type/team intersection, automation-type include or exclude, and case state; prints a dry-run
  summary and run payload, and creates the run only with `--create`. Folder paths are resolved against
  the live tree and fail fast if unmatched
- Project 1 field-id reference (test types, automation types, teams, states, top-level folders) in the
  skill
- First captured spec `specs/web-password-manager-regression.json` (Web › Password Manager regression,
  202 cases as of 2026-07-22) plus filter-spec template
- Additional captured specs: Web Admin Console (180), Web Admin Portal/SM/Providers (70), Old Client/New
  Server (tag `oldnew`, 31), Mobile iOS (step-1 = 203; the Configuration=Android subtraction to ~148 is a
  documented manual UI step, as Testmo's API cannot filter cases by configuration), Mobile Android
  (step-1 = 191), Directory Connector/BWDC (24)
- `--milestone-id` and `--period` CLI options to link runs to an existing milestone and fill the
  `<period>` placeholder in a run name. Milestones themselves must be created in the Testmo UI — the API
  has no milestone-create route (verified); linking a run via `milestone_id` is supported and verified.
- `setup_release_runs.py` orchestrator plus `release-profiles.json`: create every run for a release
  (`partial`/`full`, where `full` extends `partial`) in one pass, linked to a milestone resolved by name.
  Dry-run prints a per-run case-count summary; `--create` posts them all. Fetches cases/folders once for
  the whole set.
