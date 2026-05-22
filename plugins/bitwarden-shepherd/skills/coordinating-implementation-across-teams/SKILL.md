---
name: coordinating-implementation-across-teams
description: Phase 5 (Implementation) deep-dive playbook — shepherd coordinates teams executing the initiative across the support period, pulse check, retrospective, and closure.
when_to_use: Use when an initiative is in active execution and the shepherd is coordinating, not implementing. Triggers — "support period", "early PR review for drift", "monthly stakeholder update", "Adoption Retrospective", "closing out the initiative". Not for Phase 4 scoping (use `scoping-and-handing-off-to-teams`).
allowed-tools: Skill, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_remote_links, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_issues, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence_cql
---

Phase 5 (Implementation) deep-dive playbook for an initiative shepherd. **You are not doing the implementation.** You enable teams, maintain consistency, ensure the initiative completes, and step back when it does. Time budget: 2–6 months wall clock, 10–20 hours/month of shepherd time. Composes `Skill(running-work-transitions)` in `bitwarden-delivery-tools` for the originating-side Support Period, Pulse Check, Retrospective, and Closure phases of the [Work Transition Playbook](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2521038855).

The funnel doc's mental model:

> **Think of the shepherd as:**
>
> - A guide ensuring teams stay aligned with the initiative's vision
> - A coordinator managing cross-team dependencies and communication
> - A subject matter expert available for questions about the approach
> - A reporter keeping leadership informed of progress
> - _Not_ a project manager micromanaging day-to-day work
> - _Not_ doing code reviews on every PR (unless specifically needed for approach validation)

## Establishing Communication Channels (Before Implementation Starts)

Set up the coordination mechanisms before teams begin. The funnel doc specifies:

- **Optional dedicated Slack channel** (e.g., `#initiative-typescript-migration`). Pin links to: PoC PR, ADR, architecture plan, Jira dashboard. Use for questions, blockers, and learnings across teams.
- **Bi-weekly tech-leads sync** with all affected tech leads. 30–45 minutes. Round-robin: progress, blockers, questions, cross-team dependencies.
- **Optional office hours** (1–2 hours per week for drop-in questions) or use the company-wide office hours.
- **Monthly stakeholder-sync update** for engineering and architecture leadership — 15 min, status / completion percentage / risks / decisions needed.

Set response-time expectations explicitly when you announce the channel: "Questions in Slack — aim for 1 business day response. Architecture concerns — same day."

## Kickoff Meeting

When teams are ready to begin (capacity allocated, stories in sprint planning), host a 1-hour kickoff with all teams. Per the funnel doc:

- **Recap the initiative.** Problem, solution, PoC results — for engineers who weren't in handoff meetings.
- **Walk through the approach** and key patterns. The PoC PR is the best teaching artifact you have.
- **Review cross-team dependencies.** Make them visible so teams know who they wait on and who waits on them.
- **Introduce communication channels and cadence.** What to use where; what response time to expect.
- **Answer questions and address concerns.**
- **Celebrate the start.**

Share a resources package in the Slack channel: PoC PR, ADR, architecture plan, FAQ (start empty), your availability and response time.

## Supporting Teams During Execution

Four activities, per the funnel doc:

### 1. Answer Questions

- Respond in the Slack channel within ~1 business day.
- Jump on Meets when text doesn't suffice.
- Clarify edge cases or scenarios the PoC didn't cover.
- Provide examples or references to similar implementations.

### 2. Review for Consistency (Not Detailed Code Review)

This is the most-violated rule of Phase 5. The funnel doc is unambiguous: **"Trust teams for detailed code review – only intervene for approach issues."**

- Monitor PRs related to the initiative.
- Review **the approach in early PRs from each team** to ensure alignment with the PoC pattern.
- Provide feedback only on approach deviation, not on style, naming, test coverage, or anything else the team's own reviewers handle.
- The funnel doc's example pattern: "This looks good but uses callbacks instead of the async/await pattern from the PoC — was that intentional?"

The "Not a reviewer for the team's PRs" line from `navigating-the-initiative-funnel` applies symmetrically here: tech leads expect you not to be their team's code reviewer. Respect it.

### 3. Troubleshoot Unexpected Issues

When teams hit problems the planning didn't anticipate:

- Help diagnose: implementation issue, or approach issue?
- For approach issues, escalate to Architecture Council if fundamental adjustment is needed.
- Document solutions in the FAQ so other teams can learn.

### 4. Unblock Dependencies

- Track which teams are waiting on others (via the dashboard and the bi-weekly sync).
- Coordinate communication between dependent teams.
- Escalate to engineering leadership when blockers can't be resolved at the team level.
- Adjust sequencing if the original plan proves problematic.

## Maintaining Cross-Team Consistency

The funnel doc calls this "one of the shepherd's most critical responsibilities." Four sub-activities:

- **Early detection of divergence.** Notice when teams interpret the pattern differently. Spot legitimate variation vs. misunderstanding. Review 1–2 early PRs per team to catch issues before they multiply.
- **Share learnings across teams.** Post in Slack when one team solves a common problem. Update the FAQ as patterns emerge. Call out good examples: "Team X's PR #567 shows a clean way to handle this edge case."
- **Refine guidance when needed.** If teams consistently struggle, the guidance may need improvement. Update the architecture plan or create supplementary guides. Host ad-hoc working sessions if multiple teams hit the same issue.
- **Make judgment calls on acceptable variation.** Some variation is appropriate based on context (e.g., "Mobile apps use variation A because of platform constraints; web should use the standard pattern"). Some variation is drift that undermines consistency. Document the calls.

## Tracking and Reporting Progress

The funnel doc specifies multiple cadences:

### Weekly (Your Internal Tracking)

- Review Jira dashboard: completed, in progress, blocked.
- Check the Slack channel for unresolved questions or concerns.
- Note risks or trends (e.g., multiple teams reporting the same issue).

### Bi-Weekly Tech-Leads Sync

- 30–45 minute meeting with tech leads from all affected teams.
- Round-robin update: progress, blockers, questions.
- Coordinate on dependencies.
- Identify needs for Architecture Council input.

### Monthly Leadership Update

15-minute slot in a stakeholder sync. Cover:

- **Status:** on track / at risk / blocked.
- **Completion percentage** (stories done / total stories).
- **Revised timeline** if needed.
- **Escalations** or decisions needed.

Example phrasing from the funnel doc:

> "TypeScript migration 60% complete, 3 of 6 teams finished their epics. Vault team delayed 2 weeks due to higher priority security fix. Still on track for Q3 completion."

### Celebrating Milestones

- First team completes its epic — recognition in Slack / team meeting.
- 50% completion — update in company all-hands.
- Last PR merged — celebrate with everyone involved.

## Managing Documentation

Documentation should not wait until the end. Per the funnel doc:

- **Draft early.** Create documentation structure (outline / skeleton) as Implementation starts.
- **Add content progressively.** As patterns stabilize and teams produce real implementations, add to the docs.
- **Have teams contribute examples** from their own implementations.

Documentation lands in two homes per [Documentation Patterns](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/1774977070). What goes where:

**Close-to-code (alongside the team's code, in the repository):**

- **Framework / pattern `README.md`** updates as the pattern stabilizes across teams. The PoC's initial framework README evolves with what teams discover during rollout.
- **Folder-level notes** in each team's adopted area pointing to the framework README and the ADR.
- **Inline docs** (JSDoc/XML comments for TypeScript/Angular/.NET; `rustdoc` for Rust) per the per-stack rubric in Documentation Patterns.
- **CLAUDE.md updates** at the root and folder levels where the new pattern changes how engineers (and Claude tooling) should work. Use `@` syntax to link the `README.md` files that carry the canonical pattern.

**Centralized (in [`bitwarden/contributing-docs`](https://github.com/bitwarden/contributing-docs), rendered at [contributing.bitwarden.com](https://contributing.bitwarden.com/)):**

- **ADR updates** — final status (Accepted → Implemented if your numbering scheme uses that), lessons learned, actual timeline vs. predicted. Edit the same ADR file you opened during PoC; don't create a new one.
- **Migration guide** — how to convert from the old pattern to the new. This is logistical / how-to content and belongs centrally so it's findable across repos.
- **Contributing guide updates** — new standards or patterns that should govern future code beyond this initiative.
- **Runbooks** — if the initiative involved operational or infrastructure changes, runbook content typically lives here too (or in SRE's home as appropriate).

Timing per the funnel doc:

- Draft technical guide when 2–3 teams have completed implementation.
- Finalize all documentation before marking the initiative complete.
- Plan for documentation to be ready 1–2 weeks before the final PR merges.

## Knowledge Transfer

Per the funnel doc, ensure the initiative's outcomes live beyond your involvement. During final weeks:

- **Tech talk or brown bag** (45–60 min) for full engineering org, possibly at an office hours session or Architecture Council slot.
- **Onboarding materials** for new engineers.
- **Update team runbooks** with new patterns.
- **Consider recording** a video walkthrough.

Tech talk structure (funnel doc):

| Time   | Content                  |
| ------ | ------------------------ |
| 5 min  | Approach we took and why |
| 10 min | Demo or code walkthrough |
| 5 min  | Results and metrics      |
| 5 min  | Lessons learned          |
| 5 min  | Q&A                      |

## The 30-Day Pulse Check (Work Transition Playbook Phase 4)

Composing the playbook from the originating side — this is the load-bearing checkpoint that prevents "we handed it off" from becoming "it was never picked up." The Work Transition Playbook is unambiguous: **the 30-day pulse check is the one phase that should not be skipped regardless of how the rest is adapted.**

A 15–30 minute conversation, or an async thread. Cover:

- Has the team begun working with the transferred material? If not, what's blocking?
- Unanswered questions or insufficient documentation areas?
- Is the team comfortable with the approach, or working around it?
- Does the support period need adjustment?

If a team hasn't started at all, escalate jointly with the receiving team — not punitively. Capacity issue, priority conflict, or transition gap? Understand before assuming.

## Mid-Flight Course Correction

The funnel doc's example: mid-implementation discovery of GraphQL resolver performance issues. The shepherd's response:

- Immediately raise to Architecture Council.
- Pause affected teams' work while investigating.
- Work with one team to test a revised approach.
- Update guidance with the new findings.
- Communicate clearly: **"Pause, don't abandon, we're fixing this."**
- Extend timeline if needed.

The lesson: good shepherding includes recognizing when to pause, adjust, and communicate — not just pushing forward regardless.

## Completion and Closure

### Exit Criteria

Per the funnel doc, the initiative is complete when:

- All stories completed and merged to `main`.
- All teams' epics marked complete in Jira.
- Documentation written, reviewed, and published.
- Knowledge transfer completed.
- Retrospective conducted.

### Retrospective (Work Transition Playbook Phase 5, ~90 Days)

Schedule within 2 weeks of completion, while memories are fresh. 1.5 hours, you + tech leads from all affected teams. Per the funnel doc's agenda:

- **What went well?** Processes that worked, coordination wins, what to repeat.
- **What could have gone better?** Friction points, delays, wrong assumptions, what to do differently.
- **Process improvements.** Communication adjustments, scoping or estimation changes.
- **Was the work understood well enough to execute?** Which teams were close on estimates? Which were off? What caused variance?

Document findings and action items. Update the funnel process documentation with the learnings — Bitwarden's funnel gets better when shepherds add what they learned.

### Closure (Work Transition Playbook Phase 6)

- Mark the BW initiative as complete in Jira.
- Archive the Slack channel (or make read-only as reference).
- Ensure all documentation is findable.
- Update related runbooks or onboarding materials.
- Submit any funnel-process improvements based on learnings.
- Update the ARCH idea status to its final completed status in JPD.

Recognize contributors publicly (all-hands, Slack), in performance reviews, with a case-study post if warranted.

The Work Transition Playbook's framing on closure applies here: don't linger as a "just-in-case" reviewer past closure — that's a soft form of refusing to let go.

## Impact Measurement (3–6 Months After Completion)

Per the funnel doc, revisit the success metrics defined during Scoping:

- **Quantitative metrics** (if defined): bug reduction before/after, performance improvements, time savings. Example from the doc: "Predicted 30% reduction in error handling bugs; actual reduction: 42%."
- **Qualitative feedback:** survey teams — is the new pattern better than the old? What's working, what's not?
- **Adoption tracking:** Is new code following the pattern? Are teams defaulting to the new approach? Drift back to old patterns?

Document results:

- Update the ADR with actual vs. predicted outcomes.
- Add impact summary to the architecture plan.
- Share results with the engineering org.

## Updates to the BW Initiative

During Implementation (see [Idea-Based Initiatives](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2785181779)):

- **Status tracking is primarily through child epics and their stories** — the initiative itself doesn't need frequent field updates.
- **Comments:** Significant coordination events — cross-team dependency resolution, mid-course corrections, milestone achievements, escalations. Comments become the narrative timeline used at retrospective.
- **Links:** Add new related work as it emerges — operational tickets, bug reports, documentation pages, adjacent initiatives.
- **Description:** Update only if scope or approach changed materially.
- **ARCH idea status:** Update to "5️⃣ Implementation" at kickoff, then to its final status at completion.

## Common Mistakes

- **Doing detailed code review.** You are not the team's reviewer. Approach-alignment only.
- **Letting drift compound.** Catch divergence in PRs 1–2 per team, not PRs 10–20.
- **Skipping the 30-day pulse check.** The Work Transition Playbook is explicit — this is the load-bearing checkpoint. Skip it and silent failure modes become invisible.
- **Treating documentation as an end-phase artifact.** Patterns drift between Implementation and writeup. Document progressively.
- **Quietly resuming work** because a team isn't picking it up. Per the playbook, that's a leadership conversation, not a heroism opportunity.
- **Lingering past closure.** Hand back to the team's regular cadence and step away. The signal matters.
- **Skipping the retrospective.** It's the only mechanism that improves the funnel itself.

## Reference

- [Software Initiative Funnel](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/584515614) §5 — canonical phase description, examples of successful, troubled, and course-correcting implementations.
- [Work Transition Playbook](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2521038855) — canonical six-phase transition; Phase 5 of the funnel is the originating-side support-period-through-closure portion.
- [Documentation Patterns](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/1774977070) — close-to-code vs. centralized `contributing-docs`, per-tech-stack best practices, CLAUDE.md conventions.
- [Idea-Based Initiatives](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2785181779) — how to update the BW Initiative through Implementation.
- Related: `Skill(shepherding-an-initiative)` for the umbrella playbook; `Skill(running-work-transitions)` (in `bitwarden-delivery-tools`) for the originating-side support-period guidance; `Skill(scoping-and-handing-off-to-teams)` for the phase that hands work into this one.
