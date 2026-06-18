# Severity as a risk weight

The layer model (`testing-trophy.md`) tells you the _cheapest layer that buys the confidence a
behavior requires_, landed inside the target repo's shape. **Severity tells you how much
confidence is required.** A defect in vault
unlock and a typo on a settings label are not owed the same rigor — severity is the dial
that turns "cheapest sufficient" from a flat rule into a risk-weighted one.

Severity is the **impact of a defect on the system or user**, independent of how urgently
it gets fixed (that is _priority_). This skill weights coverage by severity, not priority.

## Source of truth

The canonical classification is Bitwarden's [**Defect Severity Classification Guide**](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2759229512/Severity),
Confluence page `2759229512`. The levels
and criteria below mirror that page so the analysis degrades gracefully when the
`bitwarden-atlassian-tools` MCP is unavailable — but the page is authoritative. When the
`bitwarden-atlassian-tools` MCP is available, fetch it with `mcp__bitwarden-atlassian__get_confluence_page` (pageId
`2759229512`) to pick up revisions before relying on the cached copy here. If the fetch
fails or the MCP is unavailable, use the mirrored table below and note in the report that
the severity definitions are from the cached copy (version not re-verified) — degrade
gracefully; never block on it.

**Security-vulnerability defects are the exception:** their severity follows the
_Vulnerability Tracking and Management_ guide, not this one. If a behavior is
security-sensitive (crypto, auth, a threat-model-relevant path), treat its risk as at
least Critical regardless of the table below.

## Where each behavior's severity comes from

- **Bug / defect ticket** — read the severity already assigned on the Jira issue (the
  severity field, or the reporter/QA's stated severity in the description/comments). Use it
  directly; if it is absent, classify against the criteria below and mark it an assumption.
- **Feature, PR, tech breakdown** — there is no defect yet, so assess each behavior's
  **risk severity**: _if this behavior broke in production, what severity would the
  resulting defect carry?_ Classify it against the same criteria. This is what makes the
  recommendation risk-aware rather than uniform.

## Levels and criteria (mirrored from the guide)

| Severity        | A defect here would…                                                                                                                     | Signals (from the guide)                                                                                                                                               |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Critical**    | Severely harm core functionality, data integrity, or security with no viable workaround                                                  | Blocks a critical flow (login, vault access, billing, account creation); data loss/corruption/exposure; crash/unrecoverable state; affects all or a broad user segment |
| **High**        | Significantly degrade a core feature/flow, but a workaround exists (difficult or non-obvious), or impact is limited to a subset of users | Core feature impaired but not blocked; specific client/OS/auth method; burdensome/undiscoverable workaround; compounding friction in a core workflow                   |
| **Medium**      | Degrade functionality or UX meaningfully, but a workaround exists or scope is limited                                                    | Non-critical / secondary flow broken; misleading-but-not-destructive output; degraded experience for a subset; extra steps to work around                              |
| **Low**         | Have minimal functional impact; does not meaningfully hinder the user                                                                    | Cosmetic / typo / visual only; negligible edge case; minor UX inconsistency; trivial workaround                                                                        |
| **Informative** | Be a known limitation, third-party compatibility issue, or environmental quirk — not a defect in Bitwarden's core behavior               | Autofill on a non-standard third-party site/app; no clear owner or fix path; unlikely to be actioned                                                                   |

## How severity calibrates the recommendation

Severity does **not** mean "push everything Critical to E2E." The cheapest-sufficient rule
still governs _which_ layer; severity governs _how completely_ the behavior must be covered
and _how hard a missing test counts as a gap_. Concretely:

- **Critical** — the confidence bar is highest: cover the behavior's material failure modes,
  not just the happy path, at whatever layer each mode is cheapest to pin down. Critical
  behaviors that are genuine end-to-end journeys (login, vault unlock, checkout) are exactly
  what the trophy reserves the **thin E2E layer** for — the guide's "critical user flows"
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
