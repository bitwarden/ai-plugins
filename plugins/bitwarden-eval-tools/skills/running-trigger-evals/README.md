# running-trigger-evals

Runs and reports reproducible trigger-rate evals for a Bitwarden skill's
`description` / `when_to_use` text: does it fire on the real phrasings it should
catch, and stay silent on near-misses?

This is the standard tool for the **Triggering** assertion category. For
Structure and Behavior evals, use `/skill-creator:skill-creator` instead.

## When it triggers

- Editing a skill's `description` / `when_to_use` frontmatter and confirming
  triggering hasn't regressed.
- A net-new skill needs an eval set and baseline per the review gate.
- Asks like "run a trigger eval", "check the trigger rate", "test if my skill
  still fires", "compare against baseline".

## Two modes

- **installed**: skill's plugin is already registered; watches the real token.
- **isolated**: skill not yet registered (in development / unmerged PR); writes
  a throwaway command file carrying the skill's real description, watches for it,
  and cleans up.

## Quick start

Installed skill:

```bash
python3 scripts/trigger_eval.py \
  --mode installed \
  --eval-set path/to/trigger-eval.json \
  --skill-token my-skill-token \
  > /tmp/report.json
```

Isolated skill:

```bash
python3 scripts/trigger_eval.py \
  --mode isolated \
  --eval-set path/to/trigger-eval.json \
  --skill-path path/to/skills/my-skill \
  > /tmp/report.json
```

Regression check against a recorded baseline:

```bash
python3 scripts/trigger_eval.py \
  --mode installed --eval-set eval.json --skill-token my-skill-token \
  --baseline baseline.json --check-regression \
  > /tmp/report.json   # exits 1 if a regression is flagged
```

## Files

- `SKILL.md`: main instructions.
- `scripts/trigger_eval.py`: the runner (stdlib-only, Python 3.10+).
- `references/cli-reference.md`: full flag table, report schema, exit codes.
- `references/authoring-eval-sets.md`: balance, near-misses, blinding.
- `examples/sample-eval-set.json`: a tiny 4-case set.
- `examples/sample-report.json`: an annotated output example.

## Requirements

- Python 3.10+ (stdlib only).
- `claude` CLI on `PATH`.
