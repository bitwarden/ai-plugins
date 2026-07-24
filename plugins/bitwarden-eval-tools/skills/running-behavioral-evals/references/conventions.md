# Conventions: directory layout, naming, and formats

These keep an experiment legible to someone who did not run it, and runs comparable across days and models.

## Experiment directory

One directory, under `docs/` in the repo, not a plugin data directory that subject runs might read.

```
docs/<skill-name>-eval/
  SESSION-STATE.md       # what is tested, current state, findings, open items
  directive-ledger.md    # version ledger + directive table + per-run entries
  run-prompts.md         # the exact blinded prompts, one block per variant
  results/               # quarantined artifacts, off-limits to subject runs
    <input>/
      <input>__<variant>__<model>__<timestamp>-coverage.md
      <input>__<variant>__<model>__<timestamp>-execution-log.md
```

Re-read `SESSION-STATE.md` first when resuming. Keep it short and current: goal, frozen control, current treatment version, the thesis and whether it holds, open items. Full detail lives in `directive-ledger.md`.

## Run artifact naming

Two files per run, identical but for the suffix:

```
<input>__<variant>__<model>__<timestamp>-coverage.md
<input>__<variant>__<model>__<timestamp>-execution-log.md
```

- **input**: short slug (`pm-40636`, `billing-csv`).
- **variant**: the treatment carries its version (`min-v0.9`); a frozen control does not (`rich`), since it never changes.
- **model**: `opus`, `sonnet`. Record it rather than reconstructing it later.
- **timestamp**: `HHMMSS`, enough to order runs and separate same-input runs.

Double underscores keep the slug parseable when a field contains a hyphen.

Rename the `-coverage.md` suffix to fit your skill's output. One file for the product, one for the log.

## Verifying labels

Do not trust the session label to tell you which variant produced a file. Plugin-install differences (marketplace versus local) have swapped output directories relative to the session that wrote them. Confirm each file's variant from its own execution log's `Skill(...)` invocation before grading. Part of the taint check, not optional.

## The version ledger

One line per version at the top of `directive-ledger.md`, one bump per applied change-set. This is the treatment's experiment version, kept in its SKILL.md `version:` frontmatter, separate from the plugin's semver.

```
- v0.1 (07-22) initial bare rebuild: step list + output template, everything withheld.
- v0.2 (07-22) added directives #13/#14/#15 as step-level instructions.
- v0.3 (07-23) rewrote #15 into an inspection escalation ladder.
```

One bump per testable state ties any artifact to the exact skill text that produced it.

## The directive table

One row per candidate directive:

```
| # | Directive (terse form) | Source file | Failure mode to watch for | Status | Observed? (date + notes) |
```

- **Failure mode**: the specific bad outcome it prevents. If you cannot name one, the directive is a candidate to drop.
- **Status**: `withheld`, `added`, or `dropped` (see `ablation-accretion.md`).
- **Observed?**: the run and date where that failure actually appeared. This column is the evidence for an `added`.

## The rubric: `behavior-eval.json`

The expectations live with the skill under test, in its `evals/behavior-eval.json`, committed alongside it. Same shape the other behavior suites in this marketplace use:

```json
{
  "skill_name": "assessing-test-coverage",
  "eval_type": "behavior",
  "purpose": "What these cases cover and why each one earns its place.",
  "evals": [
    {
      "id": 1,
      "name": "reverted-coverage-not-claimed",
      "prompt": "The task, with any given state inline.",
      "expected_output": "Prose description of the correct outcome.",
      "expectations": [
        "Does not claim coverage for tests reverted off the default branch",
        "Cites a permalink at the commit it actually read"
      ]
    }
  ]
}
```

`expectations` is the rubric. Each entry is one objectively checkable claim, graded pass or fail with no partial credit. Give every case a `name`; the baseline keys on it.

Prefer advice-only cases, where the state is supplied in the prompt and the graded artifact is the stated plan. Re-runs then perform no writes and need no credentials.

## The report card: `behavior-baseline.json`

Sits next to the rubric and is refreshed on every run. Results key on `<model>/<effort>`, because a comparison across different models or effort levels is not a comparison:

```json
{
  "grader_model": "claude-opus-5",
  "denominator": "expectations x runs_per_arm",
  "per_expectation": "passes per expectation, in behavior-eval.json order, out of runs_per_arm",
  "claude-sonnet-5/default": {
    "reverted-coverage-not-claimed": {
      "runs_per_arm": 4,
      "new-skill": "16/16",
      "old-skill": "12/16",
      "no-skill": "12/16",
      "new-skill-per-expectation": "4/4/4/4",
      "old-skill-per-expectation": "0/4/4/4",
      "no-skill-per-expectation": "0/4/4/4"
    }
  }
}
```

Use the arm names the marketplace's other behavior suites already use: `new-skill` is the treatment, `old-skill` is the frozen control, `no-skill` is the same prompt with no skill loaded at all.

Run the `no-skill` arm. Without it you learn which variant is better and not whether either one earns its tokens, and a case where all three arms score the same is a case that is not measuring the skill.

Record `runs_per_arm` honestly, and keep the per-expectation breakdown. An aggregate that holds while one expectation collapses from `4/4` to `0/4` is the regression you most want to see, and the aggregate hides it.

A regression is a per-expectation count falling for the same case, same arm, same `<model>/<effort>` key. A difference against a different key is not a regression; it is an unmeasured configuration.

## Per-run log entries

Under the table, one entry per run: input, isolation method, the decisive fact you verified and against what, and any directive promoted with its justification. Numbers live in `behavior-baseline.json`; this log holds the narrative. Note the model and treatment version so the entry survives the skill moving on.

## Environment gotcha: CLAUDE_PLUGIN_DATA

`${CLAUDE_PLUGIN_DATA}` does not reliably expand inside a skill's Bash or Write steps; it has been inert across models, falling back every run. Resolve the experiment directory to an explicit project-relative path instead, so runs land where you expect and quarantine stays predictable.
