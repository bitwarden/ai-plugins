# Session State - <skill-name> behavioral eval

Recall/handoff doc. Refreshed <date>. If resuming: read this, then `directive-ledger.md` for the full log.

## The experiment

- **Goal:** <what you are testing. e.g. rebuild the rich <skill> as a bare-minimum <skill>-min, re-adding directives only when a run demonstrates the failure they prevent (evidence-driven accretion). Target: treatment output >= control.>
- **Control (frozen baseline):** `<path to control skill>`. Never edit it.
- **Treatment (under test):** `<path to treatment skill>`. Currently at **v<X.Y>** (`version:` field in its SKILL.md frontmatter).
- **Method per run:** run the variants against the same input in separate, blind top-level sessions; quarantine the artifacts into `results/<input>/` before comparing; adjudicate decisive facts against the live system, not against a single control run.

## Current state

- Treatment is at **v<X.Y>**.
- Thesis: <the claim you are evaluating, and whether it currently holds>.
- Recommended variant so far: <variant + model, or "undecided">.

## Noise floor

- Control-vs-control on <input>, same model, two runs: <N of M per-item verdicts flipped>. Treat any single-run difference smaller than this as not-yet-signal.

## Locations & naming

- Experiment folder: `docs/<skill-name>-eval/` - this file, `directive-ledger.md`, `run-prompts.md`, `results/`.
- Rubric: `<skill>/evals/behavior-eval.json`. Report card: `<skill>/evals/behavior-baseline.json`, keyed `<model>/<effort>`, refreshed every run.
- Run artifacts: `results/<input>/<input>__<variant>[-version]__<model>__<timestamp>-{product,execution-log}.md`.
- **Standing rule:** when a run completes and you begin comparing, MOVE its artifacts into `results/<input>/` (blind protection). Confirm each file's variant from its own execution log's `Skill(...)` call, not from the session label.

## Verified ground truth

- <decisive fact> - verified against <live source + commit/ref> on <date>.

## Open items

- <pending run, unresolved disagreement, or staged-but-not-added directive>

## Working preferences

- Blind eval discipline; never prime a subject. Control is a frozen baseline, not an oracle.
- Verify against files/repos; do not compare from memory.
- Change one variable per comparison (skill vs model vs run structure).
