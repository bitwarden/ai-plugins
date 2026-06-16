# Adversarial checklist — rejection criteria

Run every check against each per-platform recommendation and against the overall shape.
A check "fails" only when you can state a concrete, evidence-backed objection. Record the
evidence; an objection you can't ground is itself rejected.

## Shape-level checks

1. **Ice-cream cone (too E2E-heavy).** Is confidence concentrated in slow, flaky E2E tests
   that integration or unit tests could buy more cheaply? Any behavior recommended for E2E
   that is not a genuinely critical, full-system user journey is suspect — demand the
   justification and propose the lower layer.

2. **Missing platform layer.** Does an affected platform have a gap in its trophy — e.g.
   server logic with no integration layer, a client with only E2E and no component/unit
   coverage, core logic with nothing at all? A whole missing layer is a major finding.

3. **Inverted cost/confidence.** Is core branching logic pushed up to integration/E2E
   while trivial glue sits at lower layers? Confidence should sit at the cheapest
   sufficient layer.

## Row-level checks (per behavior → layer assignment)

4. **Unit masquerading as integration (and vice-versa).** Is something labeled
   "integration" actually a unit test with everything mocked (re-asserting mocks, not real
   collaboration)? Or a true cross-collaborator behavior mislabeled "unit"? Mislabeling
   distorts the shape and the confidence claim.

5. **Over-testing trivial code.** Tests recommended for getters/setters, framework glue,
   generated code, or invariants the type system/analyzer already guarantees. Cost without
   confidence — recommend dropping or moving to static.

6. **E2E for branch coverage.** Edge cases or error paths assigned to slow full-system
   tests when they belong at unit/integration. E2E is for journeys, not branches.

7. **Flaky-E2E candidate.** Does a recommended E2E test depend on timing, external
   services, animation, network, or shared mutable state likely to make it flaky? Flag the
   flakiness risk and whether an integration test with a controlled boundary would be more
   reliable.

## Grounding checks

8. **Coverage claimed without evidence.** Any "already tested" / "existing coverage"
   assertion not backed by an observed test, diff hunk, or CSV row. Especially: **E2E
   coverage asserted without inspecting the dedicated private `test` repo** — that repo is
   not inside the platform repos, so unexamined E2E claims are unverified by definition.

9. **Untestable / ambiguous requirement.** A behavior recommended for testing whose
   acceptance criteria are too vague to write a deterministic assertion against. The fix is
   to flag the requirement gap upstream, not to write a test against a guess.

10. **Assumption presented as fact.** Inferred platform, stack, tooling, or scope stated
    without an "assumption" marker. Demand it be labeled so the reader can weigh it.

## Verdict mapping

- **Endorse** — no failing checks, or only cosmetic notes.
- **Revise** — one or more fixable row-level findings, shape essentially sound.
- **Reject-with-reasons** — a shape-level failure (ice-cream cone, missing layer, inverted
  cost/confidence) or pervasive ungrounded coverage claims. State what a correct
  recommendation would require.
