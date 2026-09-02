# Changelog

All notable changes to the Bitwarden Testmo Tools plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026-09-02

### Removed

- **Breaking:** `setup_release_runs.py --project`. The flag defaulted to `1` and silently outranked every
  spec's `project_id`, so the two entrypoints disagreed about the same file — `testmo_create_run.py` has
  always treated `spec["project_id"]` as authoritative. A spec written for one project and run through the
  orchestrator without a matching flag would be created into another. The flag also had no working use
  case: project-1 folder paths do not resolve in the sandbox, so `--project 2` failed every spec at folder
  resolution before creating anything.

### Added

- `resolve_project()`: the orchestrator now reads `project_id` from every spec in the profile and refuses
  to run when they disagree, listing which specs target which project. A spec with no `project_id` is also
  an error.
- `load_specs()`: all specs are read and parsed up front, so a profile naming a spec with no file — or a
  spec with malformed JSON — fails before any API call rather than mid-pass.

### Changed

- The run header prints `Project : N (from the specs)` in place of the flag's value.
- A missing spec file is now a hard error at load time instead of a `MISSING SPEC` row in the summary
  table; `FOLDER ERROR` rows still surface there.
- Dropped an unused `os` import from `setup_release_runs.py`.

## [0.4.5] - 2026-09-02

### Fixed

- A non-JSON response is no longer an unhandled traceback. `json.loads` on the response body was
  unguarded, so a proxy or login-wall HTML page arriving with a 200 raised a bare `JSONDecodeError`. It now
  raises `TestmoAPIError` naming the request and quoting the first 200 characters of the body.
- `setup_release_runs.py` no longer claims success after a partial failure. A rejected POST aborted the
  whole pass, and the final line still read "Done. All runs linked to milestone …" for runs that were never
  created. The create loop now records each run's outcome, continues, and closes with a
  `N created / N skipped / N failed` tally; a failure lists every run that did not make it and exits
  non-zero, noting that the milestone is only partially populated.
- `testmo_create_run.py` no longer reports a run it did not create. A response carrying no run id printed
  `CREATED run id=None https://bitwarden.testmo.net/run/None`; it now exits with the response body.
- Failure rows identify the spec file alongside the run name (`Extension [extension-linux-firefox-regression]`).
  Multi-config runs share a `run_name` by design, so a tally of three failed `Extension` runs was
  unactionable — the spec name is what `--exclude` takes.

### Changed

- API failures raise a new `TestmoAPIError` instead of calling `sys.exit` inside `call()`. The single-run
  script still aborts on it, but the orchestrator can now catch a per-run failure and keep going. Error
  messages are built from the request line and response body only, never the API key; HTTP 401/403 adds an
  "is TESTMO_API_KEY current?" hint.

## [0.4.4] - 2026-09-01

### Fixed

- Every runnable command in `SKILL.md` addressed the scripts and specs with a cwd-relative path
  (`python3 scripts/testmo_create_run.py --spec specs/<run>.json`). An installed plugin lives in the plugin
  cache while the working directory is the user's own repository, so both halves of that command resolved
  to files that do not exist. All five invocations now go through `${CLAUDE_PLUGIN_ROOT}`, the convention
  already used by `bitwarden-devops-engineer`, `bitwarden-security-engineer`, `bitwarden-delivery-tools`,
  `bitwarden-init`, and `claude-config-validator`.

### Added

- `SKILL.md`: a "Locating the scripts and specs" section explaining why paths go through
  `${CLAUDE_PLUGIN_ROOT}`, and noting that a user's own spec is passed by its real path. Each command block
  sets a `SKILL` shorthand of its own, since shell state does not carry between commands.
- `README.md`: a note that its examples are relative to the plugin directory and need a
  `${CLAUDE_PLUGIN_ROOT}/` prefix when the plugin is installed.

## [0.4.3] - 2026-09-01

### Fixed

- `SKILL.md`: the filter-spec schema no longer conflates the two meanings of `tags`. The example showed
  `tags` only at the top level (where it labels the created run), while the key list beneath it — headed
  "Every key under `filters`" — documented `tags` as a case filter. A reader following the prose to write a
  tag-only spec would set the top-level key and leave `filters` empty, which selects **every** case in the
  project; the zero-case guard catches only the opposite mistake. The section is now split into "Top-level
  keys (the run payload)" and "Keys under `filters` (case selection)", with a dedicated note on `tags`
  appearing in both and the shipped `old-client-new-server-regression.json` as the worked example.

### Added

- `SKILL.md`: a warning that an empty or missing `filters` block matches every case, and documentation for
  the previously unlisted top-level keys `project_id`, `run_state_id`, `config_id`, and `note`.
- `specs/regression-run.template.json`: a `_comment` explaining the two halves of a spec, the two meanings
  of `tags`, the empty-`filters` hazard, and when to add a `config_id` — the template is what new specs are
  copied from, so the distinction needs to be discoverable there.

## [0.4.2] - 2026-09-01

### Removed

- The "sandbox first" guardrail, which could not be followed as written. `SKILL.md` step 2 told the reader
  to dry-run against project `2`, but `testmo_create_run.py` takes its project solely from the spec's
  `project_id`, and every shipped spec — including the template — pins `1`. The documented command always
  hit live project 1. It was dropped rather than made executable: the sandbox does not mirror project 1's
  folders, tags, or configurations, so a dry-run there cannot validate the case set a spec selects. The
  same instruction is removed from `SKILL.md`'s guardrail list and `README.md`'s safety list.

### Changed

- `SKILL.md`: the workflow is now four steps, with the (unchanged) live dry-run as the review step for new
  specs as well as each period's run, and guidance to compare the case count against the previous cycle.
- `SKILL.md`: the project list now records what project `2` is and is not good for, so the guardrail is not
  reintroduced; the `setup_release_runs.py --project` note describes what the flag does instead of
  suggesting sandbox testing.
- `README.md`: the dry-run safety bullet notes that a dry-run only reads, and documents the fail-fast on
  unresolved folder paths.

## [0.4.1] - 2026-09-01

### Security

- `scripts/testmo_create_run.py` no longer shells out to `curl`, which received the Testmo API key as a
  command-line argument (`-H "Authorization: Bearer $KEY"`). Process arguments are readable by any local
  user for the life of the request — via `ps auxww` on macOS, and `ps` or `/proc/<pid>/cmdline` on Linux,
  which does not enable `hidepid` by default. `setup_release_runs.py` issues one such request per page per
  spec, so a release setup left the key exposed across dozens of requests. Requests now go through
  `urllib.request` with the header set in-process, so the key never leaves the Python process.

### Changed

- Dropped the `curl` prerequisite: the scripts now use only the Python standard library, which also makes
  them portable to Windows shells without `curl` on `PATH`. Documented in `README.md` and `SKILL.md`.
- API errors now report the HTTP status, reason, and response body (previously only curl's stderr).

## [0.4.0] - 2026-08-28

### Added

- `specs/cli-regression.json`: scopes to the whole `CLI` top-level folder and all descendants with the
  established regression defaults (Test Type = Smoke/Regression, case state Active, manual only). Unlike
  the Web specs it needs no enumerated subfolders, as the folder is a single product.
- Desktop as **three** same-named `Desktop` runs distinguished only by Testmo Configuration:
  `specs/desktop-macos-regression.json` (broad — whole `Desktop` folder + defaults),
  `specs/desktop-windows-regression.json` and `specs/desktop-linux-regression.json` (narrow — driven by
  the `desktop-essential` tag).
- Extension as **four** same-named `Extension` runs on the same broad/narrow split:
  `specs/extension-macos-chrome-regression.json` (broad, Configuration `MacOS, Chrome`), plus
  `specs/extension-windows-edge-regression.json`, `specs/extension-macos-safari-regression.json`, and
  `specs/extension-linux-firefox-regression.json` (narrow — driven by the `extension-essential` tag).
- Every Desktop and Extension variant, broad and narrow alike, is a **two-step run**: removing the cases
  belonging to non-target configurations is a manual UI pass, since Testmo's `/cases` API cannot filter
  by configuration. Each spec documents its own step 2.
- Narrow variants drop the test-type filter (a tagged case counts regardless of type) but keep the case
  state and automation-type filters, so retired and already-automated cases are excluded. Measured effect
  on 2026-08-28: `desktop-essential` 79 raw → 69, `extension-essential` 51 raw → 48.
- All seven Desktop/Extension `config_id`s resolved and committed (Desktop: macOS 21, Windows 22, Linux
  20; Extension: `MacOS, Chrome` 7, `Windows, Edge` 15, `MacOS, Safari` 10, `Linux, Firefox` 5), and both
  tag names verified unique (`desktop-essential` 15999, `extension-essential` 17190). Verified against
  project 1 on 2026-08-28.
- Seeded the `full` release profile with all eight. They run only for full releases, not partial ones.
- SKILL.md section documenting the multi-configuration run pattern for Mobile, Desktop, and Extension —
  the broad/narrow split, why step 2 cannot be automated, and the resolved config and tag ids.
- `--exclude <spec-name>` on `setup_release_runs.py` to skip one of a profile's runs for a single release
  (repeatable or comma-separated). A name not in the profile is a hard error, so a typo cannot silently
  create the run it was meant to skip. Use it for one-off omissions only — a run skipped every cycle
  belongs in `release-profiles.json`.

### Changed

- Restructured `release-profiles.json` so `full` is no longer a superset of `partial`. Both now extend a
  new shared `common` base (Web PM / Admin Console / Admin Portal, Old Client / New Server, both Mobile).
  **Directory Connector (BWDC) belongs to `partial` only** and is no longer inherited by `full`. Done
  declaratively — `load_profile()` already resolved arbitrary parents, so no code change was needed.
  Reach for `--exclude` only for one-off omissions; a run skipped every cycle belongs in the profiles.
- `testmo_create_run.py` now treats `"config_id": null` as an explicit "not yet looked up" placeholder:
  the key is omitted from the run payload, dry-runs still print case counts (so a spec can be validated
  before its Configuration is known), and `--create` is refused with a message pointing at
  `GET /projects/{id}/configs`. Without this, creating a placeholder spec would produce several
  indistinguishable same-named runs. A `null` `milestone_id`, `tags`, or `note` is likewise no longer
  sent as a literal `null`.

## [0.3.1] - 2026-08-26

### Fixed

- `exclude_automation_type_ids` and `automation_type_ids` were compared against the raw
  `custom_automation_type` object returned by the API (`{"id": 10, "name": "Automated"}`) instead of its
  `id`, so neither filter ever matched. `exclude_automation_type_ids` was a silent no-op — every run
  created from a spec using it (all committed regression specs) included already-automated cases.
  `automation_type_ids` had the inverse failure and would have matched zero cases. Both now compare on
  the automation type id, with `null` still meaning "no type set". `setup_release_runs.py` reuses
  `matches()` and is fixed by the same change.

  Impact: re-run the dry-run for any spec relying on these filters — case counts will drop. For example
  the VFO1 core-UX spec went from 321 matched cases to 95 once already-automated cases were correctly
  excluded.

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
