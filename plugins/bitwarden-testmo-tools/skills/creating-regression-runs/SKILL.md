---
name: creating-regression-runs
description: Create Bitwarden regression test runs in Testmo from a reviewable JSON filter spec. Use when asked to set up a bimonthly/periodic regression run, select cases for a run, or create a Testmo run from folder/test-type/team/automation filters. Dry-run first; writes mutate the live instance.
---

# Creating Regression Runs in Testmo

Turn the manual "filter cases → create a run" workflow into a repeatable, reviewable one. The bundled
script (`scripts/testmo_create_run.py`) reads the case repository, selects cases matching a committed
filter spec, and — only when explicitly told to — creates the run via the Testmo API.

**Writes mutate the live Testmo instance. Always dry-run and review before `--create`.**

## Prerequisites

- `TESTMO_API_KEY` exported in the environment. Reference it only by variable — never print, echo, log, or
  commit the value.
- `python3` and `curl` available on `PATH`.

## API reference

- **Base:** `https://bitwarden.testmo.net/api/v1`, auth header `Authorization: Bearer $TESTMO_API_KEY`.
- **Projects:** `1` = **Bitwarden** (live: ~13.7k cases), `2` = **Pretend** (sandbox — safe for write
  tests), `11` = Automation - Test, `14` = Archive.
- **Pagination quirk:** `per_page` only accepts specific values (100 works; 5/10 return HTTP 422). Omit
  `per_page` and page with `page=N`; responses carry `next_page`/`last_page`.
- **Read endpoints (GET):** `/projects/{id}/cases`, `/projects/{id}/folders`, `/projects/{id}/milestones`,
  `/projects/{id}/runs`, `/projects/{id}/automation/runs`, and single-run detail at `/runs/{id}`
  (top-level — `/projects/{id}/runs/{id}` 404s).
- **Create run (POST `/projects/{id}/runs`):** body `{name, state_id, include_all:false, cases:[ids],
milestone_id?, config_id?, tags?, note?}`. Run `state_id`s (from `/projects/{id}/states`): 6=New,
  7=In progress, 8=Under review, 9=Rejected, 10=Done. Active runs use `7`.

## Workflow

1. **Define or load the filter spec** (see schema below). Start from
   `specs/regression-run.template.json`. Commit one spec file per recurring run so it is reviewable and
   reproducible.
2. **Dry-run against the sandbox (project `2`) first** when validating a new spec or a script change:
   ```bash
   python3 scripts/testmo_create_run.py --spec specs/<run>.json
   ```
   Review the matched case count and the run payload it prints.
3. **Dry-run against live (project `1`)** and confirm the case count and sample look right.
4. **Idempotency check:** confirm a run for this period/milestone does not already exist
   (`GET /projects/1/runs`) before creating another.
5. **Create the run** only after the dry-run is reviewed:
   ```bash
   python3 scripts/testmo_create_run.py --spec specs/<run>.json --create
   ```

## Filter-spec schema

```json
{
  "project_id": 1,
  "run_name": "Password Manager",
  "run_state_id": 7,
  "milestone_id": 123,
  "tags": ["regression"],
  "filters": {
    "folder_paths": ["Web > Password Manager", "Web > Shared > TDE > TDE - PM"],
    "include_subfolders": true,
    "test_type_ids": [19, 20],
    "case_state_ids": [4],
    "exclude_automation_type_ids": [10, 23, 24]
  }
}
```

Every key under `filters` is optional — omit a key to skip that dimension. A case must match **all**
provided keys (keys are ANDed; multi-value lists within a key are ORed). Keys:

- `tags` — Testmo tag names or ids, applied **server-side** by the `/cases` API (`?tags=...`), then combined
  with any other filters. A tag-only spec (e.g. `["oldnew"]`) needs nothing else. Prefer the tag **id** when
  a name is ambiguous — several tag names in project 1 are duplicated.
- `folder_paths` — folders by readable path, e.g. `"Web > Password Manager"`. Each expands to that folder
  **and all descendants** (set `include_subfolders: false` for exact-folder-only). Paths are OR'd. The
  script resolves paths against the live folder tree and **fails fast** if any path is unmatched, so specs
  survive folder renames being caught rather than silently dropping cases. `folder_ids` does the same by id.
- `test_type_ids` / `team_ids` — the case's multiselect set must **intersect** the list.
- `case_state_ids` — the case `state_id` must be in the list (`4` = Active).
- `automation_type_ids` — include only these automation types (`null` in the list = "no type set").
- `exclude_automation_type_ids` — drop cases with these automation types. Prefer this for "manual only"
  (`[10, 23, 24]`) so newly-added _non-automated_ types are included by default.
- `has_automation` — bool; matches the case flag. NOTE: as of 2026-07 every Regression-typed case in
  project 1 has `has_automation=false`, so this is rarely a useful filter for the manual suite.

The script refuses to create a run matching zero cases.

## Run naming

Keep `run_name` to the bare domain/area — e.g. `"Password Manager"`, `"Admin Console"`,
`"Directory Connector (BWDC)"`. Do **not** encode the platform, the word "Regression", or the release
period in the name:

- The **release/period** is conveyed by the parent milestone the run is linked to, so `<period>` no longer
  belongs in `run_name` (the `--period` substitution remains for any spec that still uses the placeholder).
- The **platform variant** is conveyed by the run's Testmo **Configuration** (`config_id`), not the name.
  Both mobile specs are therefore named just `"Mobile"` and distinguished by config
  (`config_id` 1 = Android, 3 = iOS). Look up config ids via `GET /projects/{id}/configs`.

## Multi-configuration runs (Mobile, Desktop, Extension)

Some platforms ship **several same-named runs distinguished only by Testmo Configuration**. Each variant
is its own spec file with the same `run_name` and a different `config_id`.

Testmo's `/cases` API **cannot filter by configuration** and exposes no per-case config assignment, so
these are always **two-step runs**: the spec reproduces step 1, and removing the non-target
configuration's cases is a manual UI pass. Each affected spec documents its own step 2 in `_comment`.

- **Mobile** — 2 runs, both named `Mobile`. Same filters, differing only by which automation type is
  excluded. `config_id` 1 = Android, 3 = iOS.

Desktop and Extension instead use a **broad + narrow** split, where one variant covers the full folder and
the rest are driven by an "essential" tag:

- **Desktop** — 3 runs, all named `Desktop`. Broad = **macOS** (21); narrow = **Windows** (22), **Linux**
  (20), driven by the `desktop-essential` tag (id 15999).
- **Extension** — 4 runs, all named `Extension`. Broad = **`MacOS, Chrome`** (7); narrow =
  **`Windows, Edge`** (15), **`MacOS, Safari`** (10), **`Linux, Firefox`** (5), driven by the
  `extension-essential` tag (id 17190).

Config and tag ids above verified 2026-08-28 via `GET /projects/1/configs` and `GET /projects/1/tags`.

Every variant on both platforms — broad and narrow alike — takes a step 2. The two variant types differ
only in how cases are selected:

|            | Broad                               | Narrow                                       |
| ---------- | ----------------------------------- | -------------------------------------------- |
| Scope      | whole top-level folder + subfolders | the `<platform>-essential` tag (server-side) |
| Test Type  | Smoke + Regression                  | **any** — the tag defines the scope          |
| Case state | Active                              | Active                                       |
| Automation | manual only (exclude 10, 23, 24)    | manual only (exclude 10, 23, 24)             |

Narrow variants deliberately drop the **test-type** filter — a tagged case counts regardless of type — but
they keep the **state** and **automation-type** filters so retired and already-automated cases stay out.

Verify tag names against `GET /projects/1/tags` before trusting a narrow spec: it has no folder or type
filter to constrain it, so a wrong or duplicated tag name silently yields the wrong case set rather than
erroring.

**`"config_id": null` is a deliberate placeholder** meaning "this run needs a Configuration that has not
been looked up yet." Dry-runs still work so case counts can be validated, but `--create` is refused —
otherwise the variants would be indistinguishable from each other. Fill it in from
`GET /projects/{id}/configs`.

## Project 1 field reference (captured 2026-07-22 — re-verify via `/projects/1/fields`)

- **Test Type** (`custom_test_type`, multiselect): 18=Functional, 19=Regression, 20=Smoke,
  21=Accessibility, 22=Compatibility.
- **Automation Type** (`custom_automation_type`, single): 8=Not Automating, 11=Ready to Automate,
  9=In Progress, 10=Automated, 23=Automated-Android, 24=Automated-iOS, 12=Blocked. "Manual only" =
  exclude {10, 23, 24}.
- **Case `state_id`**: 4=Active (~94% of cases), 5=(inactive/deprecated), plus legacy strays. Regression
  runs filter to `[4]`.
- **Team** (`custom_team`, multiselect): 25=Admin Console, 26=Auth, 27=Autofill, 28=Billing,
  38=Desktop Native, 29=DIRT, 30=Key Management, 31=Mobile, 37=Passwordless, 32=Platform,
  33=Secrets Manager, 34=Tools, 35=UI Foundation, 36=Vault.
- **Top-level folders**: Web=3136, Extension=2779, Mobile=3010, Desktop=2923, CLI=2858, API=3390,
  Passwordless=3103. (Excluded as junk: "Retired Test Cases"=81330, "Need to be deleted"=371518.)

## Guardrails

- **Dry-run by default** — the script writes only with `--create`.
- **Sandbox first** — validate new specs against project `2` before touching project `1`.
- **Idempotent** — do not create a duplicate run for a period/milestone.
- **Committed specs** — prefer a reviewed spec file over ad-hoc arguments.
- **Never expose the key** — reference `TESTMO_API_KEY` only.

## Milestones

Each period's runs should link to a milestone (e.g. `2026.8.0 Manual Regression`). The Testmo web UI
groups releases as a parent `YYYY.M.0 Release` milestone with `… Manual Regression` and
`… Automated Regression` children.

- **Creating the milestone is MANUAL.** The Testmo v1 API has **no** milestone-create route
  (`POST /projects/{id}/milestones` returns "method not supported" — the endpoint is GET/HEAD only).
  Create the period's milestone in the Testmo UI first.
- **Linking runs is automated.** Find the milestone id (`GET /projects/1/milestones`, newest first, or from
  the UI), then either put `milestone_id` in each spec or pass `--milestone-id <id>` at run time — verified
  to attach the run to the milestone.

## Setting up a whole release (recommended)

Use `setup_release_runs.py` to create every run for a release in one pass, linked to a milestone.
Release membership lives in `release-profiles.json` — each profile lists its specs, and a profile may
`extends` another.

`full` is **not** a superset of `partial`. Both extend a shared `common` base; the difference is:

- **`common`** — the specs every release runs (Web PM / Admin Console / Admin Portal, Old Client / New
  Server, both Mobile). Not meant to be run directly.
- **`partial`** — `common` + **Directory Connector (BWDC)**, which runs on partial releases only.
- **`full`** — `common` + CLI + the 3 Desktop and 4 Extension configuration variants. No BWDC.

```bash
# 1. Create the period's milestone in the Testmo UI, e.g. "2026.8.0 Manual Regression".
# 2. Dry-run the whole release (prints a run/case-count summary; creates nothing):
python3 scripts/setup_release_runs.py --release full --milestone-name "2026.8.0 Manual Regression"
# 3. Create them all once the summary looks right:
python3 scripts/setup_release_runs.py --release full --milestone-name "2026.8.0 Manual Regression" --create
```

It resolves the milestone by name (fails if missing/ambiguous — the API can't create milestones), derives
`--period` from the milestone name (override with `--period`), fetches cases/folders once for the whole
set, and links every run to the milestone. Default project is 1; override with `--project` (e.g. 2 for
sandbox testing).

**Skipping a component for one release** — use `--exclude <spec-name>` (repeatable, or comma-separated)
when a release does not need one of the profile's runs. Spec names are the file names in `specs/` without
the `.json`:

```bash
python3 scripts/setup_release_runs.py --release partial \
  --milestone-name "2026.8.1 Manual Regression" \
  --exclude directory-connector-regression --create
```

The excluded specs are listed in the summary header. A name that is not in the profile is a hard error
rather than a no-op, so a typo cannot silently create the run you meant to skip. Reach for `--exclude` for
one-off omissions; if a set of runs is skipped every cycle, add a profile to `release-profiles.json`
instead.

For a single run, `testmo_create_run.py --spec <file> [--milestone-id N] [--period X]` still works.

## Per-run counts drift

Case counts change as the repository evolves — a spec that matched 202 last cycle may match 196 this
cycle. That is expected; the tooling always reflects live data. Review the dry-run summary each period.

## Not yet implemented (next steps)

- Seed the `full` profile's additional specs as they are captured.
