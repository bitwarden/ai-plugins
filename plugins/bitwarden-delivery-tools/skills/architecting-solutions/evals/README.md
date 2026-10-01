# architecting-solutions evals

Behavior test cases for the `architecting-solutions` skill, in the `skill-creator` schema.

`behavior-eval.json` holds ten cases targeting the Bitwarden-specific parts of the skill.

Each case's `expectations` are the pass criteria. Denominators differ per case because they count expectations, not runs — every expectation is graded independently for both configurations.

Cases are **advice-only** — they grade the design the skill produces and run no live edits, commits, or PRs, so re-runs are mutation-safe.

Any change to `SKILL.md` should be paired with a re-run and a refresh of `behavior-baseline.json`; the baseline is what future comparisons diff against.

## How to run

Numbers are only comparable when the harness matches, so reproduce this one rather than improvising:

- **Both arms** run `claude -p --model opus --strict-mcp-config` from an empty working directory, so no repo `CLAUDE.md`, `.claude/`, or sibling skill leaks into either.
- **With-skill** adds `--plugin-dir <path to bitwarden-delivery-tools>` and prefixes the case prompt with `Use the architecting-solutions skill to answer this.` The direction is deliberate: this measures what the skill does to the output, not whether it self-triggers. Without it the skill often never fires and both arms collapse to the same configuration. Triggering is a separate concern with its own eval type.
- **Baseline** gets no plugin and no prefix.
- Capture `--output-format stream-json`. Several expectations are about what the responder _did_ (fetching the ADR index before recommending), which the final answer does not necessarily mention, so the grader needs the tool trace as well as the text.
- **Grade config-blind.** Shuffle the 20 outputs behind opaque ids before grading, and run the grader as a separate `claude -p --allowedTools ""` process so it cannot look up which arm produced what. Keep the id-to-arm mapping out of the grader's input.

Sanity-check before trusting a run: every with-skill trace should open with `Skill bitwarden-delivery-tools:architecting-solutions`, and no baseline trace should mention it.

`behavior-baseline.json` records the pass/fail rate per case, keyed by model + effort. Diff only within a key — a different model or a different harness is a different series, not a regression. Regression check:

```bash
diff <(jq -S . behavior-baseline.json) <(jq -S . result.json)
```

An empty diff means no regression. When a change is intentional and the new numbers are the new desired state, replace `behavior-baseline.json` with the new results in the same PR as the skill change.
