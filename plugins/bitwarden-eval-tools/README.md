# Bitwarden Eval Tools Plugin

A reusable trigger-rate eval runner for Bitwarden skills. Genericizes the
hand-rolled "trigger eval" pattern (does a skill fire on the right prompts and
stay silent on the wrong ones) into a single tool any plugin can invoke.

## Overview

Trigger evals answer one narrow question about a skill's `description` /
`when_to_use` text: does the model reach for the skill on the real phrasings it
is meant to catch, and does it stay silent on near-misses? This plugin is the
standard runner for that question. Use `/skill-creator:skill-creator` for
Structure and Behavior evals; use this for Triggering.

## Features

- **Two modes**
  - **installed**: evaluate a skill whose plugin is already registered in the
    running environment. Watches the real skill token.
  - **isolated**: evaluate a skill still in development or on an unmerged PR.
    Writes a throwaway slash-command file carrying the skill's real description
    into `<project_root>/.claude/commands/`, watches for it, and always cleans up.
- **Tolerant scanning.** Both modes scan past unrelated `Skill` / `Read` tool
  calls so accounts that auto-fire session-init skills first do not produce false
  negatives. This is the reason the runner exists rather than skill-creator's
  stricter harness.
- **Reliability-aware reporting.** Alongside the blended pass rates (threshold
  0.5), a `reliability` block reports a per-case `all_runs_agree` pass^k signal.
- **Balance warning.** Non-blocking stderr warning when the true/false split is
  skewed by more than ~20%.
- **Opt-in regression check.** `--check-regression` compares a fresh run against
  a recorded baseline (matched by query string), flags hard and reliability
  regressions, and exits `1` on either, always printing the full summary.
- **Report-only sibling exclusion.** `--exclude-skill` records whether named
  sibling tokens also fired, for catching triggering overlap between skills,
  without changing pass/fail semantics.

## Installation

### Add the Bitwarden Marketplace (if not already added)

```bash
/plugin marketplace add bitwarden/ai-marketplace
```

### Install the plugin

```bash
/plugin install bitwarden-eval-tools@bitwarden-marketplace
```

## Usage

The `running-trigger-evals` skill triggers when you are editing a skill's
`description` / `when_to_use` frontmatter and need to confirm triggering hasn't
regressed, when a net-new skill needs an eval set and baseline, or when you ask
to "run a trigger eval", "check the trigger rate", or "compare against baseline".

Run the script directly for an installed skill:

```bash
python3 plugins/bitwarden-eval-tools/skills/running-trigger-evals/scripts/trigger_eval.py \
  --mode installed \
  --eval-set path/to/trigger-eval.json \
  --skill-token my-skill-token \
  --runs-per-query 3 --num-workers 8 --timeout 45
```

Or an isolated (not-yet-installed) skill:

```bash
python3 plugins/bitwarden-eval-tools/skills/running-trigger-evals/scripts/trigger_eval.py \
  --mode isolated \
  --eval-set path/to/trigger-eval.json \
  --skill-path path/to/skills/my-skill
```

See the skill's [`references/cli-reference.md`](skills/running-trigger-evals/references/cli-reference.md)
for the full flag table, report schema, and exit codes.

## Plugin Structure

```
plugins/bitwarden-eval-tools/
├── .claude-plugin/
│   └── plugin.json                 # Plugin manifest
├── README.md                       # This file
├── CHANGELOG.md
└── skills/
    └── running-trigger-evals/
        ├── SKILL.md                # Main skill instructions
        ├── README.md               # Skill-specific documentation
        ├── scripts/
        │   └── trigger_eval.py     # The runner (stdlib-only)
        ├── references/
        │   ├── cli-reference.md     # Flags, report schema, exit codes
        │   └── authoring-eval-sets.md
        └── examples/
            ├── sample-eval-set.json
            └── sample-report.json
```

## Requirements

- Python 3.10+ (uses PEP 604 `X | None` type hints; stdlib only).
- The `claude` CLI available on `PATH`.

## Contributing

Contributions welcome. Please follow:

- [Bitwarden Contributing Guidelines](https://contributing.bitwarden.com)
- Repository standards in the root `README.md`

## Support

- **Issues**: [GitHub Issues](https://github.com/bitwarden/ai-marketplace/issues)
- **Marketplace**: [Bitwarden AI Marketplace](https://github.com/bitwarden/ai-marketplace)
