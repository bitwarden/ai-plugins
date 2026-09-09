# Candidate load-bearing directives: <skill-name>

Working log for the bare-minimum rebuild of `<skill>` (`<path to treatment SKILL.md>`).

## Method

v0 is the control stripped to a step list plus an output template. It trusts the model's baseline competence. Each directive below was load-bearing in the original and was deliberately withheld from v0. Add a directive back only when a run reproduces the failure mode it prevents, so it proves it earned its tokens.

Status values: `withheld` (not in v0), `added` (restored to the treatment), `dropped` (runs show it is not needed).

## Version ledger (treatment `version:` field)

One bump per applied change-set (a testable skill state). Separate from the plugin's semver.

- v0.1 (<date>) initial bare rebuild: step list + output template, everything withheld.
- v0.2 (<date>) <what changed>.

## Directive table

| #   | Directive (terse form) | Source file | Failure mode to watch for          | Status   | Observed? (date + notes) |
| --- | ---------------------- | ----------- | ---------------------------------- | -------- | ------------------------ |
| 1   | <terse directive>      | <source>    | <specific bad outcome it prevents> | withheld |                          |
| 2   | <terse directive>      | <source>    | <specific bad outcome it prevents> | withheld |                          |

## Experiment log

Record each run: input used, isolation method, the decisive fact verified (and against what), and any directive promoted from `withheld` to `added` with its justification. Note the model and treatment version. Counts go in the skill's `evals/behavior-baseline.json`, not here.

### Run 1 - <input>, <date>

**Method:** two separate top-level sessions, one per variant, same input. Taint check: <CLEAN/TAINTED + evidence>.

**Decisive fact (verified):** <fact> - against <live source + ref>.

**Result:**

- **treatment (v<X.Y>, <model>):** <what it produced; correct or wrong on the decisive fact; notable strengths/weaknesses>.
- **control (<model>):** <same>.

**Takeaways:**

- <what this run is evidence for or against>.
- <any directive promoted withheld -> added, and why>.

**Attribution:** <skill / model / run noise / run structure - and how you ruled the others out>.
