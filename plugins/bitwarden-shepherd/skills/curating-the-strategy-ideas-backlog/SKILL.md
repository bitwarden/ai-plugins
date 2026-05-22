---
name: curating-the-strategy-ideas-backlog
description: Peer-Reviewer and portfolio-curator side of the TSI Shepherding Model — backlog stewardship, quarterly prioritization, funnel intake handoff.
when_to_use: Use when peer-reviewing someone else's Technical Strategy Idea or stewarding the ARCH idea portfolio. Triggers — "I'm peer reviewer on ARCH-…", "Architecture Council prep", "quarterly RICE scoring", "transitioning ARCH-X to the funnel". Not for Primary Owner work on a specific idea (use `championing-a-strategy-idea`).
allowed-tools: Skill, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_remote_links, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_issues, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence_cql
---

Peer-Reviewer and portfolio-curator playbook for Bitwarden's [Technical Strategy Ideas](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2344517656) (TSI) backlog — the upstream idea-stage system that feeds the Software Initiative Funnel at Identification. Covers serving as constructive challenge function for someone else's idea, stewarding the backlog (weekly triage, monthly RICE updates, Now/Next/Later placement), the quarterly prioritization review with engineering leadership, and the handoff of approved ideas to the funnel.

## The Two Roles per Active Idea

Each TSI in active status (Research through Implementation) has two Architecture members assigned. The TSI page is explicit about this:

- **Primary owner.** Drives the idea through the pipeline: writes the problem statement, conducts research, presents at Architecture Council, shepherds the transition to the funnel. Accountable for progress. The Primary Owner's playbook is `Skill(championing-a-strategy-idea)`.
- **Peer reviewer.** A second Architecture engineer who acts as a sounding board, stays informed, and provides a **constructive challenge function**. Not a co-owner. Their job is asking the hard questions, catching cross-initiative conflicts, ensuring stakeholder engagement is thorough. **This is your role when invoking this skill** — alongside the broader portfolio-curator practice covered in the rest of the skill.

### How Peer Review Works

Per the TSI page:

- Peer reviewers are assigned per idea. As ideas move through the lifecycle and new ones enter, pairings shift to keep the team building breadth across the portfolio.
- The primary owner shares progress and decision points with the peer reviewer on an ongoing basis. The biweekly architecture working session is the primary venue; ad-hoc check-ins are expected for time-sensitive decisions.
- Before an idea moves from Backlog to Research, the primary owner and peer reviewer **jointly complete the Stakeholder & Engagement Map** section of the template. This is a gate.
- When the idea is presented at Architecture Council, the peer reviewer attends as an informed ally who can help field questions and support the discussion.
- **No single engineer should carry more than two active reviewer assignments at a time, primary or peer.** Overloading review defeats its purpose.

## The Stakeholder & Engagement Map as a Gate

The map is the gate ideas must pass through before advancing from Backlog to Research. Its five fields — Decision makers, Must consult, Must inform, Known friction points, Engagement approach — are detailed in `Skill(championing-a-strategy-idea)`, the canonical home for the map's mechanics from the Primary-Owner side. The map is **completed collaboratively** by Primary Owner and Peer Reviewer; ideas do not enter Research without it.

As Peer Reviewer, your specific job is to push on the map — especially **Known friction points**, the field where ideas most often get soft-pedaled and the TSI page explicitly names as where "technically sound proposals stall at adoption." When triaging an idea ready to advance from Backlog → Research, the question is: is the map complete and honest? Push back if friction is hand-waved, if decision makers are vague ("the Vault team" rather than a named role with stated authority), or if the engagement approach doesn't match the stakeholder's communication style.

## RICE Scoring Discipline

Each idea carries a RICE score: **Reach × Impact × Confidence / Effort**. Per the TSI page, scoring guidance lives in [Idea RICE Scoring](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2634252326/Idea+RICE+Scoring).

Curator practice:

- **Update scores monthly.** As more is learned about an idea — through peer review, stakeholder conversations, or related initiatives advancing — the score gets refined.
- **Weekly new-idea triage** ensures the backlog stays current; **mid-quarter backlog management** revisits scores against the current portfolio.
- Resist score inflation. Reach is what it is; Confidence reflects the actual state of knowledge. An honest RICE score that says "Confidence is low" is more valuable than an inflated one that hides the question that PoC would answer.

## Theme, Roadmap Placement, Customer Segments

Per the TSI page, ideas carry standardized prioritization fields beyond RICE:

- **Theme.** Architecture / Operations / SDLC / Products / Application Security. Determines which portfolio view the idea shows up in.
- **Roadmap placement.** Now / Next / Later. Per the [Architecture / Engineering Operating Model](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/1286963201), these are the lanes used in the Now/Next/Later portfolio communicated to engineering leadership.
- **Customer segments.** Individuals / Teams / Enterprises / Self-Hosted / Internal. Captures who benefits.

The Operating Model is explicit on the distinction between Now, Next, and Later — particularly that **Later is a directional signal, not a commitment**. Keep that framing in conversations with engineering leadership; quarterly date commitments at the Later stage create false precision.

## The Quarterly Prioritization Cycle

Per the TSI page:

| Activity               | Frequency                 | Participants                                             |
| ---------------------- | ------------------------- | -------------------------------------------------------- |
| New-idea triage        | Weekly                    | Architecture                                             |
| Score updates          | Monthly                   | Architecture                                             |
| Backlog management     | Mid-quarter               | Architecture + interested Staff+ engineers               |
| Prioritization review  | Quarterly                 | Architecture + engineering leadership                    |
| Adoption retrospective | Per initiative at handoff | Primary owner + peer reviewer, shared in working session |

The **quarterly prioritization review** is the moment Architecture brings top candidates to engineering leadership for approval to enter the funnel. The Operating Model describes this as the 60-minute quarterly deep review, with a monthly 15–20 minute lightweight update via stakeholder syncs in between.

Curator practice for the quarterly review:

- Walk through the Now / Next / Later portfolio. Highlight what moved since the last review and why.
- Deep-dive on "Now" items: current funnel phase, which teams are or will be involved, what Architecture needs from those teams, expected timeline for engagement. This is where teams get advance notice of work heading their way.
- Discuss "Next" items: invite input on sequencing and priority. What should move up or down? What dependencies don't show in the data? What team-originated ideas belong in the pipeline?
- Open floor for engineering teams to raise topics, ask questions, or flag concerns about architectural direction.

## Transitioning an Approved Idea to the Funnel

When leadership approves an idea for funnel intake (typically at the quarterly review), it transitions to a BW Initiative at Phase 1 Identification. Per the TSI page, this involves:

- **Create Initiative.** A new Jira Initiative under the BW project.
- **Link to idea.** Work-item link from the BW initiative back to the ARCH idea (in JPD). This is the foundational traceability link.
- **Assign shepherd.** A Staff+ engineer identified to lead the initiative through the funnel. Often the primary owner; sometimes a different Staff+ engineer with the right domain expertise.
- **Assign peer reviewer.** A second Architecture engineer as sounding board and challenge function for the funnel work (often the same peer reviewer who was on the idea, sometimes rotated).
- **Complete Stakeholder & Engagement Map.** If not already complete, the shepherd and peer reviewer jointly finalize it before entering Research.
- **Enter Identification.** The initiative starts Phase 1 of the funnel.
- **Update ARCH idea status** to "1️⃣ Identification" in JPD.

From here, the shepherd uses `Skill(shepherding-an-initiative)` and the phase-deep shepherd skills to drive the initiative forward. The peer reviewer continues to be informed and provides challenge function.

## Ideas That Don't Proceed

Per the TSI page, decline reasons include:

- **Not aligned with strategy.**
- **Insufficient value** — cost exceeds benefit, even after considering different approaches.
- **Better handled elsewhere** — team-level work, product processes, other channels.
- **Timing** — external factors or dependencies make it impractical for the foreseeable future.
- **Superseded** by a related idea or existing initiative.
- **Resolved** through other means (team work, external changes).

Declined ideas remain visible in JPD with rationale recorded. The curator-side discipline: **always record the rationale, always preserve the institutional memory**. Without a recorded reason, the same idea gets re-evaluated 6 months later from scratch.

## The Adoption Retrospective (At Funnel Handoff)

Per the TSI page, when an initiative reaches Implementation and begins the Work Transition Playbook handoff, the **Primary Owner and Peer Reviewer run a brief retrospective focused on influence effectiveness** — what engagement worked, where mandate was lacking, where disagreements surfaced late, what to do differently next time.

When you are the Peer Reviewer on the idea, participate. The canonical retrospective playbook — the four questions, what to look for, where findings go — lives in `Skill(championing-a-strategy-idea)`, the Primary Owner's skill. The retrospective is Architecture-internal (Primary Owner + Peer Reviewer), focused on **how Architecture used its influence**, and is distinct from the funnel's end-of-Implementation retrospective (shepherd + receiving tech leads, focused on execution).

## Curator Practices When Reviewing a New Idea

When a tech lead or Staff+ engineer files a new idea, curator-side triage typically includes:

- **Is the problem actually cross-cutting?** If it's contained to one team's codebase, decline with rationale ("stays in-team — see `Skill(contributing-to-technical-strategy)` for when not to file"). Don't pull team-scope work into Architecture's portfolio.
- **Is the Problem / Opportunity Statement specific?** "Error handling is inconsistent" → push back with: "specify the pattern variations and the impact." Reference the TSI page's guidance on specificity.
- **Is friction named?** If the Stakeholder & Engagement Map is missing or hand-waves the "Known friction points" field, send it back. Naming friction up front is non-negotiable for advancement to Research.
- **Is this superseded?** Search the ARCH backlog for adjacent or duplicate ideas. Link explicitly if related; supersede if duplicate.
- **Does this raise enough architectural significance to bring to Architecture Council?** Some ideas — new patterns, major tech choices, cross-cutting security — warrant Council input before entering the funnel.

## Common Mistakes

- **Letting the Stakeholder & Engagement Map slide.** The gate exists for a reason. Ideas that advance to Research without honest friction-naming stall at adoption.
- **Score inflation.** Manufactured Confidence numbers and inflated Reach values produce a backlog that doesn't actually represent reality. The quarterly review depends on the scores being honest.
- **Over-assigning peer review.** More than 2 active assignments per Architecture engineer dilutes the challenge function. The TSI page's "no more than two" rule is load-bearing.
- **Treating decline as failure.** Declined ideas with recorded rationale are valuable institutional knowledge. Quiet drops, not declines, are the problem.
- **Skipping the adoption retrospective at handoff.** Architecture's influence effectiveness only improves if its operating patterns get examined. Participate in it — the playbook for running it is in `Skill(championing-a-strategy-idea)`.
- **Curating in isolation from the Operating Model.** The Now/Next/Later portfolio is communicated to engineering leadership at quarterly review and to Platform at the monthly sync — curate with that audience in mind.

## Reference

- [Technical Strategy Ideas](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2344517656) — canonical TSI template, peer-review model, prioritization cycle, governance.
- [Architecture / Engineering Operating Model](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/1286963201) — Now/Next/Later portfolio communication, Architecture Initiative Review, Architecture/Platform sync.
- [Idea-Based Initiatives](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2785181779) — what the ARCH idea becomes when it transitions to the funnel.
- [Software Initiative Funnel](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/584515614) — where approved ideas go at Phase 1 Identification.
- [Idea RICE Scoring](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2634252326/Idea+RICE+Scoring) — scoring reference guidelines.
- Related: `Skill(championing-a-strategy-idea)` for the Primary-Owner side of the same Shepherding Model (driving a specific idea you hold accountability for); `Skill(contributing-to-technical-strategy)` (in `bitwarden-tech-lead`) for the team-tech-lead-as-contributor side of filing; `Skill(shepherding-an-initiative)` for what happens once an idea is approved and enters the funnel.
