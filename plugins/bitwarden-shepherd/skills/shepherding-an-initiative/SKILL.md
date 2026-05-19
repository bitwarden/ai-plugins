---
name: shepherding-an-initiative
description: Five-phase umbrella playbook for an initiative shepherd. Dispatches to phase-deep skills (Research, PoC, Scoping, Implementation) at the right moment.
when_to_use: Use when an approved ARCH idea enters the Software Initiative Funnel, or when choosing which phase deep-dive applies. Triggers — "ARCH-X just got approved", "I'm assigned shepherd", "what phase am I in". Not for pre-funnel championing (use `championing-a-strategy-idea`).
allowed-tools: Skill, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_remote_links, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_issues, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence_cql
---

End-to-end umbrella playbook for an initiative shepherd, covering all five phases of the [Software Initiative Funnel](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/584515614): Identification → Research → Proof of Concept → Scoping & Commitment → Implementation. Maps each phase's effort, deliverables, and decision gate; holds the line on what the shepherd produces vs. what gets handed to teams. Fetch the canonical funnel page via `get_confluence_page` when entry/exit criteria or full template detail is needed.

## The Rule of Ownership (Hold Throughout)

**You own the initiative. Each receiving team owns how it executes its part.**

Every phase has a single sentence to remember: when you start writing the team's stories, the team won't own the work. When you stop coordinating across teams, the initiative drifts. Both failures are yours to prevent.

For the agent-neutral, team-side view of the same boundary (the version tech leads read), invoke `Skill(navigating-the-initiative-funnel)` in `bitwarden-delivery-tools`. Reading both perspectives keeps you honest about where the line actually sits.

## Time and Effort Expectations

The funnel page sets these benchmarks. They're not aspirational — they're the basis for capacity planning when leadership asks "what does it cost to shepherd this?"

| Phase                    | Duration   | Shepherd Effort   | Decision Maker                        |
| ------------------------ | ---------- | ----------------- | ------------------------------------- |
| 1 — Identification       | ~1 week    | 4–8 hours         | Holistic engineering leadership       |
| 2 — Research             | 3–5 weeks  | 40–80 hours       | Eng leadership + Architecture Council |
| 3 — Proof of Concept     | 2–4 weeks  | 40–80 hours       | Eng leadership + Architecture Council |
| 4 — Scoping & Commitment | 2–4 weeks  | 30–50 hours       | Engineering leadership (Director+)    |
| 5 — Implementation       | 2–6 months | 10–20 hours/month | Teams execute; shepherd coordinates   |

Total: 150–300 hours of shepherd time over 4–9 months for a medium initiative — roughly 5–10% of one person's time with higher concentration in Research and PoC.

## Phase-by-Phase: What the Shepherd Does

### Phase 1 — Identification

**Purpose:** Capture enough context for meaningful evaluation without premature commitment of resources.

**You produce:**

- A BW Initiative issue under the Bitwarden Company (BW) project. Type: Initiative. Assignee: you (the proposed shepherd). Reporter: whoever surfaced the problem. Priority: a placeholder ("TBD - Awaiting Research" or Medium).
- A description distilled from the upstream ARCH idea (if one exists) into an executive-readable summary — not a copy of the full TSI template. Pattern, link inventory, and field-by-field guidance live in [Idea-Based Initiatives](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2785181779).
- A **work item link** from the ARCH idea (in Jira Product Discovery) to the BW initiative. This is the foundational traceability link — every idea-based initiative must have one.
- Initial "Relates to" links: prior attempts, adjacent SRE/BRE/TSD/PM tickets, anything the ARCH idea's own research surfaced.
- An ARCH idea status update to "1️⃣ Identification" in JPD.

**Decision gate:** Holistic engineering leadership decides Proceed / Hold / Decline.

**What you do NOT do:** Pre-scope the solution. Research hasn't happened yet. Resist the urge to come in with an answer.

### Phase 2 — Research

**Purpose:** Deeply understand the problem space and explore potential solutions before committing to direction.

**You produce:**

- 3–5 stakeholder interviews (the affected teams' tech leads are likely subjects).
- A current-state analysis surveying existing implementations across the codebase — inconsistencies, workarounds, technical debt — with impact quantified where possible.
- 2–4 documented solution approaches with explicit trade-offs.
- An **Architectural Assessment** in Confluence under the EN-space assessments folder, refined through stakeholder review.
- Optional preview at Architecture Council for major initiatives.
- ARCH idea status updated to "2️⃣ Research".

**Decision gate:** Engineering leadership with Architecture Council input. Proceed to PoC / Continue Research / Hold / Decline.

**Deep skill:** `Skill(running-an-architectural-assessment)` for stakeholder interview structure, current-state analysis, options generation, and the Architectural Assessment template.

### Phase 3 — Proof of Concept

**Purpose:** Validate the recommended solution works in practice within Bitwarden's codebase before committing to full implementation. Reduce risk through hands-on experimentation.

**You produce:**

- A PoC area chosen in coordination with the owning team's tech lead — representative but contained (~1–5 files or one module).
- The framework or foundation that broader rollout will reuse, plus 1–3 production-quality example implementations.
- One or more PRs (may or may not be merged; mark "PoC" in title if not).
- An Architecture Council walkthrough — 15–30 minutes, with the PoC PR, the findings (what worked, what didn't, what would need to change), and the proposed direction.
- A **draft ADR** (status: Proposed) following the [Bitwarden ADR template](https://contributing.bitwarden.com/architecture/adr/). ADRs live in the centralized [`bitwarden/contributing-docs`](https://github.com/bitwarden/contributing-docs) repository under `docs/architecture/adr/` — there is no per-repo ADR directory.
- **Close-to-code documentation** for the framework and example implementations (per [Documentation Patterns](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/1774977070)) — a `README.md` alongside the framework code, folder-level notes near examples, and CLAUDE.md updates where new patterns are introduced. The deep skill covers what each home (close-to-code vs. centralized `contributing-docs`) is for.
- ARCH idea status updated to "3️⃣ Proof of Concept".

**Decision gate:** Engineering leadership with Architecture Council recommendation. Proceed to Scoping / Revise PoC / Return to Research / Decline.

**Deep skill:** `Skill(running-a-proof-of-concept)` for PoC area selection, building the framework, Architecture Council prep, and ADR drafting.

### Phase 4 — Scoping & Commitment

**Purpose:** Transform a validated PoC into a concrete implementation plan with effort estimates, team assignments, and executive commitment.

**You produce:**

- A **High-Level Architecture Plan** in Confluence under the EN-space planning folder: scope, approach (phasing, migration path), team alignment, dependencies, risk mitigation, success metrics, documentation plan.
- Child epics under the BW initiative — typically one per team or major module. Each epic carries its area of the codebase, the PoC PR reference, expected outcomes, and success criteria.
- A scheduled **handoff meeting** with each receiving team (1 hour per team, structured 20/15/15/10): 20 min present, 15 min Q&A, 15 min team's initial breakdown thinking, 10 min commit to a breakdown date.
- A cost/benefit analysis documented in the architecture plan.
- An initiative priority (Critical / High / Medium / Low) updated on the BW initiative.
- A leadership presentation seeking explicit go/no-go with capacity commitment.
- **Operational prioritization** with engineering leadership: target start date, quarter, relative priority against teams' other commitments, sprint capacity allocation.
- A finalized ADR (status: Accepted) with timeline.
- ARCH idea status updated to "4️⃣ Scoping & Commitment".

**Decision gate:** VP of Engineering / CTO. Proceed to Implementation / Rescope / Defer / Decline.

**Critical anti-pattern:** You writing the team's stories. The team does the breakdown — not you. You review breakdowns for consistency with the initiative's vision, not to rewrite stories.

**Deep skill:** `Skill(scoping-and-handing-off-to-teams)`. The Phase 4→5 handoff is a work transition from the originating side; that skill composes `Skill(running-work-transitions)` from `bitwarden-delivery-tools` for the transition mechanics.

### Phase 5 — Implementation

**Purpose:** Execute across teams. You coordinate, support, and maintain consistency — you do not implement.

**You produce / maintain:**

- Communication channels: optional `#initiative-<name>` Slack channel with pinned PoC PR / ADR / architecture plan / Jira dashboard; bi-weekly tech-leads sync (30–45 min); optional office hours; monthly stakeholder-sync update.
- A kickoff meeting with all teams (1 hour) recapping problem, solution, PoC results, dependencies, communication channels.
- Approach support — answering questions in Slack, jumping on Meets when text isn't enough, clarifying edge cases not covered in PoC.
- **Review-for-consistency** on early PRs from each team — not detailed code review. The team's PR review still happens inside the team.
- Cross-team consistency: early drift detection, judgment on legitimate variation vs. drift that undermines consistency, an FAQ that captures recurring questions and solutions.
- Weekly progress tracking (dashboard + Slack channel), bi-weekly tech-leads sync, monthly leadership update.
- Documentation produced progressively (drafted at 40% complete, finalized at 90%): technical guide, migration guide, ADR final updates, contributing-guide updates, runbooks as relevant.
- Knowledge transfer — a tech talk or brown bag in the final weeks (45–60 min).
- A **retrospective** within 2 weeks of completion (shepherd + tech leads from all affected teams, 1.5 hours).
- An impact measurement 3–6 months later against the success metrics defined in Scoping.
- ARCH idea status updated to "5️⃣ Implementation", then to its final status at completion.

**Deep skill:** `Skill(coordinating-implementation-across-teams)`. For the Phase 4→5 transition's later stages (Phases 3–6 of the Work Transition Playbook on the originating side — pulse check at ~30 days, retrospective at ~90 days, closure), that skill composes `Skill(running-work-transitions)` from `bitwarden-delivery-tools`.

## Cross-Cutting Practices

These apply across phases:

- **Keep the ARCH idea status synchronized.** The funnel-phase status (1️⃣–5️⃣) is how Architecture and engineering leadership see your initiative in JPD views. Updating only the BW initiative goes stale at the portfolio level.
- **Link aggressively on the BW initiative.** "Relates to" SRE/BRE/PM tickets, prior-attempt tickets, adjacent initiatives, operational tickets that emerge. The link inventory is one of the most valuable artifacts you maintain.
- **Use Jira comments as a timeline.** Significant decisions, stakeholder feedback, mid-course corrections, cross-team dependency resolutions — these belong in initiative comments. They become invaluable at retrospective and for future shepherds facing similar work.
- **Update the initiative description as the approach evolves.** It's a living summary, not a research document. Detailed research belongs in the Architectural Assessment, implementation details in epics and stories, decision rationale in the ADR.

## When the Initiative Is Smaller Than the Funnel Was Designed For

The funnel is built for initiatives that genuinely span multiple teams. For an initiative that lives largely in one team's domain or one adjacent team, a tech lead may shepherd directly via `bitwarden-tech-lead` rather than this plugin. If you're operating as the shepherd for a small-scope initiative, run a compressed version: lighter Architectural Assessment, smaller PoC, single handoff meeting, less formal cross-team coordination during Implementation. The phases still apply; the artifacts get smaller.

The minimum invariant regardless of scope: a documented problem, a documented decision, capacity explicitly committed before Implementation starts, and a retrospective at the end.

## Common Mistakes

- **Skipping straight to PoC because the solution feels obvious.** The Architectural Assessment is where the team's expertise gets surfaced and friction gets named. Skipping it produces solutions that stall at adoption.
- **Writing the team's stories during Scoping.** Faster in the moment, but the team won't own work it didn't author. Insist on the handoff and the team breakdown.
- **Phase 5 without operational prioritization.** Executive commitment ("yes, do this") is necessary but not sufficient. Without a target quarter, a capacity allocation, and a place in team backlogs with relative priority, epics sit.
- **Reviewing every PR.** You are not the team's reviewer. Review early PRs for approach alignment; trust the team for code quality.
- **Letting the ARCH idea status go stale.** The portfolio view depends on it. Update it at every phase transition.
- **Skipping the retrospective.** It's the only mechanism that improves the funnel itself. Every initiative's lessons either feed back or get re-learned.

## Reference

- [Software Initiative Funnel](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/584515614) — canonical phase-by-phase document. Fetch via `get_confluence_page` when the full template, the entry/exit criteria, or the example timeline table is needed.
- [Idea-Based Initiatives](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2785181779) — canonical BW Initiative anatomy, description template, link conventions, phase-by-phase initiative evolution.
- [Work Transition Playbook](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2521038855) — canonical six-phase transition reference; the Phase 4→5 handoff is a transition from the originating side.
- [Architecture / Engineering Operating Model](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/1286963201) — how Architecture's initiative portfolio gets communicated (Architecture Initiative Review, Architecture/Platform sync).
- Related: `Skill(running-an-architectural-assessment)`, `Skill(running-a-proof-of-concept)`, `Skill(scoping-and-handing-off-to-teams)`, `Skill(coordinating-implementation-across-teams)`, `Skill(curating-the-strategy-ideas-backlog)`; from `bitwarden-delivery-tools`: `Skill(navigating-the-initiative-funnel)`, `Skill(running-work-transitions)`.
