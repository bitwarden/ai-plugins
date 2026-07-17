# CLI reference: `trigger_eval.py`

Stdlib-only Python 3.10+ script. Prints a single JSON summary to stdout;
diagnostics (balance warnings, per-case PASS/FAIL, regression detail) go to
stderr.

## Flags

| Flag                 | Type                   | Default           | Required?                                                                                                                                                                             |
| -------------------- | ---------------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--mode`             | `{installed,isolated}` | n/a               | required                                                                                                                                                                              |
| `--eval-set`         | path                   | n/a               | required; JSON array of `{query, should_trigger}`                                                                                                                                     |
| `--skill-token`      | str                    | n/a               | required in `installed` mode unless `--skill-path` is given (then derived from the parsed `name:` frontmatter field); ignored with a stderr warning in `isolated` mode                |
| `--skill-path`       | path                   | n/a               | required in `isolated` mode; optional in `installed` mode as a source for deriving `--skill-token`                                                                                    |
| `--description`      | str                    | n/a               | optional, isolated mode only: override the description baked into the temp command file (to test a candidate `SKILL.md` edit before writing it); warned and ignored in installed mode |
| `--exclude-skill`    | str (repeatable)       | `[]`              | optional, either mode: sibling skill token(s) to also watch for. Report-only, not a pass/fail gate                                                                                    |
| `--project-root`     | path                   | auto-detected     | optional, isolated mode only: overrides `find_project_root()`; warned and ignored in installed mode                                                                                   |
| `--runs-per-query`   | int                    | `3`               | optional                                                                                                                                                                              |
| `--num-workers`      | int                    | `8`               | optional                                                                                                                                                                              |
| `--timeout`          | int                    | `45`              | optional (seconds per run)                                                                                                                                                            |
| `--model`            | str                    | `claude-opus-4-7` | optional                                                                                                                                                                              |
| `--baseline`         | path                   | n/a               | required only if `--check-regression` is set                                                                                                                                          |
| `--check-regression` | flag                   | `False`           | optional                                                                                                                                                                              |

### Cross-field validation

Enforced after parsing (`parser.error(...)`), so the failure is a clean CLI
error rather than a traceback:

- `--mode installed` requires `--skill-token` or `--skill-path`.
- `--mode isolated` requires `--skill-path`.
- `--check-regression` requires `--baseline`.

## Report JSON schema (stdout)

```jsonc
{
  "mode": "installed", // or "isolated"
  "skill_token": "my-skill-token", // the watched token (installed) or null
  "skill_name": "my-skill", // parsed from SKILL.md when a path was given
  "runs_per_query": 3,
  "model": "claude-opus-4-7",
  "balance_warning": null, // string if the true/false split is skewed

  // Blended pass rates at threshold 0.5. Field names match the existing
  // creating-pull-request baseline.json for continuity.
  "should_trigger_pass_rate": 1.0, // fraction of should_trigger cases with rate >= 0.5
  "should_not_trigger_pass_rate": 0.9, // fraction of should_not cases with rate < 0.5
  "should_trigger_pass": "10/10",
  "should_not_trigger_pass": "9/10",

  // pass^k reliability signal: every run agreed with the expectation.
  "reliability": {
    "all_runs_agree_rate": 0.95,
    "should_trigger_reliable": "10/10",
    "should_not_trigger_reliable": "9/10",
  },

  "results": [
    {
      "query": "package this up into a draft pr",
      "should_trigger": true,
      "triggers": 3,
      "runs": 3,
      "trigger_rate": 1.0,
      "all_runs_agree": true,
      "sibling_fires": { "labeling-changes": 0 }, // present only with --exclude-skill
    },
    // ...one entry per eval case
  ],

  // Present only when --check-regression is passed.
  "regression": {
    "hard_regressions": [],
    "reliability_regressions": [],
  },
}
```

### Field notes

- `trigger_rate` = `triggers / runs`.
- `all_runs_agree` is `True` when `triggers == runs` (should_trigger case) or
  `triggers == 0` (should_not_trigger case). It is the pass^k-style reliability
  signal, distinct from the blended `trigger_rate`.
- `sibling_fires` maps each `--exclude-skill` token to how many of this case's
  runs also saw that sibling fire. It never affects pass/fail.
- `regression.hard_regressions`: baseline blended pass was True, fresh is
  False. `regression.reliability_regressions`: baseline `all_runs_agree` was
  True, fresh is False. Cases are matched by `query` string, not index.

## Exit codes

| Code | Meaning                                                                                                                              |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `0`  | Ran successfully; no regression check requested, or none detected                                                                    |
| `1`  | `--check-regression` was set and at least one hard or reliability regression was found (the full summary is still printed to stdout) |
| `2`  | Argument / validation error (from `argparse` / `parser.error`)                                                                       |
