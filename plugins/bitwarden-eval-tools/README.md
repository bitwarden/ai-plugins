# Bitwarden Eval Tools Plugin

Evidence that a skill works. Two skills answer the two questions worth asking
about one: does it fire when it should, and does it change what the model
produces.

## Overview

`running-trigger-evals` answers the first. It genericizes the hand-rolled
trigger-eval pattern, asking whether the model reaches for a skill on the real
phrasings its `description` and `when_to_use` are meant to catch, and stays
silent on near-misses.

`running-behavioral-evals` answers the second. Skills accrete instructions over
time and few are ever tested in isolation, so nobody knows which ones change
behavior and which only cost tokens. It compares two variants on real inputs in
blind paired runs and grades them against ground truth verified against the
live system.

Use `/skill-creator:skill-creator` for structural review of a skill's wording
and layout.

## `running-trigger-evals`

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

## `running-behavioral-evals`

Run a behavioral A/B evaluation of a skill. You compare two variants (for example a stripped-down "min" against a rich original) on real inputs, in isolated blind sessions that cannot see each other, then grade their outputs against ground truth you verified against the live system. The result is an evidence-backed verdict on which variant is better, and a documented experiment anyone can pick up and continue.

What it carries:

- **The six-phase loop:** scaffold, design the blinded run, run in isolation, taint-check and quarantine, grade against ground truth, decide or accrete.
- **Isolation and blinding** (`references/isolation-and-blinding.md`): why decisive runs need separate top-level sessions rather than subagents, how to avoid priming the subject, and how to prove the blind held.
- **Grading** (`references/grading.md`): why the original skill is not a stable oracle, how to establish ground truth from the live system, and how to measure the run-to-run noise floor before trusting a difference.
- **Ablation-accretion** (`references/ablation-accretion.md`): strip a skill to its skeleton, then add a directive back only when a run reproduces the failure it prevents. Includes the trap where two individually-earned directives combine into a loophole.
- **Conventions** (`references/conventions.md`): experiment directory layout, run-artifact naming, the version ledger and directive table, and known environment gotchas.
- **Templates** (`assets/`): copy-paste starting points for the session-state doc, the directive ledger, and the blinded run prompts.

**When to use it:** "eval this skill", "which of these two skill versions is better", "is the stripped-down version as good as the original", "prove this instruction earns its place". It is not for static/structural review of a skill's wording, for trigger-rate evaluation (whether a skill fires), or for evaluating agents.

## Installation

### Add the Bitwarden Marketplace (if not already added)

```bash
/plugin marketplace add bitwarden/ai-plugins
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
    ├── running-trigger-evals/
    │   ├── SKILL.md                # Main skill instructions
    │   ├── README.md               # Skill-specific documentation
    │   ├── scripts/
    │   │   └── trigger_eval.py     # The runner (stdlib-only)
    │   ├── references/
    │   │   ├── cli-reference.md    # Flags, report schema, exit codes
    │   │   └── authoring-eval-sets.md
    │   └── examples/
    │       ├── sample-eval-set.json
    │       └── sample-report.json
    └── running-behavioral-evals/
        ├── SKILL.md                # The six-phase loop
        ├── references/
        │   ├── ablation-accretion.md
        │   ├── conventions.md
        │   ├── grading.md
        │   └── isolation-and-blinding.md
        └── assets/                 # Experiment scaffold templates
```

## Requirements

- Python 3.10+ (uses PEP 604 `X | None` type hints; stdlib only).
- The `claude` CLI available on `PATH`.

## Relationship to skill-creator

`running-behavioral-evals` reuses Anthropic's `skill-creator` for the mechanics: its eval viewer, the `grading.json` field shape, its rubric template, its benchmark aggregator, and its optional blind comparator agent. It owns what skill-creator does not have: separate-session isolation, the taint check, quarantine, the naming convention, ground truth verified against the live system rather than against the other variant, the noise floor, and the ablation-accretion ledger.

## Contributing

Contributions welcome. Please follow:

- [Bitwarden Contributing Guidelines](https://contributing.bitwarden.com)
- Repository standards in the root `README.md`

## Support

- **Issues**: [GitHub Issues](https://github.com/bitwarden/ai-plugins/issues)
- **Marketplace**: [Bitwarden AI Plugins](https://github.com/bitwarden/ai-plugins)
