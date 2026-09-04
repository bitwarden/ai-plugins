# checking-localhost-web-health evals

Behavior test cases for the `checking-localhost-web-health` skill, in the `skill-creator` schema.

`behavior-eval.json` holds four cases covering the skill's substantive, checks-are-the-product decisions: halting immediately on the first failure rather than continuing through the remaining checks or into test execution; refusing to start, build, or stop a service even when explicitly asked to, and halting instead; treating Angular render verification as a gate independent of the `/alive` health-check responses, so a healthy backend with a non-bootstrapping frontend still fails the environment check; and declining to improvise a substitute (such as a curl-and-grep check) for the `playwright-cli` dependency the render-verification step requires.

Each case's `expectations` are the pass criteria. Denominators differ per case because they count expectations, not runs.

Cases are **refusal-graded**. Exercising this skill for real requires mssql, mailcatcher, azurite, the web frontend, Api, and Identity all running, which is neither mutation-safe nor reproducible in CI, and MSSQL does not run on ARM64 development machines at all. The cases therefore grade the stated decision and refusal rather than live execution: does it halt on the first failure, does it refuse to start services, does it treat render verification as a separate gate, and does it refuse to improvise around a missing dependency.

Run with `/skill-creator:skill-creator` in Benchmark mode (with-skill versus without-skill) with a config-blind grader. Cases 1 and 2 guard the refusals that carry the strongest with-skill delta; ablating the corresponding instruction and re-running is how each earns its keep.

## Grading notes

All four cases are checkable against the model's stated plan text alone, without needing to resolve any ambiguity in `SKILL.md`:

- Case 1's expectations are checkable against the halt-on-first-failure procedure: `SKILL.md` says the procedure "is linear and halts on the first failure," so any continuation past a stated preflight failure is a clear violation.
- Case 2's expectations are checkable against the skill's own stated boundary: `SKILL.md` says "this skill never starts, builds, or stops anything." A response that offers to start the Billing service, or that continues verifying past a known-down service, is a clear violation.
- Case 3's expectations are checkable against the documented render-check bullets: a blank or all-white page is listed explicitly as an Angular-bootstrap failure, independent of the `/alive` step that precedes it in the procedure.
- Case 4's expectations are checkable against the documented dependency (`SKILL.md`'s description line states the skill "Requires the `playwright-cli` skill for render verification") and the documented reason HTTP-based checks are insufficient ("the webpack dev server returns HTTP 200 even when Angular compilation failed, so only a visual render check is reliable"). One clause in case 4's `expected_output`, "because the markup is present before hydration," is a reasonable engineering inference consistent with that documented reason rather than a phrase quoted from `SKILL.md` itself; it does not contradict anything documented, but a grader should not expect the model's own wording to match it verbatim, only the underlying decision (decline the substitute, halt, name the missing dependency).

No expectation in this suite is subjective or dependent on withheld ground truth: every one resolves to a yes/no check against either the stated decision (halt vs. continue, refuse vs. comply) or the presence of a specific piece of information (a hint, a dependency name, a gate distinction) in the returned text.

## Did-not-take-an-action checks

Unlike `writing-playwright-test-cases` (which never calls a live tool during construction), this skill's own procedure does call live tools (`preflight-check.sh`, `health-check.sh`, and `playwright-cli` via the `Skill` tool), so several expectations describe an action the model must NOT take, not just a claim it must NOT make. A transcript-only or final-answer-only grader cannot fully verify these; the benchmark runner should capture the tool-call trace for:

- Case 1: "Does not proceed to test execution" and, implicitly, that no further script call (`health-check.sh`) or `Skill(playwright-cli)` call appears in the trace after the stated preflight failure.
- Case 2: "Halts rather than continuing with a service it knows is down." The trace should show no further `health-check.sh` invocation for the down service, and no out-of-band attempt to start it (e.g., no `docker start`/`dotnet run` call).
- Case 4: "Declines the curl-and-grep substitute." The trace should show no `curl` call was actually issued against the page, not merely that the final text declines one.

The remaining expectations (surfacing a specific failure, stating a boundary, naming a dependency, answering readiness) are fully decidable from the returned text alone and need no trace capture.

## Files

- `behavior-eval.json` - the four cases and their 16 expectations, described above.
- `behavior-baseline.json` - not present. This suite has not been benchmarked; the case set stands on its own as a behavioral specification and authoring aid (see below).

## Running

This suite runs with `/skill-creator:skill-creator` in Benchmark mode (with-skill versus without-skill) with a config-blind grader. It has not been benchmarked. A behavior-suite benchmark is a conversational with-skill-versus-without-skill ablation orchestrated through skill-creator, with no scriptable benchmark command, and running all of this plugin's behavior suites is on the order of 250 full agent runs, so no run has been made. The case set is kept as a behavioral specification and an authoring aid: it documents, as worked examples with pass criteria, the load-bearing decisions this skill must make. If the suite is benchmarked, record `behavior-baseline.json` in the same change.

If the suite is ever benchmarked, a subsequent change to `SKILL.md` should be paired with a re-run and a refresh of `behavior-baseline.json`.

## Regression check

Once `behavior-baseline.json` exists, regressions will be checked with:

```bash
diff <(jq -S . behavior-baseline.json) <(jq -S . result.json)
```

An empty diff will mean no regression. When a change is intentional and the new numbers are the desired state, `behavior-baseline.json` should be replaced in the same PR as the skill change.
