---
name: navigating-the-initiative-funnel
description: The tech lead's role across the five phases of Bitwarden's Software Initiative Funnel. Covers what the shepherd owns vs. what the tech lead owns at each phase, how to run an epic breakdown after handoff, sizing and estimation, cross-team dependency tracking, and the escalation paths that protect team autonomy. Use when your team is about to receive an initiative epic, when you're asked to participate in an Architectural Assessment or PoC, when you're preparing a team breakdown, or when you need to surface concerns back to the shepherd or engineering leadership.
---

Bitwarden runs cross-cutting technical work through the [Software Initiative Funnel](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/584515614). A senior engineer — typically Staff+ for cross-team initiatives, sometimes a tech lead for smaller-scope work that lives largely inside one team's domain — shepherds each initiative through five phases: Identification, Research, Proof of Concept, Scoping & Commitment, and Implementation. The tech lead participates throughout, but most heavily in Scoping & Commitment and Implementation. This skill is the working playbook for that participation, written from the perspective of the tech lead working alongside a separate shepherd; when you are shepherding the initiative yourself, read the phase descriptions for both roles and run both. When you need the canonical reference, fetch the funnel page via the `get_confluence_page` MCP tool; this document is the operating summary.

## The Rule of Ownership

Every phase has a single sentence to remember: **the shepherd owns the initiative; the tech lead owns how their team executes its part**. The moment you blur that line, one of two failure modes shows up — either the shepherd starts writing your stories (and your team doesn't own the work), or you start making cross-team decisions that aren't yours to make (and the initiative drifts).

## Phase-by-Phase: Who Does What

### Phase 1 — Identification

The shepherd creates a BW Initiative issue, documents the problem, and gets a go/no-go from engineering leadership.

**Your role is light here.** If the shepherd reaches out because your team's domain is affected, provide context, known history, and stakeholders. Flag prior attempts you know about. Don't pre-scope — the research hasn't happened yet.

### Phase 2 — Research

The shepherd interviews stakeholders (you are a likely one), surveys the codebase, and produces an Architectural Assessment with 2–4 solution options.

**Your role:** be interviewed well. Share your team's pain points, workarounds, and the constraints the shepherd won't see from outside. Quantify where you can ("this causes ~3 bugs per sprint"). If the shepherd proposes a direction that would conflict with work already on your roadmap, say so now — not after commitment.

### Phase 3 — Proof of Concept

The shepherd picks a PoC area (sometimes in your team's codebase), builds a framework or example, presents to Architecture Council, and drafts an ADR.

**Your role if the PoC lands in your codebase:** assign a point-of-contact on your team to pair with the shepherd or review their PRs. Be a collaborator, not a gate. The PoC is meant to test feasibility in real code — if it's cutting corners, that's a signal worth surfacing, but don't treat the PoC PR like a production review. Surface concerns about the approach to the shepherd directly; don't quietly ship workarounds.

### Phase 4 — Scoping & Commitment

This is the phase where the most rides on your participation. The shepherd creates child epics under the BW initiative (typically one per team or major module), writes epic descriptions, and schedules handoff meetings. Then **your team owns the breakdown**.

The shepherd brings to the handoff: the PoC findings, the architecture plan section relevant to your team, the success criteria, and time for Q&A. You bring: questions, a realistic read on how this fits your existing roadmap, and a commitment date for the breakdown itself.

After the handoff, run a team breakdown session. Your team creates the stories — not the shepherd. Apply the funnel's story-quality rules:

- **Be specific.** "Migrate user-service error handling to new pattern" beats "update error handling."
- **Write acceptance criteria** that define done. Reference the PoC PR or architecture plan for the technical approach.
- **Note dependencies** — especially cross-team ones. Those feed back to the shepherd for coordination.
- **Assign to the team, not to individuals.** Individuals come during sprint planning.
- **Label for filtering** (e.g. `initiative-typescript-migration`) so the shepherd's dashboard can track progress.
- **Size with your team's normal process.** Don't invent a new estimation method for initiative work.

When the breakdown is done, share it back with the shepherd. They review for consistency with the initiative's vision, not to rewrite stories or micromanage. Expect questions like "this looks good but uses callbacks instead of the async/await pattern from the PoC — was that intentional?" That's the shepherd doing their job. Yours is to have a good answer.

Before the initiative advances to Implementation, engineering leadership must explicitly commit capacity — a specific allocation for specific sprints. **Do not accept an epic into your backlog without that commitment.** Executive commitment without operational prioritization is the failure mode where epics sit in backlogs and never get pulled into sprints.

### Phase 5 — Implementation

Your team executes. The shepherd coordinates across teams, answers approach questions, reviews 1–2 early PRs for alignment (not detailed code review), and reports progress to leadership.

Your ongoing responsibilities:

- **Bi-weekly tech-leads sync** with the shepherd and other affected teams. Round-robin on progress, blockers, cross-team dependencies, and emerging questions. 30–45 minutes.
- **Watch for drift inside your team.** If your engineers are interpreting the pattern differently across PRs, tighten guidance — don't wait for the shepherd to catch it.
- **Flag emerging issues.** If your team hits a problem that suggests the PoC didn't cover the real production shape of the problem, raise it. The shepherd can escalate to Architecture Council and coordinate a pause or pivot. The worst outcome is three teams quietly implementing three different workarounds.
- **Use the FAQ doc.** If there's an `#initiative-foo` Slack channel or an FAQ Confluence page the shepherd is maintaining, post answers your team figures out — other teams will hit the same question.
- **Do not stop reviewing code.** The shepherd is not a reviewer for your team's PRs. Your team's detailed code review still happens inside your team.

When your team's epic is done, mark it done, participate in the retrospective the shepherd runs, and hand back to your regular cadence.

## The Two Lists You Hold in Your Head

**Things you own and the shepherd does not:**

- Story breakdown, acceptance criteria, estimates.
- Detailed code review inside your team.
- Your team's PR merging cadence.
- Sprint planning and assignment to individuals.
- Decisions that are purely inside your team's codebase boundary.

**Things the shepherd owns and you do not:**

- The initiative ADR and architecture plan.
- Cross-team consistency and the decision to pause/pivot.
- Architecture Council representation.
- The leadership-facing progress narrative.
- Communicating with other teams' leads about shared dependencies.

When something is in neither list, it's usually a cross-team dependency — which means it belongs to the shepherd until they push it back to you with scope and context.

## Escalation Paths

- **Capacity conflict** (your team can't absorb the epic on the proposed timeline): escalate to your EM and the shepherd. The funnel's Scoping & Commitment phase is explicitly where capacity gets negotiated — that's the right venue, not halfway through Implementation.
- **The PoC approach doesn't work in your team's context:** raise to the shepherd. If it's a fundamental issue, the shepherd takes it to Architecture Council.
- **Another team is drifting from the pattern in a way that will hurt your team's work:** raise to the shepherd. Cross-team consistency is their job; you don't negotiate directly with another team's implementation.
- **The shepherd is absent or unresponsive:** the funnel calls out that shepherds should designate a backup for long absences. If there isn't one, escalate to engineering leadership — don't quietly fill the gap.

## Common Mistakes

- **Accepting the shepherd's stories as written.** If you didn't run your team's breakdown session, you don't have team ownership. Re-run it, even if it feels like redundant work.
- **Treating the handoff as ceremonial.** The handoff meeting is the moment to ask the uncomfortable questions. If something seems off in the PoC pattern, the handoff is cheap; post-merge is expensive.
- **Letting drift compound.** Small variations multiply. Catch them in the first 1–2 PRs, not the last 10.
- **Starting work before capacity is allocated.** Epics that land in backlogs without clear sprint allocation die there. That's a leadership conversation, not a heroism conversation.
- **Over-indexing on the shepherd.** They're coordinating 5+ teams. Your team's detailed code quality, sprint discipline, and team-internal decisions are still yours.

## Reference

- [Software Initiative Funnel](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/584515614) — the canonical phase-by-phase document. Fetch via `get_confluence_page` when you need the full template, the go/no-go criteria, or the example timeline table.
- Related: `Skill(running-work-transitions)` for the Phase 4→5 transition mechanics on either side of the handoff, `Skill(architecting-solutions)` for the architectural judgment you bring to the breakdown.
