---
name: running-a-proof-of-concept
description: Phase 3 (Proof of Concept) deep-dive playbook — validates the Research recommendation in real Bitwarden code and drafts the ADR.
when_to_use: Use when Research has produced an approved recommendation and the shepherd is validating it in real code before Scoping. Triggers — "PoC time", "building the PoC", "drafting the ADR". Not for the High-Level Architecture Plan (use `scoping-and-handing-off-to-teams`) or cross-team coordination (use `coordinating-implementation-across-teams`).
allowed-tools: Skill, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_remote_links, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_issues, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence_cql
---

Phase 3 (Proof of Concept) deep-dive playbook for an initiative shepherd. Deliverables: one or more PRs that demonstrate the recommended pattern in real Bitwarden code, Architecture Council review, and a draft ADR in the centralized [contributing-docs](https://github.com/bitwarden/contributing-docs) repository (not per-repo). Time budget: 2–4 weeks, 40–80 hours of shepherd time. PoCs that stretch past 4 weeks usually signal either the wrong scope (too ambitious) or the wrong approach (the recommendation isn't working).

## What the PoC Is For

Three things, in order:

1. **Prove the approach works in Bitwarden's real codebase** — not in a sandbox, not on a clean repo, not in a hypothetical. Production-quality code on a representative slice.
2. **Surface the friction the assessment couldn't predict.** Every approach looks good on paper. The PoC is where you discover that the chosen pattern needs a TypeScript interface refinement, or that the test infrastructure can't represent the new boundary, or that the receiving team's existing telemetry breaks under the new structure.
3. **Give the receiving teams something concrete to react to.** A PoC PR is a far better basis for handoff than an architecture doc alone. Teams orient on code faster than on prose.

If the PoC doesn't accomplish all three, the next phase will pay for it.

## Selecting the PoC Area

This is the highest-leverage decision in the phase. The funnel doc's guidance: representative but contained, ideally ~1–5 files or one module that demonstrates the key patterns.

How to choose:

- **Pick an area that exercises the parts of the approach most likely to fail.** If the approach is async error handling, pick a service with non-trivial async paths. If it's a new state-management library, pick a feature with real state transitions.
- **Avoid the simplest possible case.** A PoC on a trivial slice proves nothing the assessment didn't already claim.
- **Avoid the worst possible case.** A PoC on the most pathological module of the codebase will fail for reasons that have nothing to do with the approach. You'll learn something, but not what you needed to learn.
- **Coordinate with the owning team's tech lead.** Their input on the right slice is usually decisive. They know which area is illustrative and which is a tarpit. They also know which area their team has spare capacity to host the PoC PR review on.

Once selected, identify a **point-of-contact on the owning team** (usually a senior engineer, sometimes the tech lead) who will pair with you or review your work. They are not adopting the work — they are your partner in surfacing where it doesn't fit.

This is also a good moment to consult `Skill(architecting-solutions)` in `bitwarden-tech-lead` for the team-scope architectural constraints that will shape your PoC (security mindset, multi-client reality, V+/-2 compatibility, etc.). The PoC ships against those constraints from the start, not retrofitted.

## Building the PoC

### Framework / Foundation

If the approach requires shared scaffolding — middleware, base classes, type definitions, shared libraries — build it first. This is the reusable piece that broader rollout depends on. The framework itself is part of what the PoC is validating.

Two principles:

- **Production-quality.** Cut corners on scope, not on quality. The funnel doc is explicit: "don't cut corners — this tests whether the approach actually works." Corner-cut PoCs answer the question "could this work if everything were perfect?" — not the question you actually need to answer.
- **Match existing patterns where they exist.** New code that ignores established Bitwarden conventions will fail review for reasons that obscure whether the approach itself worked. Read first. Build alongside, not in opposition to, what's already there.

### Example Implementation(s)

Implement 1–3 examples demonstrating the new pattern in the chosen area. Each example should be self-contained enough that a reviewer can see the pattern in action, but realistic enough that it tests real-world complexity. Examples from the funnel doc: migrate one API endpoint, one UI component, or one service module.

For each example, capture:

- **What worked.** The cases where the pattern fits cleanly.
- **What challenges emerged.** Edge cases, integration friction, places where the framework had to be adjusted, things that surprised you.
- **What would need to change for full rollout.** Sometimes the PoC reveals that the framework needs refactoring before scale-out; sometimes it reveals that the rollout itself needs phasing.

### The PR(s)

- Mark "PoC" in the title if not intended for merge — the funnel doc allows either, but be explicit about intent.
- In the PR description, write the three points above (what worked, what challenges, what would change). The PR description is the most-read artifact of the PoC; teams will read it months after the PoC PR was opened.
- Link to the Architectural Assessment so reviewers have context for why the pattern looks the way it does.

## Architecture Council Walkthrough

The funnel doc strongly recommends presenting the PoC to [Architecture Council](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/751698031) at this phase. Format:

- 15–30 minute walkthrough of the PoC findings.
- Add to an upcoming Council agenda — work with the Council facilitator on timing.
- Bring: the PoC PR(s), the assessment summary, your honest read on what worked and what didn't, your proposed direction (proceed / revise / return to Research / decline).
- Optional: have the owning team's point-of-contact attend. Their on-the-ground perspective often carries weight the shepherd's framing can't.

What the Council provides: pattern-level guidance, cross-initiative awareness (is this approach in conflict with something else underway?), validation of the proposed direction, and surface concerns about rollout.

What the Council does not provide: a green light independent of engineering leadership's go/no-go at the end of the phase. The Council recommends; leadership decides.

## Drafting the ADR

If the PoC validates the approach, draft an Architecture Decision Record following the [Bitwarden ADR template](https://contributing.bitwarden.com/architecture/adr/). ADRs live in the centralized [`bitwarden/contributing-docs`](https://github.com/bitwarden/contributing-docs) repository under `docs/architecture/adr/` (rendered at `contributing.bitwarden.com/architecture/adr/`). There is no per-repo ADR directory — Bitwarden's architectural decisions are intentionally centralized so they're discoverable across all codebases the decision touches.

Open a PR against `contributing-docs` with the new ADR file, numbered sequentially after the latest accepted ADR. Example for reference: [`0020-observability-with-opentelemetry.md`](https://github.com/bitwarden/contributing-docs/blob/main/docs/architecture/adr/0020-observability-with-opentelemetry.md).

The ADR is **not** the architecture plan — that comes in Scoping. The ADR is the decision artifact. Sections per the template:

- **Context and problem statement.** A self-contained summary; don't assume the reader has the assessment open.
- **Decision (chosen solution).** Specific. Name the pattern, library, or approach.
- **Alternatives considered.** From the assessment's 2–4 options. Brief — full trade-offs are in the assessment.
- **Rationale for decision.** Tie to the PoC findings, not just the assessment.
- **Consequences (positive and negative).** What changes for the codebase, the teams, operations, security posture. Negative consequences belong here — the ADR is honest, not promotional.
- **Status: Proposed.** It moves to "Accepted" during Phase 4 once leadership has committed.

The ADR is the durable artifact that survives the shepherd's departure. Six months from now, someone will hit a related decision and read this ADR to understand why the codebase is shaped the way it is. Write for that reader.

## Establishing Documentation Patterns

The ADR captures the _decision_. The PoC is also the moment to establish the _functional_ documentation that the new pattern needs to be discoverable and usable by the teams who will adopt it during Phase 5. Per [Documentation Patterns](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/1774977070), Bitwarden splits documentation into two homes that you should land in deliberately:

- **Close-to-code (functional, _what_).** Lives alongside the code in the repository. GitHub renders these `README.md` files automatically when engineers navigate, which is the discovery path that actually works. Use [Mermaid](https://github.blog/developer-skills/github/include-diagrams-markdown-files-mermaid/) for diagrams so they render in-place.
- **Centralized (logistical and architectural, _how_ and _why_).** Lives in the [`bitwarden/contributing-docs`](https://github.com/bitwarden/contributing-docs) repository, rendered at [contributing.bitwarden.com](https://contributing.bitwarden.com/). ADRs, setup guides, feature-flag operating procedures, and cross-cutting architectural references go here.

What the PoC should ship in each home:

- **Alongside the framework code, a `README.md`** explaining what the framework is, its interface, how to extend or apply it, and what trade-offs were deliberately made. Reference the ADR for the decision rationale. Examples to model on: [EventIntegrations](https://github.com/bitwarden/server/blob/main/src/Core/Dirt/EventIntegrations/README.md), [DbSeederUtility](https://github.com/bitwarden/server/blob/main/util/DbSeederUtility/README.md), [EmergencyAccess](https://github.com/bitwarden/server/blob/main/src/Core/Auth/Services/EmergencyAccess/readme.md).
- **Near the example implementation(s), short folder-level notes** that link out to the framework README and the ADR. Even thin folder docs help future engineers find their way to the canonical context.
- **The ADR itself in `contributing-docs`** as covered above.
- **Tech-stack-appropriate inline docs.** XML comments or JSDoc for TypeScript/Angular/.NET; `rustdoc` and crate/module-level `README` for Rust. The Documentation Patterns page has the per-stack rubric.
- **CLAUDE.md updates where the PoC introduces a new pattern.** If the new pattern is one engineers (and Claude tooling) need to follow going forward, add it to the root or folder-area `CLAUDE.md` — link the `README.md` via `@` syntax and the ADR by URL. The `bitwarden-init` and `claude-config-validator` plugins help bootstrap and review these.

The shape of the documentation matters because the PoC is what the receiving teams in Phase 4 will react to. A PoC PR + a framework `README` + an ADR is far more legible than a PoC PR alone — and the difference shows up as faster handoff meetings and less "wait, what was the intended pattern here?" during Implementation.

## Updates to the BW Initiative

During PoC (see [Idea-Based Initiatives](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2785181779)):

- **Links / description:** Add "Relates to" links to the PoC PR(s) (or reference them in the description if they don't have separate Jira tickets).
- **Comments:** Record Architecture Council feedback, PoC findings (what worked, what didn't, what changed from the assessment), and the ADR decision. The Council session itself usually generates several comment-worthy moments.
- **Description:** If the PoC revealed a significant shift from the assessment, update the description to reflect current direction. The description always represents the initiative's current state, not its history.
- **ARCH idea status:** Update to "3️⃣ Proof of Concept".

## Exit Criteria

Per the funnel doc:

- **Deliverables:** One or more PRs demonstrating the solution (even if not merged); Architecture Council review completed; ADR drafted (if proceeding); the team point-of-contact supportive of the approach.
- **Decision maker:** Engineering leadership with Architecture Council recommendation.
- **Possible decisions:** Proceed to Scoping / Revise PoC (pivot to an alternative from the assessment) / Return to Research / Decline.

For the leadership review, bring:

- A 5–10 minute summary of the PoC outcome.
- The clear ask — usually "approval to move to Scoping with X teams over Y timeframe."
- Honest acknowledgment of any concerns surfaced by the Council or the point-of-contact.

## Common Mistakes

- **Cutting corners on PoC quality.** Then later wondering why the framework breaks at scale. The funnel doc is unambiguous: production-quality.
- **Picking a PoC area too small to be representative.** "Look, it works on this one trivial case" doesn't survive contact with the next team's reality.
- **Picking a PoC area inside a team whose tech lead wasn't consulted.** The PoC is also a relationship — make sure the team is willing to host it.
- **Treating the ADR as paperwork.** It's the durable decision artifact. Worth the hour.
- **Skipping Architecture Council to save time.** The Council's cross-initiative awareness is the cheapest way to catch conflicts that would be expensive to resolve later.
- **Quietly walking away from the assessment recommendation during PoC.** If the PoC suggests a different direction, surface it explicitly — don't ship a PoC that mismatches the assessment without naming why.

## Reference

- [Software Initiative Funnel](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/584515614) §3 — canonical phase description, examples of effective vs. ineffective PoCs.
- [Bitwarden ADR template](https://contributing.bitwarden.com/architecture/adr/) — canonical ADR structure, served from the centralized [`bitwarden/contributing-docs`](https://github.com/bitwarden/contributing-docs) repository.
- [Documentation Patterns](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/1774977070) — canonical guidance on close-to-code vs. centralized documentation, tech-stack-specific best practices, and CLAUDE.md conventions.
- [Idea-Based Initiatives](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2785181779) — how to update the BW Initiative during PoC.
- Related: `Skill(shepherding-an-initiative)` for the umbrella playbook, `Skill(running-an-architectural-assessment)` for the upstream Research-phase work the PoC validates, `Skill(scoping-and-handing-off-to-teams)` for what the PoC feeds into, `Skill(architecting-solutions)` (in `bitwarden-tech-lead`) for team-scope architectural constraints that shape PoC design.
