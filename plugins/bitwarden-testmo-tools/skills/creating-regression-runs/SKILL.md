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
  "run_name": "Web Regression — Password Manager (2026-07)",
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
  (`[10, 23, 24]`) so newly-added *non-automated* types are included by default.
- `has_automation` — bool; matches the case flag. NOTE: as of 2026-07 every Regression-typed case in
  project 1 has `has_automation=false`, so this is rarely a useful filter for the manual suite.

The script refuses to create a run matching zero cases.

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

Per-period flow:

```bash
# 1. Create "2026.8.0 Manual Regression" in the Testmo UI, note its id (say 251).
# 2. Create each run linked to it, filling the <period> placeholder:
python3 scripts/testmo_create_run.py --spec specs/web-password-manager-regression.json \
    --period 2026.8.0 --milestone-id 251 --create
# ...repeat for each spec.
```

## Not yet implemented (next steps)

- Optional helper to create all specs' runs in one pass for a period.
