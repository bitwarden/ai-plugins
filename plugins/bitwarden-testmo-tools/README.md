# Bitwarden Testmo Tools

Tool-integration plugin that connects Claude Code to Bitwarden's [Testmo](https://bitwarden.testmo.net)
instance via its REST API. It creates test runs from reviewable JSON filter specs, without hand-crafting
API calls, so any team can make its recurring "filter cases → create run" workflow repeatable.

## Overview

The `creating-test-runs` skill selects the cases each spec matches (by folder, tag, test type, team,
automation type, and case state) and creates one run per spec:

- **Several specs per pass.** The folder tree and case list are fetched once for the whole batch, and
  `--create` refuses the batch unless every run is ready.
- **Milestone linkage** by milestone id or exact name.
- **Duplicate checks.** A run whose name and configuration already exist in the milestone is refused
  unless explicitly allowed.

Writes mutate the live Testmo instance, so the workflow is built around review: a dry-run the user reads
before anything is created.

Other plugins can build on this skill by handing it their own specs — for example, the
`bitwarden-testing-tools` `setting-up-regression-runs` skill passes it QA's release regression specs.

## Installation

Install from the Bitwarden AI Plugins marketplace:

```
/plugin marketplace add bitwarden/ai-plugins
/plugin install bitwarden-testmo-tools
```

### Prerequisites

- A Testmo API key exported as `TESTMO_API_KEY` in your shell environment (e.g. `~/.zshrc`).
  The key is read from the environment and never printed, committed, or passed on a command line.
- `python3` on your `PATH` (the script uses only the standard library).
- `curl` only as a fallback, on networks running TLS interception — the script detects that case and
  switches over on its own. It is already present on macOS, Windows 10+, and most Linux distributions.

## Usage

In Claude Code:

> Create a Testmo run from my-run.json and link it to the "2026.8.0 Manual Regression" milestone.

Or run the bundled script directly. It defaults to a **dry-run** and only writes when `--create` is passed.
The paths below are relative to this plugin directory — from an installed plugin, prefix them with
`${CLAUDE_PLUGIN_ROOT}/`, since the script lives in the plugin cache rather than your working directory:

```bash
# Dry-run: show each run's matched case count and status, create nothing
python3 skills/creating-test-runs/scripts/testmo_create_runs.py \
  --spec a.json --spec b.json --milestone-name "2026.8.0 Manual Regression"

# Create the runs after reviewing the dry-run output
python3 skills/creating-test-runs/scripts/testmo_create_runs.py \
  --spec a.json --spec b.json --milestone-name "2026.8.0 Manual Regression" --create
```

See [`skills/creating-test-runs/SKILL.md`](skills/creating-test-runs/SKILL.md) for the workflow and the
filter-spec schema. A template lives at
[`skills/creating-test-runs/examples/test-run.template.json`](skills/creating-test-runs/examples/test-run.template.json).

## Safety

- **Never commit credentials.** The API key is referenced only via `TESTMO_API_KEY`.
- **Dry-run by default.** Runs are created only with an explicit `--create` flag, after review. A dry-run
  reads live data and writes nothing, so it is safe to repeat.
- The script refuses runs that match zero cases, duplicates of runs already in the milestone, and specs
  that reference a folder that no longer exists, rather than silently creating the wrong run set.
