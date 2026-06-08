# The Three Bitwarden-Adopted Collaboration Models

Load this reference when reading the deep-dive on each model. The parent SKILL.md keeps the workflow steps (Step 1 escape hatches, Step 3 inputs, Step 4 matching logic); this file carries the per-model mechanic, change-shape fit, and Bitwarden examples.

The three models are drawn from Pete Hodgson's [cross-team collaboration patterns](https://blog.thepete.net/blog/2021/06/17/patterns-of-cross-team-collaboration/). Trusted Outsider and Tour of Duty are intentionally omitted — they didn't reflect how Bitwarden teams actually work.

## File a Ticket

**Mechanic:** Driving team raises a request; **the owning team takes the work into their own domain.** If the change warrants a tech breakdown, the owning team writes it (often as a sibling breakdown linked from the driving team's signoff table). The owning team creates their own epic and stories on their board. The driving team specifies the contract they need (inputs, outputs, behavior) but not the internal implementation; their post-filing involvement is clarifying intent, reviewing the design, and signing off on the approach.

**What this implies for the driving team:** File a Ticket is **not** a low-cost option for the driving team's roadmap. It transfers planning and execution load to the owning team, who must absorb it into their sprint, their breakdown queue, and their metrics. Confirm the owning team can absorb it before defaulting to File a Ticket.

**File a Ticket is not "file and forget."** The ticket lands on the owning team's backlog, but it needs collaboration to get scheduled and to land correctly. The driving team stays engaged on alignment, refinement, clarifying intent during design, and reviewing the implementation when it lands. If the driving team disappears after filing, the work tends to stall or land off-target.

**Change shape this fits:**

- The change requires domain knowledge the driving team doesn't have.
- The change touches the owning team's internal architecture, not just its API surface.
- The change has compounding risk if done wrong (security primitives, data integrity, cryptography).
- The change is touching another team's core domain invariants — the change is deep enough that the owning team's mental model needs to absorb it; new architectural decisions, contract changes, security primitives.
- The change alters the mental model that the owning team has of their code.
- The change impacts areas in the owning team's domain that are under active development (open PRs, open breakdowns) — multiple changes in the same files from multiple teams will result in coordination friction.

**Bitwarden examples:**

- Mobile UI parity for a new feature — owned by Mobile (different stack, native expertise required).
- Modifications to authentication or session-management primitives — owned by Auth.
- Cryptographic implementation work — owned by KM.
- Database schema migrations on shared, high-traffic tables — owned by the data-owning team.
- Refactoring the internal architecture of a shared service — owned by the service team.
- Changes to the event-bus mechanism itself (not just adding a topic to it).

**Common shape:** "Change how it works internally" rather than "use it in a new way." If the change requires the owning team to reason about their domain invariants, they should hold the pen.

## Internal Open-Source

**Mechanic:** Driving team writes the change and opens a PR; owning team reviews and merges as maintainers. Work appears on the driving team's roadmap and metrics; the owning team's involvement is design review on the API and merge gatekeeping.

**Change shape this fits:**

- The change extends an existing pattern the owning team has documented.
- Codebase conventions are mature enough that an outside PR can land cleanly.
- The driving team has bandwidth and enough familiarity with the codebase to write a passable PR.

**Bitwarden examples:**

- Adding a new component to a shared component library, following the library's conventions.
- Adding a new endpoint to an existing API where similar endpoints already exist.
- Registering a new event topic on an event bus where topic-registration is a documented pattern.
- Extending a public type or interface with a new optional field.

**Common shape:** "Build on top of" or "add another instance of" — the owning team has anticipated this kind of extension, and the conventions are stable enough that the change can land without owning-team domain reasoning. The owning team's value-add is design review on the API, not writing the boilerplate.

## Embedded Expert

**Mechanic:** An engineer from the owning team embeds with the driving team for a defined period, working inside the driving team's codebase as a paired contributor through design, implementation, review, and (often) post-launch hardening.

**This is a rare model.** It's the heaviest pattern in the catalog and the only one where the owning team commits an engineer to the driving team's codebase rather than the other way around. **Two conditions must both hold** before recommending it:

1. **The owning team has explicitly agreed to commit bench capacity for the embed.** Embedded Expert is not a model the driving team can pick unilaterally — it's a real engineer-week commitment from the owning team. If they haven't volunteered or confirmed, route through Step 1's escape hatch instead (request them as reviewers) and let them counter-propose Embedded Expert if they want it.
2. **The driving team's success genuinely depends on owning-team presence inside the codebase, not just guidance.** Examples: a security-critical first integration where the owning team wants to be in the build (and has volunteered for it), a launch window where a one-time design review isn't enough, a foundational early integration where the owning team wants real-consumer feedback during the build. "We want their expertise" alone isn't enough — most "want their expertise" cases are satisfied by a one-time bounded design or threat-model review (the Step 1 escape hatch), not by an embed.

**Bitwarden examples (rare):**

- KM bench-commits an engineer to embed with a feature team during a security-critical first integration of a new cryptographic primitive, riding through design, review, and one sprint post-launch. KM proposes the embed; the feature team doesn't pre-assume it.
- Platform bench-commits an engineer to embed with a feature team for the first consumer adoption of a major new SDK, specifically to feed real-consumer learnings back into the SDK's API during the integration.

**Common shape:** "The owning team is sending an engineer." If that sentence isn't already true when the model is being proposed, the right answer is the escape hatch (request them as reviewers), not Embedded Expert.
