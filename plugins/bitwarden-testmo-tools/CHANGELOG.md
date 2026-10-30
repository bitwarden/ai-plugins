# Changelog

All notable changes to the Bitwarden Testmo Tools plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-28

### Added

- `creating-test-runs` skill: creates test runs in Bitwarden's Testmo instance from reviewable JSON
  filter specs, with a dry-run the user reviews before anything is written.
- `testmo_create_runs.py`: selects cases by tag (server-side), folder path or id with subtree expansion,
  test type, team, automation type, and case state, then creates one run per spec only with `--create`.
  - Accepts several `--spec` arguments in one pass, fetching the folder tree and case list once for the
    whole batch, and refuses `--create` unless every run is ready.
  - Links runs to an existing milestone by `--milestone-id` or `--milestone-name`.
  - Refuses to create a run whose name and configuration already exist in the milestone or in the same
    batch, unless `--allow-existing` is passed.
  - Refuses runs matching zero cases, specs with unresolved folders, and specs whose `config_id` is a
    `null` placeholder, and lists the multi-configuration runs that need a manual Testmo UI pass.
  - Keeps `TESTMO_API_KEY` out of argv and output, refuses redirects, and falls back to `curl` on
    networks running TLS interception.
- References for the Testmo API and project 1 field ids, multi-configuration runs, and the TLS fallback,
  plus a spec template.
