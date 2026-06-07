---
name: contributing-to-technical-strategy
description: How team-level patterns flow up into Bitwarden's Technical Strategy Ideas backlog and back down through BW Initiatives into team epics and stories. Covers recognizing which team-level patterns belong in the TSI backlog, framing an idea well enough for Architecture to evaluate it, the ARCH idea ↔ BW Initiative linkage, and defining epic-level and story-level work downward from an initiative. Use when noticing a cross-team pattern of pain that exceeds one team's scope, when surfacing ideas to the architecture group, when understanding how an initiative connects back to its originating idea, or when breaking epic-level work out of an initiative onto a team.
allowed-tools: Skill, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_remote_links, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_issues, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence_cql
---

Bitwarden's technical strategy has a vertical shape: ideas live at the top, initiatives in the middle, and team-level epics and stories at the bottom. The tech lead is the role that spans the vertical — noticing the patterns at the bottom that belong at the top, and translating the work at the top back down into stories the team ships.

This skill covers that full vertical:

- Recognizing an idea worth capturing.
- Framing it well enough for Architecture to evaluate.
- Understanding how an approved idea becomes a BW Initiative.
- Defining epic-level and story-level work downward from an initiative.

The canonical references are [Technical Strategy Ideas](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2344517656) and [Idea-Based Initiatives](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2785181779). Fetch them via `get_confluence_page` when the full templates or the complete field definitions are needed.

## The Top of the Funnel: Technical Strategy Ideas

Technical Strategy Ideas (TSIs) are Bitwarden's **idea backlog** — the curated collection of technical improvement opportunities that Architecture maintains in Jira Product Discovery under the `ARCH` project. Ideas get RICE-scored, categorized by theme, and placed on a Now / Next / Later roadmap. The ones that get prioritized enter the Software Initiative Funnel at Identification.

### Recognizing an Idea Worth Capturing

Create a TSI when these patterns appear:

- **A pattern of pain across multiple teams.** Five teams are each solving the same error-handling problem differently. That's not five team-level problems; it's one cross-team idea.
- **An architectural gap or tech debt with broad impact.** The debt exists in shared code, or its absence is blocking other teams.
- **An opportunity to improve developer experience or operational reliability** at a level that a single team can't own.
- **A technology trend Bitwarden should evaluate** — not "we should use GraphQL because it's modern," but "REST's round-trip cost is quantifiable here and here, and the alternatives warrant evaluation."
- **A security improvement that spans multiple systems.**

Stay in-team (and create nothing) when:

- The problem is contained to a single team's codebase and that team can solve it in normal work.
- The problem is urgent and requires immediate action — those bypass this process; talk to leadership directly.
- It's a product-driven feature request — that belongs in product backlogs, not TSIs.

Staff+ engineers are the primary contributors to TSIs, but tech leads absolutely can and should contribute ideas sourced from their teams' experience. The patterns surfacing across sprints are signal Architecture often doesn't have direct access to.

### Framing an Idea Well

A TSI doesn't require a full architectural proposal. It does require enough context for Architecture to evaluate whether it's worth research. The TSI template has several sections — the ones that matter most:

- **Problem / Opportunity Statement.** Be specific about the current state, the pain points, and the opportunity if solved. "Error handling is inconsistent" is vague; "Five different error handling patterns exist across clients, causing debugging difficulty and user confusion" is actionable. Quantify where possible — "~3 bugs per quarter tied to this" or "~4 hours per sprint lost to this" makes impact concrete.
- **Strategic Alignment.** Which OKRs, strategic themes, or architectural principles does this support? What other initiatives does it depend on or enable?
- **Target Audience / Stakeholders.** Teams, users, or systems that benefit; others affected; teams with expertise to consult.
- **Stakeholder & Engagement Map.** This is where ideas frequently stall if done poorly. Identify decision makers by name or role (not just team names), must-consult stakeholders, must-inform stakeholders, and — this is the uncomfortable one — **known friction points**: where will disagreement or resistance come from, and why? Naming friction upfront is how good ideas avoid becoming technically sound proposals that stall at adoption. Ideas that acknowledge friction earn more trust than ones that present only the upside.
- **Proposed Direction.** High-level only — don't design the solution. That's for funnel research. Rough conceptual approach, technologies worth considering, build/buy/integrate thinking.
- **Operational & Quality Considerations.** Key metrics or SLIs, performance constraints, testability implications, self-hosted vs. cloud implications, compliance touchpoints (SOC 2, ISO 27001).
- **Validation Approach.** What a minimal proof of concept would look like; what signals would indicate this is worth pursuing; what assumptions need testing.
- **Rough Sizing.** T-shirt size, expected duration, complexity factors.
- **RICE score** for prioritization, plus customer segments and theme.

Not every field needs to be filled perfectly on first write. The Stakeholder & Engagement Map, in particular, is completed collaboratively between the primary owner and a peer reviewer before an idea moves from Backlog to Research. When an idea is filed from a team, the architecture group will pair the filer with a reviewer — that's how the map gets sharpened.

### What Happens After Filing

Architecture triages new ideas weekly, updates RICE scores monthly, manages the backlog mid-quarter, and runs a quarterly prioritization review with engineering leadership. Ideas approved for pursuit transition into the Software Initiative Funnel at the Identification phase.

Ideas that aren't pursued move to Declined — with the rationale recorded. All declined ideas remain visible for institutional memory, so the same idea doesn't get re-evaluated without context.

## The Middle of the Funnel: From Idea to Initiative

When an ARCH idea is approved for the funnel, a separate artifact is created: a **BW Initiative** issue in Jira's Bitwarden Company project. These are two different records for two different purposes (see [Idea-Based Initiatives](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2785181779)):

- The **ARCH idea** stays in Jira Product Discovery. It continues to carry RICE, theme, roadmap placement, the full TSI template, and — critically — the funnel-phase status (1️⃣ Identification through 5️⃣ Implementation).
- The **BW Initiative** is the execution-level record. Strategic summary, shepherd as assignee, child epics for each team, issue links to related work across projects, Jira comments documenting decisions and coordination events.

They're linked by a **work item link**: the BW initiative "implements" the ARCH idea. That link is what lets someone in JPD trace to execution status, and someone in Jira trace back to strategic rationale.

A tech lead usually won't create the BW Initiative — that's the shepherd's job during Identification. But initiatives get **read** often: when one shows up affecting the team, when trying to understand why a shepherd is proposing a specific approach, when checking for related work in adjacent teams. A well-linked initiative answers three questions at a glance:

1. **Where did this come from?** The ARCH idea link carries the strategic rationale.
2. **What work is being done?** The child epics show current execution across teams.
3. **What else is related?** "Relates to" links capture prior attempts, dependencies, operational tickets, cross-project coordination.

When receiving an epic from an initiative, take five minutes to read the parent BW Initiative and follow the link up to the ARCH idea. The context is almost always worth the time.

## The Bottom of the Funnel: Connecting the Trace to Team Work

This is where tech-lead-specific work lives. During Scoping & Commitment, the shepherd creates child epics under the BW Initiative — typically one per team or major module. The team's epic is then theirs to break down.

The mechanics of that breakdown — story-quality rules, what to include, what to avoid, how to share it back to the shepherd — live in `Skill(navigating-the-initiative-funnel)`. That skill is the canonical home for breakdown practice. What matters here, in this skill, is the **traceability** that keeps the breakdown connected upward to the originating idea:

- Before running the team's breakdown session, follow the link inventory up: read the BW Initiative's description, then follow the work-item link to the ARCH idea. The TSI carries the strategic rationale, stakeholder map, and known friction points — all of which should inform how the team interprets the epic. Five minutes of reading here saves hours of mis-scoped stories later.
- When a breakdown surfaces ambiguities that weren't in the TSI or initiative description, two options: the ambiguity is inside the team's scope (decide and move), or it has cross-team implications (push it to the shepherd with enough context to resolve it without starting over). The "Stakeholder & Engagement Map" section of the TSI usually tells which one is in play.
- When the team hits a friction point during implementation that was predicted in the TSI's "Known Friction Points" section, surface it to the shepherd with that reference. It's a signal the friction showed up where expected — not a new problem, but a planned one that needs active navigation.

### Keeping the Trace Alive

As work progresses, link aggressively on the BW Initiative:

- **"Relates to"** the SRE/BRE/TSD/PM tickets that touch this work.
- **Prior-attempt tickets** discovered during implementation.
- **Adjacent initiatives** that interact with this one.
- **Operational tickets** that emerge during rollout.

The initiative's link inventory is one of the most valuable things it provides — it's the complete picture of work associated with the effort across all projects. When in doubt, link it. When a team's breakdown surfaces an ambiguity that affects other teams, raise it to the shepherd rather than resolving unilaterally.

## Common Mistakes

- **Letting a cross-team pattern stay team-scoped because filing an idea feels like overhead.** The overhead is real; so is the cost of five teams independently working around the same gap.
- **Filing an idea without naming the friction.** Architecture can help navigate disagreement, but only if the friction has been named where it lives.
- **Confusing the ARCH idea with the BW Initiative.** Two artifacts, two audiences, linked but separate. Keep both in sync as the initiative advances.
- **Skipping the link inventory.** An initiative without "Relates to" links makes everyone re-discover context the next time something similar comes up.
- **Running a team breakdown without reading the TSI.** The idea carries context the initiative description summarizes away — strategic rationale, stakeholder map, known friction. Five minutes of reading upstream saves hours downstream.

## Reference

- [Technical Strategy Ideas](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2344517656) — the canonical TSI template and backlog model.
- [Idea-Based Initiatives](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2785181779) — the canonical BW Initiative structure and phase-by-phase evolution.
- Related: `Skill(navigating-the-initiative-funnel)` for the phase mechanics once an idea is in the funnel, `Skill(architecting-solutions)` for the architectural judgment to bring to both idea-framing and team breakdown, `Skill(running-work-transitions)` for the Phase 4→5 handoff this breakdown feeds into — on either side of the transition.
