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

- `TESTMO_API_KEY` exported in the environment. Reference it only by variable — never print, echo, log,
  commit, or pass the value as a command-line argument (argv is readable by other local users).
- `python3` available on `PATH` (the scripts use only the standard library).
- `curl` is **not** normally needed, but is used as a fallback on networks running TLS interception.
  It ships with macOS, Windows 10+, and most Linux distributions. The scripts switch to it by
  themselves on a `CERTIFICATE_VERIFY_FAILED`; if you need to know why, see
  [references/tls-inspecting-proxies.md](references/tls-inspecting-proxies.md).

## Locating the scripts and specs

The scripts and the committed specs ship **inside the installed plugin**, not in the user's working
directory. Always address them through `${CLAUDE_PLUGIN_ROOT}`; a bare `scripts/…` or `specs/…` path
resolves against whatever repository the user happens to be in and will not exist. Every command below
opens by setting a shorthand, because shell state does not carry over between commands:

```bash
SKILL="${CLAUDE_PLUGIN_ROOT}/skills/creating-regression-runs"
```

A user's own spec file is the exception — pass its real path, wherever it lives.

## Reference material

Endpoints, project ids, and the numeric ids behind every field value live in
[references/api-reference.md](references/api-reference.md). Read it before writing a new spec or
diagnosing one that selects the wrong cases. The base URL is
`https://bitwarden.testmo.net/api/v1` and every shipped spec targets project `1` (live Bitwarden).

## Workflow

1. **Define or load the filter spec** (see schema below). Start from
   `${CLAUDE_PLUGIN_ROOT}/skills/creating-regression-runs/specs/regression-run.template.json`. Commit one
   spec file per recurring run so it is reviewable and reproducible.
2. **Dry-run the spec** and confirm the matched case count, the sample cases, and the run payload look
   right:
   ```bash
   SKILL="${CLAUDE_PLUGIN_ROOT}/skills/creating-regression-runs"
   python3 "$SKILL/scripts/testmo_create_run.py" --spec "$SKILL/specs/<run>.json"
   ```
   A dry-run reads live data but writes nothing, so this is the review step for a new spec as well as for
   each period's run. Compare the count against the previous cycle — a large swing usually means a
   renamed folder or a changed tag rather than real repository churn.
3. **Idempotency check:** confirm a run for this period/milestone does not already exist
   (`GET /projects/1/runs`) before creating another. This step is manual for a single run —
   `setup_release_runs.py` performs it for you and refuses on a collision.
4. **Create the run** only after **the user** has reviewed the dry-run. Print the dry-run summary
   — matched case count, sample cases, run payload — and obtain their explicit confirmation first.
   **Never issue the dry-run and the `--create` in the same turn:** reviewing your own dry-run and
   proceeding is not the review step, and this write mutates the live instance.
   ```bash
   SKILL="${CLAUDE_PLUGIN_ROOT}/skills/creating-regression-runs"
   python3 "$SKILL/scripts/testmo_create_run.py" --spec "$SKILL/specs/<run>.json" --create
   ```

## Filter-spec schema

A spec has two distinct halves. **Top-level keys describe the run that gets created**; **keys under
`filters` select which cases go into it.** They are not interchangeable, and `tags` exists in both — see
the warning below.

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

### Top-level keys (the run payload)

- `project_id` — **required.** The Testmo project the run is created in. `1` is the live Bitwarden
  repository; every shipped spec pins it.
- `run_name` — **required.** See [Run naming](#run-naming).
- `run_state_id` — run state; `7` (In progress) is the default and what active runs use.
- `milestone_id` — milestone to link the run to. Usually supplied at run time by `--milestone-id` or by
  `setup_release_runs.py` instead of being committed.
- `config_id` — Testmo Configuration, for platforms that ship several same-named runs (omit it otherwise).
  See [references/multi-configuration-runs.md](references/multi-configuration-runs.md).
- `tags` — **labels applied to the created run.** These do _not_ select cases.
- `note` — free-text note on the run.
- `filters` — the case-selection block, below.

### Keys under `filters` (case selection)

Every key is optional — omit a key to skip that dimension. A case must match **all** provided keys (keys
are ANDed; multi-value lists within a key are ORed).

> **A spec with an empty or missing `filters` block matches every case in the project.** No filter means
> no constraint, so `--create` would build a run of all ~13.7k project-1 cases. The zero-case guard catches
> only the opposite mistake, so check the dry-run's case count before creating.

- `tags` — **selects cases** carrying these Testmo tag names or ids, applied **server-side** by the
  `/cases` API (`?tags=...`), then combined with any other filters. Prefer the tag **id** when a name is
  ambiguous — several tag names in project 1 are duplicated. Values are percent-encoded, so a tag name
  containing a space or a non-ASCII character is fine. Before trusting any tag filter the script probes
  `/cases` with a tag no case can carry: this API ignores query parameters it does not recognize, and a
  tag-only spec has nothing else constraining it, so an ignored `?tags=` would select the whole project.
  A non-empty probe result is a hard error.
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

### `tags` in both halves

A **tag-only spec** — one where membership in the run is defined purely by a Testmo tag — must set
`filters.tags`. Setting only the top-level `tags` labels the run and selects nothing, which leaves the
spec matching every case in the project. Shipped example
(`specs/old-client-new-server-regression.json`), which sets both deliberately:

```json
{
  "project_id": 1,
  "run_name": "Old Client / New Server",
  "run_state_id": 7,
  "tags": ["oldnew"],
  "filters": { "tags": ["oldnew"] }
}
```

The script refuses to create a run matching zero cases.

## Run naming

Keep `run_name` to the bare domain/area — e.g. `"Password Manager"`, `"Admin Console"`,
`"Directory Connector (BWDC)"`. Do **not** encode the platform, the word "Regression", or the release
period in the name:

- The **release/period** is conveyed by the parent milestone the run is linked to, so `<period>` no longer
  belongs in `run_name` (the `--period` substitution remains for any spec that still uses the placeholder).
- The **platform variant** is conveyed by the run's Testmo **Configuration** (`config_id`), not the name
  — see [references/multi-configuration-runs.md](references/multi-configuration-runs.md).
  Both mobile specs are therefore named just `"Mobile"` and distinguished by config
  (`config_id` 1 = Android, 3 = iOS). Look up config ids via `GET /projects/{id}/configs`.

## Guardrails

- **Dry-run by default** — the script writes only with `--create`.
- **The user reviews the dry-run, not you** — a dry-run reads live project `1` data and writes nothing,
  so it is the real guardrail, and it is only a guardrail if a human reads it. Print the summary, check
  the case count against the previous cycle, and get explicit confirmation before `--create`. Never
  issue the dry-run and the `--create` in the same turn.
- **Multi-configuration runs are not finished when the script exits** — every run created with a
  `config_id` (all Mobile, Desktop, and Extension runs) needs the manual step 2 described in
  [references/multi-configuration-runs.md](references/multi-configuration-runs.md). Tell the user which
  runs still need it; the scripts list them.
- **Idempotent** — do not create a duplicate run for a period/milestone. `setup_release_runs.py` enforces
  this: it refuses to create when the milestone already has runs linked, unless `--allow-existing` is
  passed. For a single run, check by hand (workflow step 3).
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
SKILL="${CLAUDE_PLUGIN_ROOT}/skills/creating-regression-runs"
# 1. Create the period's milestone in the Testmo UI, e.g. "2026.8.0 Manual Regression".
# 2. Dry-run the whole release (prints a run/case-count summary; creates nothing):
python3 "$SKILL/scripts/setup_release_runs.py" --release full --milestone-name "2026.8.0 Manual Regression"
# 3. Create them all once the USER has confirmed the summary (never in the same turn as step 2):
python3 "$SKILL/scripts/setup_release_runs.py" --release full --milestone-name "2026.8.0 Manual Regression" --create
# 4. Finish the multi-configuration runs by hand in the Testmo UI — see below.
```

**Step 3 needs the user's explicit approval.** Show them the dry-run summary and wait; do not run
the dry-run and `--create` in the same turn.

**Step 4 is mandatory, not optional.** A `--release full` run creates 14 runs, and 9 of them — 2
Mobile, 3 Desktop, 4 Extension — are
[multi-configuration runs](references/multi-configuration-runs.md)
that the API can only get halfway. Each one still needs a Testmo UI pass to remove the non-target
configuration's cases, and until that pass is done the run holds the wrong case set. `--release
partial` creates 7 runs, 2 of which (both Mobile) need it. Both scripts name the affected runs in
their output; each spec's `_comment` gives the exact pass for that run.

It resolves the milestone by name (fails if missing/ambiguous — the API can't create milestones), derives
`--period` from the milestone name (override with `--period`), fetches cases/folders once for the whole
set, and links every run to the milestone.

**The target project comes from the specs.** There is no `--project` flag: the orchestrator reads
`project_id` from every spec in the profile and refuses to run if they disagree, matching
`testmo_create_run.py`, which has always treated the spec as authoritative. A flag that outranked each
spec's own `project_id` could create a spec into a project it was never written for.

It creates as many runs as it can rather than stopping at the first failure, then prints a
`created / skipped / failed` tally. A partial failure names each run that did not make it — by run name
**and** spec name, since multi-config runs share a run name — and exits non-zero, because the milestone is
then only partly populated.

**Duplicate protection.** Before doing anything, it lists the runs already linked to the resolved
milestone. A dry-run reports the count; `--create` refuses outright, so running the same command twice
cannot quietly produce a second full set of runs. Pass `--allow-existing` when the duplicates are
intended, or `--exclude` the specs whose runs already exist — that is the normal way to add one missing
run to a milestone that is already set up.

**Skipping a component for one release** — use `--exclude <spec-name>` (repeatable, or comma-separated)
when a release does not need one of the profile's runs. Spec names are the file names in `specs/` without
the `.json`:

```bash
SKILL="${CLAUDE_PLUGIN_ROOT}/skills/creating-regression-runs"
python3 "$SKILL/scripts/setup_release_runs.py" --release partial \
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
