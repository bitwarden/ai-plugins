---
name: scoping-and-handing-off-to-teams
description: Phase 4 (Scoping & Commitment) deep-dive playbook — High-Level Architecture Plan, child epics, per-team handoffs, leadership go/no-go.
when_to_use: Use when an initiative has cleared PoC and the shepherd is scoping the work, drafting the architecture plan, handing off to teams, and seeking leadership commitment. Triggers — "handoff meeting", "drafting the architecture plan", "writing child epics", "go/no-go". Not for Phase 5 coordination (use `coordinating-implementation-across-teams`).
allowed-tools: Skill, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_remote_links, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_issues, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence_cql
---

Phase 4 (Scoping & Commitment) deep-dive playbook for an initiative shepherd — the final decision gate before significant resource allocation. The shepherd transitions from leading the work to supporting the teams that will execute it. Deliverables: the High-Level Architecture Plan, child epics, per-team handoff meetings, cost-benefit analysis, leadership go/no-go presentation, operational prioritization, capacity allocation, and the finalized ADR. Time budget: 2–4 weeks, 30–50 hours of shepherd time. Composes `Skill(running-work-transitions)` in `bitwarden-delivery-tools` for the originating-side Preparation and Transition Sessions phases of the [Work Transition Playbook](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2521038855).

## The Anti-Pattern to Reject First

Before anything else: **the team owns the breakdown — not the shepherd.** The single biggest failure mode at this phase is the shepherd writing the team's stories.

The funnel doc is unambiguous: "After the handoff, run a team breakdown session. The team creates the stories — not the shepherd." Stories the team didn't write are stories the team won't own. Once that happens, downstream failure shows up as "we're behind schedule because the stories don't match how the team actually works" and there's no clean recovery.

Hold the line. Your job is to give each team enough context, scope, and pattern to break the work down well — not to break it down for them.

## What You Produce

Phase 4 produces eight artifacts, in roughly this order: the High-Level Architecture Plan, child epics in Jira, the per-team handoff meetings, a cost/benefit analysis, the assigned initiative priority, the leadership presentation for go/no-go, operational prioritization with capacity allocation, and the finalized ADR. Each follows below as its own section.

## The High-Level Architecture Plan

A Confluence page placed under the EN-space architecture-planning folder, following the "High-Level Architecture Planning" template. The funnel doc specifies its content:

- **Scope.** What will be changed — repositories, modules, files. Be specific. Vague scope at this stage means re-scoping during Implementation.
- **Approach.** How the change rolls out. Phasing, migration path, what happens to the old pattern during and after the migration.
- **Team alignment.** Which teams own which portions. One team per epic when possible.
- **Dependencies.** What must happen first. What can happen in parallel. Where teams will block each other.
- **Risk mitigation.** Failure modes, rollback plan, what indicators trigger a pause/pivot.
- **Success metrics.** How you will know the initiative succeeded. Define these now — they become the basis for the impact measurement 3–6 months after Implementation completes.
- **Documentation needs.** What must be created or updated as the rollout progresses (technical guide, migration guide, ADR updates, contributing-guide changes, runbooks).

The architecture plan is the document each team's tech lead reads before the handoff meeting. Write it for that reader.

## Child Epics in Jira

Create epics under the BW initiative — typically one per team or major module. Each epic carries:

- **Summary.** Short and concrete (e.g., "Migrate Browser Extension to New Error Pattern").
- **Team assignment.** Assign to the team, not an individual.
- **Description.** What area of the codebase is affected; what pattern is being adopted (link to PoC PR); expected outcomes for this epic; success criteria; cross-team dependencies the team needs to know about.
- **Label / component** for filtering (e.g., `initiative-typescript-migration`). This is how everyone's dashboard rolls up progress later.

Example epic shape from the funnel doc:

> **Epic:** Migrate Browser Extension to New Error Pattern
> **Team:** Browser Extension Team
> **Description:**
>
> - Adopt error middleware pattern proven in PoC (PR #1234)
> - Apply to background scripts, content scripts, and popup
> - Must maintain existing error reporting to Sentry
> - **Success:** All extension error handling follows new pattern, zero regressions

What does not go in the epic: the implementing stories. Those come from the team's own breakdown session.

## Per-Team Handoff Meetings

Schedule one handoff meeting per team, 1 hour each. Per the funnel doc, the structure is:

| Time   | What                                                                     |
| ------ | ------------------------------------------------------------------------ |
| 20 min | Shepherd presents: PoC findings, architecture plan section for this team |
| 15 min | Q&A — team asks clarifying questions about approach                      |
| 15 min | Team discusses: initial thoughts on breakdown approach                   |
| 10 min | Next steps — team commits to completing breakdown by a specific date     |

This is also Phase 2 of the Work Transition Playbook from the originating side. The funnel doc references the playbook explicitly; both perspectives apply.

Before the meeting:

- Send the architecture plan and the PoC PR link a few business days in advance. Teams that read materials in advance bring sharper questions.
- Confirm the team's tech lead and EM will attend.

In the meeting:

- Lead with the why (the problem and the PoC findings) before the what (the architecture plan section). Teams react better to context than to specification.
- Take questions seriously, especially the ones that surface roadmap conflict. The handoff is the right venue for those — Implementation is the wrong one.
- Don't leave without a commit-to-date for the breakdown. "We'll get to it" is how epics decay in backlogs.

After the meeting:

- The team runs its own breakdown session (you are not present).
- The team's tech lead shares the completed breakdown with you.
- You **review for consistency** with the initiative's vision — not to rewrite stories or micromanage. The funnel doc names the question pattern: "this looks good but uses callbacks instead of the async/await pattern from the PoC — was that intentional?"

## Cost/Benefit Analysis

Document in the architecture plan. The funnel doc's framing:

- **Cost:** General size of the effort across teams (sum of team estimates, plus your shepherd time and Architecture Council time).
- **Benefits:**
  - **Quantitative:** bugs reduced, time saved, performance improved, on-call pages reduced.
  - **Qualitative:** developer experience, maintainability, consistency, security posture, future flexibility.
- **Comparison.** Honest. If qualitative benefits dominate, say so — leadership can weigh that. Pretending you have a quantitative case when you don't damages the next initiative's credibility.

## Initiative Priority

Per the funnel doc, work with engineering leadership to set priority against other initiatives and the [Architecture / Engineering Operating Model](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/1286963201) portfolio:

- **Critical:** Blocks major product work or creates significant risk — start immediately.
- **High:** Substantial quality-of-life improvement or risk reduction — schedule within quarter.
- **Medium:** Meaningful improvement, can be scheduled flexibly — within 2 quarters.
- **Low:** Nice to have, will do when capacity allows — opportunistic scheduling.

Update the priority on the BW initiative in Jira.

## Leadership Presentation

Present the plan to engineering leadership at a stakeholder sync. Per the funnel doc, include:

- Problem recap and solution approach.
- PoC validation results.
- Effort estimates and timeline (from team breakdowns — aggregated).
- Cost/benefit analysis.
- Risk assessment.
- Initiative priority.
- Resource ask — which teams, how much capacity, over what timeframe.

Seek an **explicit go/no-go decision**. Executive commitment means: "Yes, we're allocating resources to complete this initiative."

## Operational Prioritization

This is the step the funnel doc explicitly distinguishes from executive commitment. Executive commitment says "yes, eventually." Operational prioritization says "starting on these dates with this much capacity."

Coordinate with engineering leadership:

- **Target start date.** Based on initiative priority and other team commitments.
- **Quarter(s) of execution.**
- **Relative priority of each epic** against the team's other work (product roadmap features, other initiatives, bugs, tech debt).

Engineering leadership works with team leads and EMs to:

- Communicate the initiative's importance and timeline.
- Allocate capacity (e.g., "15% of sprint capacity for next 3 sprints").
- Adjust team roadmaps.
- Resolve conflicts if teams are over-committed.
- Place epics in team backlogs with appropriate priority.

Outputs from this step (per the funnel doc):

- A clear timeline (e.g., "Implementation begins Q2 2026, expected completion Q3 2026").
- Each involved team aware they need to allocate capacity.
- Epic priority set in Jira for each team's backlog.
- Teams acknowledge the work is in their roadmap.

The funnel doc names this failure mode explicitly: an initiative with executive commitment but no operational prioritization stalls in backlogs indefinitely. Do not advance to Implementation without operational prioritization.

## Finalize the ADR

- Update ADR status to "Accepted" if not already.
- Add the implementation timeline and final scope.
- Include start date and expected completion date.

## Updates to the BW Initiative

During Scoping (see [Idea-Based Initiatives](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2785181779)):

- **Priority field:** Set to the final priority assigned by leadership.
- **Child epics:** Create as Jira children of the initiative, one per team or module.
- **Comments:** Document executive commitment — who approved, what capacity was allocated, what timeline was agreed. This is an auditable record of the commitment.
- **Description:** Link the High-Level Architecture Plan in the description or via a comment.
- **ARCH idea status:** Update to "4️⃣ Scoping & Commitment".

## Exit Criteria

Per the funnel doc:

- **Deliverables:** High-Level Architecture Plan; epics created with clear scope and approach; teams have completed story breakdown and estimation; team estimates aggregated into overall timeline and effort; initiative priority assigned; cost/benefit analysis completed; executive commitment secured; **epics prioritized in team backlogs with clear timeline and capacity allocation**.
- **Decision maker:** VP of Engineering / CTO with stakeholder sync agreement.
- **Possible decisions:** Proceed to Implementation / Rescope (smaller scope, re-estimate) / Defer (timing conflict, schedule for future quarter) / Decline.

The five key success factors the funnel doc names:

1. Engineering leadership must explicitly say "yes, we're doing this."
2. Teams must have capacity allocated with clear start/end dates.
3. Timeline must be realistic given capacity and dependencies.
4. Epics must be prioritized in team backlogs so teams know when to pull stories into sprints.
5. Teams must own their story breakdown.

## What This Phase Hands to Phase 5

When you move into Implementation (via `Skill(coordinating-implementation-across-teams)`), the support-period phase of the Work Transition Playbook begins. The originating-side guidance — what to use you for and what not to use you for — is in `Skill(running-work-transitions)`. Read it before Implementation kicks off; it's the same playbook the receiving teams are reading.

## Common Mistakes

- **Writing the team's stories.** Already named; named again because it's the failure mode.
- **Treating executive commitment as the end of Scoping.** Without operational prioritization, executive commitment is theoretical.
- **Accepting handoff meetings that get cut short.** The handoff is the venue for the uncomfortable questions. Shorter than 1 hour means something didn't get said.
- **Padding the cost/benefit case.** Engineering leadership will catch it, and the next initiative will pay for the credibility loss.
- **Skipping the architecture plan's "documentation needs" section.** Then documentation gets written at the end, when patterns have already drifted.
- **Aggregating team estimates without team buy-in.** If a team didn't believe its estimate when it gave it, it won't deliver to it either.

## Reference

- [Software Initiative Funnel](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/584515614) §4 — canonical phase description, handoff meeting structure, operational prioritization.
- [Work Transition Playbook](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2521038855) — canonical handoff process; this phase is the originating side of Phases 1–2.
- [Idea-Based Initiatives](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2785181779) — how to update the BW Initiative through Scoping.
- [Architecture / Engineering Operating Model](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/1286963201) — how the initiative portfolio gets prioritized against other Architecture work.
- Related: `Skill(shepherding-an-initiative)` for the umbrella playbook; `Skill(running-work-transitions)` (in `bitwarden-delivery-tools`) for the originating-side handoff mechanics; `Skill(coordinating-implementation-across-teams)` for what Scoping feeds into.
