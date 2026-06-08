# Drafting the Engineering Content — Section-by-Section Guide

The template at `templates/tech-breakdown.md` enumerates the sections and their subsections — read it directly for the structural prompts. This reference captures the Bitwarden-specific guidance and gotchas the template can't.

Load this reference when actively drafting Specification, Clarifications Log, Plan, Tasks, or Agent Context. The parent SKILL.md keeps the lifecycle spine; this file carries the per-section discipline.

## Specification

- **Don't paste the Product spec.** The breakdown is a technical document; the description is the bridge from Product intent to engineering work. Link the Product feature document, don't reproduce it.
- **If Product intent is ambiguous, surface it to the Clarifications Log** rather than guessing. Ambiguous Product intent is the single biggest source of churn.
- **Specification Alternatives vs Plan Alternatives.** Specification alternatives ask "could we satisfy Product with a smaller change?"; Plan alternatives ask "given we're building this, which designs did we reject for each component?" Don't conflate.

## Clarifications Log

- **Run an AI clarify pass against the draft before requesting cross-team review** (Spec Kit's `/speckit.clarify`, Claude, or equivalent). Decisions from that pass fold back into Specification or Plan; what lands in the log is the residue — questions that needed a human stakeholder.
- **Open clarifications can ship to `Proposed`** as long as each has an owner and a target. **Don't reach `Accepted` with material Open questions** — block or owner-assign first.

## Plan

- **Apply `Skill(architecting-solutions)` (in the `bitwarden-tech-lead` plugin) as the architectural lens** — blast-radius assessment, dual-data-access parity, V±2 client compatibility, multi-client reality.
- **Prefer Mermaid source over image-only diagrams** — AI-readable, diffs cleanly, reviewers can suggest edits in text.
- **Out of Scope vs Known Limitations.** Out of Scope is what this work explicitly does not deliver (use to short-circuit drift). Known Limitations are in-scope-but-deferred constraints inside the work being shipped — name the rationale and the follow-up.
- **Walk each per-layer subsection.** The template enumerates the layers and carries a checklist for each — work through the checklists and either fill in the changes required or state explicitly that the layer isn't touched. Don't leave subsections silently empty; the value is in the follow-ups, not the yes/no.
- **Cryptographic work routes through `Skill(bitwarden-security-context)`** (in the `bitwarden-security-engineer` plugin); `Skill(threat-modeling)` is the source for definition format when existing security definitions are touched.
- **API surface changes apply a V±2 client compatibility lens.** Backwards compatibility isn't optional for self-hosted; phase changes accordingly.

## Tasks

- Tasks are at the implementation-unit level — what becomes Jira stories. **Sequence them by `Blocked on` / `Depends on`** so the team can see the critical path.
- **Don't restate architectural decisions on tasks** — the breakdown is the source for cross-cutting decisions; the task carries a pointer.
- **Jira stories are created at one of two valid timings** depending on how the team refines: at the `In Progress → Proposed` entry (default, for teams whose refinement ritual is ticket-shaped) or deferred to the `Proposed → Accepted` gate (for teams who refine on the breakdown's Tasks section). Either way, by `Accepted` the stories must exist and be bidirectionally linked. Each story mirrors one Tasks row and carries the Ticket Shape (template appendix; full reference in `references/ticket-shape.md`). The choice and its rationale are explained under "Stakeholder-communication checklist (at Proposed entry)" item 3 in the parent SKILL.md.
- Once stories exist, the Tasks section and the Jira stories are a **synchronized pair**: substantive edits mirror on the matching story in the same change; significant edits also get a summary comment on the story for traceability. Detailed field mapping, link-type rules, and sync taxonomy in `references/jira-story-mechanics.md`.
- **Mechanics-level Jira writes are intentionally not in this skill's `allowed-tools`** — delegated to whichever Jira authoring tooling the engineer has available (a `jira-manager` or `jira-cli` skill if installed, direct Atlassian MCP write calls, or the Jira UI).
- **Watch the task count and nudge a split when it grows.** A breakdown's value comes partly from being refinable end-to-end and from supporting a credible release-date estimate when work starts. Both degrade as the task count climbs. Rough thresholds, calibrated to a ~2-week sprint with typical team capacity:
  - **10 or fewer tasks** — healthy. Refinable in one or two sessions; release prediction holds.
  - **more than 10 tasks** — at this size a single breakdown can't be refined in time to start work with a credible release date. Review for natural seams: sequential phases, independently-shippable subsets, interface boundaries. Ask whether one or more subsets could ship as its own breakdown.
  - When a split is being considered or executed, raise it in `Coordination notes` so cross-team reviewers see the scope change; each child breakdown gets its own cross-team signoff cycle.

## Agent Context

The breakdown is self-contained; Agent Context is pointers to existing code and external references that supplement the inline spec — what makes the breakdown useful in future Claude conversations.

- **Repos affected** should pair with a bidirectional `CLAUDE.md` pointer: each repo's `CLAUDE.md` should point agents back to this breakdown.
- **"Things an agent should not assume" is the highest-leverage subsection** for preventing wrong-shaped AI-generated code. Treat empty as a smell — at minimum, list "no surprising assumptions identified" rather than leaving it blank.
