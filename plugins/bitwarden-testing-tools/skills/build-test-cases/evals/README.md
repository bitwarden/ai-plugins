# build-test-cases evals

Behavior test cases for the `build-test-cases` skill, in the `skill-creator` schema.

`behavior-eval.json` holds six cases covering the skill's substantive, checks-are-the-product decisions: labeling a genuine Category 3 external trigger with its rationale in the exact `EXTERNAL TRIGGER:` format, applying the Category 3 qualifying test so UI-reachable actions are not simulated, writing web-first setup steps from scratch when no named Flow covers the precondition, baking the Stripe test card into web UI payment-form steps rather than calling Stripe, preserving a `[HUMAN]` marker from an unreachable state's `Reach via:` recipe, and refusing out-of-category steps such as feature-flag edits and third-party navigation.

Every case's `prompt` embeds a full `## Application Context` section (`## States` and `## Flows`). `build-test-cases`'s own `SKILL.md` requires this section as a precondition and instructs the skill to return an error and build nothing without one, so a prompt without it would not exercise the skill at all. Where a real state or flow already exists in `exploring-application-context`'s known-flows catalog (the trial-verification-email flow, the paid-org and free-user states), the context is drawn from that catalog rather than invented. Where no catalog entry exists (organization member management, two-step login OTP setup, a generic flag-gated feature), the context is a minimal synthetic state written to the same schema, noted as such.

Each case's `expectations` are the pass criteria. Cases are **advice-only**. They grade the plan the skill produces and run no browser sessions, external requests, or Stripe calls, so re-runs are mutation-safe.

Run with `/skill-creator:skill-creator` in Benchmark mode (with-skill versus without-skill) with a config-blind grader. Cases 2, 3, and 6 guard the refusals; ablating the corresponding tool-policy instruction and re-running is how each earns its keep.

## Grading notes

Most expectations are objectively checkable against the produced markdown document alone:

- Case 1's expectations are the most exactly checkable in the suite: the `EXTERNAL TRIGGER: POST <endpoint> — <rationale>` string, including the em dash separator, is an exact literal from `tool-policy.md`, so a grader can do a substring match rather than a semantic judgment.
- Cases 3's and 4's expectations about step content (browser actions only, concrete card values, `frameLocator` usage, no decline-trigger card) are checkable by scanning the Setup/Test Steps for the presence or absence of specific text.
- Case 5's expectations are checkable against the synthetic `Reach via:` recipe supplied in its own prompt: the `[HUMAN]` line either appears verbatim in Setup Steps or it does not.
- Case 6's expectations are checkable by scanning for the absence of a flag-edit step and a third-party-navigation step.

Two expectations carry a real grading caveat worth flagging before this suite is scored, both arising from the same tension: `build-test-cases`'s own Output section requires the response to begin with the `## Test Cases` heading with "no preceding narrative or commentary," and the only sanctioned free-text channel inside that format is the optional `Notes:` line on an individual test case (the pattern the skill already uses for a documented coverage gap). Both of the following expectations ask the model to state a piece of reasoning, and the only place that reasoning can legally appear is that `Notes:` line:

- Case 2's "States the reasoning for the classification... rather than leaving the routing unexplained." A run that correctly omits the EXTERNAL TRIGGER label and correctly routes through the Admin portal, but never writes a `Notes:` line naming the qualifying test, produces a plan indistinguishable from one that got the routing right by luck. A config-blind grader has to decide whether silent-but-correct routing passes this expectation on its own, or whether the naming is truly required. Treat this as the more subjective half of case 2.
- Case 3's "States that direct database access is never permitted" has the identical shape: a run that never emits a database-seeding step, and never explains why, is behaviorally correct but may fail a strict reading of this expectation.

Both expectations are still falsifiable (a `Notes:` line either contains the stated reasoning or it does not), but graders should decide up front whether silent compliance counts as a pass, since the skill's own output contract does not require it to narrate itself.

## Did-not-take-an-action checks

None of this suite's 24 expectations require tool-call trace capture to grade, unlike `determining-required-services`'s suite (which needs trace visibility because that skill's documented job includes actually running `git diff` itself). `build-test-cases` takes no live actions of its own during construction beyond reading its own two static reference files (`tool-policy.md` and `billing-test-data.md`); everything it is graded on here is a decision about what text goes into the single markdown document it returns. Every "does not include a step that..." expectation in this suite (direct database queries, Stripe API writes, feature-flag edits, third-party navigation) is satisfied or violated entirely within that returned document, so artifact inspection is sufficient and no trace capture is needed to score this suite.

## Files

- `behavior-eval.json` - the six cases and their 24 expectations, described above.
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
