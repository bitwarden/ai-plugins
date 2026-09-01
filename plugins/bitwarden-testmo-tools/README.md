# Bitwarden Testmo Tools

Tool-integration plugin that connects Claude Code to Bitwarden's [Testmo](https://bitwarden.testmo.net)
instance via its REST API. It lets Claude read and analyze the test-case repository and run history, and
create regression test runs from reviewable, committed filter specs — without hand-crafting API calls.

## Overview

Bitwarden runs recurring regression cycles in Testmo. Selecting the right cases for a run and creating it
by hand is repetitive and error-prone. This plugin makes the "filter cases → create run" workflow
repeatable and reviewable:

- **Read + analyze** the case repository, folders, milestones, and manual/automation run history.
- **Create regression runs** from a JSON filter spec (folders, test types, teams, automation type, case
  state, `has_automation`), with a mandatory dry-run before anything is written.

Writes mutate the live Testmo instance, so the workflow is built around review: dry-run first,
idempotency checks, and a committed spec per run.

## Installation

Install from the Bitwarden AI Plugins marketplace:

```
/plugin marketplace add bitwarden/ai-plugins
/plugin install bitwarden-testmo-tools
```

### Prerequisites

- A Testmo API key exported as `TESTMO_API_KEY` in your shell environment (e.g. `~/.zshrc`).
  The key is read from the environment and never printed, committed, or passed on a command line.
- `python3` on your `PATH` (the scripts use only the standard library).

## Usage

The `creating-regression-runs` skill drives the workflow. In Claude Code:

> Create the bimonthly regression run for this period in Testmo.

Or run the bundled script directly. It defaults to a **dry-run** and only writes when `--create` is passed.
The paths below are relative to this plugin directory — from an installed plugin, prefix them with
`${CLAUDE_PLUGIN_ROOT}/`, since the scripts live in the plugin cache rather than your working directory:

```bash
# Dry-run: show matched case count and the run payload, create nothing
python3 skills/creating-regression-runs/scripts/testmo_create_run.py --spec my-run.json

# Create the run after reviewing the dry-run output
python3 skills/creating-regression-runs/scripts/testmo_create_run.py --spec my-run.json --create
```

See [`skills/creating-regression-runs/SKILL.md`](skills/creating-regression-runs/SKILL.md) for the full
workflow, guardrails, and the filter-spec schema. A template lives at
[`skills/creating-regression-runs/specs/regression-run.template.json`](skills/creating-regression-runs/specs/regression-run.template.json).

## Safety

- **Never commit credentials.** The API key is referenced only via `TESTMO_API_KEY`.
- **Dry-run by default.** Runs are created only with an explicit `--create` flag, after review. A dry-run
  reads the live repository (project `1`) and writes nothing, so it is safe to repeat.
- The script refuses to create a run that matches zero cases, and fails fast when a spec references a
  folder that no longer exists rather than silently selecting fewer cases.
