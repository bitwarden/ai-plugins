---
name: creating-test-runs
description: Create test runs in Bitwarden's Testmo instance from reviewable JSON filter specs. Use when asked to create one or more Testmo runs, link runs to a Testmo milestone, select cases for a run, or write or debug a run filter spec built from folder/tag/test-type/team/automation filters. Accepts several specs in one pass. Dry-run first; writes mutate the live instance. For a release's QA manual regression suite, use bitwarden-testing-tools' setting-up-regression-runs instead — it owns the release profiles and specs and delegates here.
---

# Creating Test Runs in Testmo

`scripts/testmo_create_runs.py` selects the cases each filter spec matches and, only with `--create`,
creates one run per spec through the Testmo API.

**Writes mutate the live Testmo instance. Always dry-run and have the user review before `--create`.**

## Prerequisites

- `TESTMO_API_KEY` exported in the environment. Reference it only by variable — never print, echo, log,
  commit, or pass the value as a command-line argument.
- `python3` on `PATH`. `curl` is used automatically as a fallback on TLS-inspecting networks; see
  [`references/tls-inspecting-proxies.md`](references/tls-inspecting-proxies.md) only if that fallback
  needs explaining.

## Paths

The script ships inside the installed plugin, so always address it through `${CLAUDE_PLUGIN_ROOT}`.
Shell state does not carry over between commands, so set the shorthand in every command:

```bash
SKILL="${CLAUDE_PLUGIN_ROOT}/skills/creating-test-runs"
```

Specs can live anywhere; pass their real paths. Never write a user's spec into `$SKILL/` — that is the
plugin cache, and `/plugin update` overwrites it.

## Workflow

1. **Get the specs.** Use the spec paths you were given, or write a new spec starting from
   [`examples/test-run.template.json`](examples/test-run.template.json), saved outside the plugin.
   Read [`references/api-reference.md`](references/api-reference.md) for the ids behind field values
   before writing or debugging a spec.
2. **Confirm the milestone exists.** The API cannot create milestones; the user creates them in the
   Testmo UI. Link runs with `--milestone-name "<exact name>"` or `--milestone-id <id>`.
3. **Dry-run.** Pass `--spec` once per run:
   ```bash
   SKILL="${CLAUDE_PLUGIN_ROOT}/skills/creating-test-runs"
   python3 "$SKILL/scripts/testmo_create_runs.py" \
     --spec /path/to/a.json --spec /path/to/b.json \
     --milestone-name "<exact milestone name>"
   ```
   A single spec also prints its folder resolution, sample cases, and run payload.
4. **Show the user the dry-run output and stop.** Point out every row whose STATUS is not `ready`, the
   `Existing` line, and any case count that looks off (a large swing from last cycle usually means a
   renamed folder or tag). Wait for explicit confirmation. **Never run the dry-run and `--create` in the
   same turn.**
5. **Create** by re-running the identical command with `--create`.
6. **Report the result**, including every run listed under `MANUAL STEP 2 REQUIRED` — those runs are
   unfinished until the user does the UI pass in
   [`references/multi-configuration-runs.md`](references/multi-configuration-runs.md).

## Reading the dry-run

| STATUS            | Meaning                                                     | Fix                                                            |
| ----------------- | ----------------------------------------------------------- | -------------------------------------------------------------- |
| `ready`           | Will be created.                                            | —                                                              |
| `NEEDS CONFIG_ID` | Spec has `"config_id": null`.                               | Look the id up via `GET /projects/{id}/configs`; set it.       |
| `EMPTY — 0 cases` | Filters match nothing.                                      | Check the spec's folders and tags against the live repository. |
| `DUPLICATE — …`   | Same run (name + config) already in the milestone or batch. | Drop that spec, or pass `--allow-existing` if intended.        |
| `FOLDER ERROR`    | A folder path or id did not resolve.                        | Fix the spec; the script stops before anything else.           |

`--create` refuses the whole batch unless every row is `ready`. The `Existing` line reads `NOT CHECKED`
without a milestone, and `CANNOT CHECK` when the API hides milestone links — in that case have the user
check the milestone in the Testmo UI before creating.

If some creates fail, the script names them and exits non-zero. Re-run with only the failed specs; the
others already exist and would now report `DUPLICATE`.

## Filter-spec schema

Top-level keys describe the run; keys under `filters` select its cases.

```json
{
  "project_id": 1,
  "run_name": "Password Manager",
  "run_state_id": 7,
  "tags": ["regression"],
  "filters": {
    "folder_paths": ["Web > Password Manager"],
    "test_type_ids": [19, 20],
    "case_state_ids": [4],
    "exclude_automation_type_ids": [10, 23, 24]
  }
}
```

**Top level:** `project_id` and `run_name` are required; every spec in one invocation must share the
same `project_id`. Optional: `run_state_id` (default `7`, In progress), `milestone_id` (overridden by the
milestone flags), `config_id` (only for same-named runs split by Testmo Configuration), `tags` (labels
the run — does **not** select cases), `note`.

**Under `filters`** every key is optional; keys are ANDed, values within a key are ORed:

- `tags` — select cases carrying these tag names or ids. Prefer ids when a name is duplicated.
- `folder_paths` / `folder_ids` — folders and their descendants (`include_subfolders: false` for exact).
- `test_type_ids`, `team_ids` — the case's set must intersect the list.
- `case_state_ids` — e.g. `[4]` for Active.
- `automation_type_ids` / `exclude_automation_type_ids` — for manual-only, exclude `[10, 23, 24]`.
- `has_automation` — bool.

A run defined purely by a tag must set `filters.tags`; setting only the top-level `tags` selects
nothing. **An empty or missing `filters` block matches every case in the project**, so always check the
dry-run count.

Keep `run_name` to the bare area (e.g. `"Password Manager"`); the release comes from the milestone and
the platform from `config_id`.
