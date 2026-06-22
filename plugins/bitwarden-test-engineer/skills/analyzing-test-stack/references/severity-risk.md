# Severity as a risk weight

The layer model (`test-layers.md`) tells you the _cheapest layer that buys the confidence a
behavior requires_, landed inside the target repo's shape. **Severity tells you how much
confidence is required.** A defect in vault
unlock and a typo on a settings label are not owed the same rigor — severity is the dial
that turns "cheapest sufficient" from a flat rule into a risk-weighted one.

Severity is the **impact of a defect on the system or user**, independent of how urgently
it gets fixed (that is _priority_). This skill weights coverage by severity, not priority.

## Source of truth

The canonical classification is Bitwarden's **Defect Severity Classification Guide**,
Confluence page `2759229512`:
<https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2759229512/Severity>. That page is
authoritative — read it for the level definitions, criteria, and signals; this file does
not reproduce them. When the `bitwarden-atlassian-tools` MCP is available, fetch the page
with `mcp__bitwarden-atlassian__get_confluence_page` (pageId `2759229512`) and classify
each behavior against its criteria. If the fetch fails or the MCP is unavailable, classify
against the generally understood meaning of the levels below using your own judgment, and
note in the report that severities were assessed without the guide (definitions not
verified) — degrade gracefully; never block on it.

The levels, highest to lowest impact, are **Critical**, **High**, **Medium**, **Low**, and
**Informative**. Use these names consistently in the report regardless of source.

**Security-vulnerability defects are the exception:** their severity follows the
_Vulnerability Tracking and Management_ guide, not this one. If a behavior is
security-sensitive (crypto, auth, a threat-model-relevant path), treat its risk as at
least Critical regardless of the level definitions.

## Where each behavior's severity comes from

- **Bug / defect ticket** — read the severity already assigned on the Jira issue (the
  severity field, or the reporter/QA's stated severity in the description/comments). Use it
  directly; if it is absent, classify against the guide's criteria and mark it an assumption.
- **Feature, PR, tech breakdown** — there is no defect yet, so assess each behavior's
  **risk severity**: _if this behavior broke in production, what severity would the
  resulting defect carry?_ Classify it against the same criteria. This is what makes the
  recommendation risk-aware rather than uniform.

## How severity calibrates the recommendation

Severity does **not** mean "push everything Critical to E2E." The cheapest-sufficient rule
still governs _which_ layer; severity governs _how completely_ the behavior must be covered
and _how hard a missing test counts as a gap_. Concretely:

- **Critical** — the confidence bar is highest: cover the behavior's material failure modes,
  not just the happy path, at whatever layer each mode is cheapest to pin down. Critical
  behaviors that are genuine end-to-end journeys (login, vault unlock, checkout) are exactly
  what the **thin E2E layer** is reserved for — the guide's "critical user flows"
  map 1:1 onto that reservation. A Critical behavior with no observed coverage is a
  **top-priority gap** and belongs at the head of `#overview`'s open risks.
- **High** — strong integration coverage of the primary path _and_ the documented
  workaround / affected configuration (the specific client, OS, or auth method that scopes
  the impact). Reach for E2E only when the path is itself a critical journey. An uncovered
  High behavior is a gap that should be scheduled, not silently accepted.
- **Medium** — the plain cheapest-sufficient layer with no escalation. A gap here is worth
  recording and ranking below Critical/High; it is reasonable to defer.
- **Low** — minimal coverage; often a single unit or integration assertion, or an explicit
  "not worth automating" call. Do **not** spend an E2E test on a Low behavior — that is the
  ice-cream-cone anti-pattern wearing a risk costume.
- **Informative** — generally not automatable as a Bitwarden behavior; record as
  out-of-scope rather than as a coverage gap, with a one-line reason.

Two corollaries:

1. **Severity ranks the gaps.** When `#gaps` and `#overview` list open risks, order them by
   severity — the reader should resolve the Critical-uncovered behaviors first. Gap
   prioritization is severity-driven, not list-order-driven.
2. **Severity ≠ priority.** A Low-severity defect can be High-priority before a launch, and
   a High-severity bug in a rarely used admin panel can be Low-priority. This skill weights
   coverage by **severity** (impact). Note priority only if the caller supplied it and it
   changes what to test first.
