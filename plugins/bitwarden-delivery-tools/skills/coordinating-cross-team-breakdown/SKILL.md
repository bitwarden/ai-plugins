---
name: coordinating-cross-team-breakdown
description: Coordinate cross-team review and signoff for a Bitwarden Tech Breakdown. Use when identifying affected teams, building the Cross-team engagement signoff table, chasing signoffs to move from Proposed to Accepted, or running the completion-communication checklist before Complete.
allowed-tools: Skill, Read, Edit, Write, Bash, Glob, Grep, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_remote_links, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_issues, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page_comments
---

This is the cross-team half of Bitwarden's Tech Breakdown. It covers the Cross-team engagement section (three subsections plus the signoff table) and the completion-communication checklist that closes the breakdown. The engineering content of the breakdown — Specification, Clarifications Log, Plan, Tasks, Agent Context — lives in `Skill(writing-tech-breakdowns)`; the canonical state machine (`In Planning → In Progress → Proposed → Accepted → Complete`, with `Rejected` as the terminal alternative) is documented there. This skill is what runs when the breakdown reaches `Proposed` and what runs again when implementation lands and the breakdown is ready to move to `Complete`.

## Canonical source

The canonical template lives in the [`bitwarden/tech-breakdowns`](https://github.com/bitwarden/tech-breakdowns) repo at `templates/tech-breakdown.md`. Read it directly when you need literal headings, column labels, or checklist items — this skill is the operating summary, not the source of truth. Files under `**/complete/**` are point-in-time historical records, not source of truth; don't pull patterns from them unless explicitly asked to mine prior decisions.

## Identifying Affected Teams

The signoff table is only as useful as the team list that feeds it. Two sources, in order:

### 1. The Initiative, via the funnel

If the breakdown sits under a BW Initiative, **run `Skill(navigating-the-initiative-funnel)`** to pull:

- The initiative's affected-teams list — typically identified by the owner during Scoping & Commitment.
- Sibling teams' epics under the same initiative — these become rows in the signoff table, with each row linking to the sibling team's own breakdown in the "Associated breakdown" column.
- The owner themselves — they hold the cross-team coordination context this skill is built around. Loop them in early, especially if a signoff is going to be contentious.

The funnel-first approach is the default when an initiative exists. It produces a signoff list that reflects the same affected-teams picture the owner is reporting to leadership. Drift between the two is itself a signal worth surfacing.

### 2. The cross-team checklist, for team-scoped work or initiative gaps

When no initiative exists, or when the initiative's affected-teams list is missing rows that the work clearly touches, walk the three Cross-team engagement subsections directly. Each question maps to potential signoff rows.

## The Three Cross-team Engagement Subsections

The template splits cross-team work into three explicit subsections plus a signoff table plus coordination notes. Walk each subsection before considering the section complete.

### Consuming other teams' APIs

For each external service or component used: name the team, the interface, the assumed behavior, and any known constraints or roadmap risk on the providing team's side. The checklist question — "any significant reliance on other teams' service/component APIs?" — is asking you to verify that the dependency is stable. Check publicly visible tech debt indicators, recent incidents, or planned deprecations on the providing team. If concerns exist, surface them as Clarifications Log entries in the breakdown.

### Changes required in other teams' code

For each file or module outside the team's domain that needs to change: name the team, the file or module, the change, the collaboration model, and the Jira items.

Two specific rules from the checklist:

- **Mobile changes** must be defined as separate Jira Tasks/Stories on the Mobile team's board. Don't fold mobile work into the originating team's stories — the Mobile team owns its sprint and its codebase.
- **Components, services, or files outside the team's domain** — post on the owning team's public Slack channel to evaluate impact before adding them to the signoff table. Public channels (not DMs) so the rest of the team has visibility into the request and can self-route to whoever's best positioned to respond. Surprise signoff requests don't work well. If a sibling team's breakdown for related work already exists, link it.

### Cross-team sequencing & ordering

If this change delivers an API or service for another team, follow the **interface-first pattern**:

- Define the interface early so the consuming team can code against it while implementation is in flight.
- Consult the consuming team **twice**: once at design (after the interface is defined in the breakdown), and again at PR (after the implementation lands). Both touchpoints belong on the signoff list.

If the order matters in the other direction — the team needs another team's work to land first — capture it in Coordination notes so the dependency is explicit.

## The Cross-team Signoff Table

A worked example with both in-flight and fully-signed-off shapes lives at `${CLAUDE_PLUGIN_ROOT}/skills/coordinating-cross-team-breakdown/examples/signoff-table.md`. Use it as a shape reference for what good cells look like, the Blocking-vs-advisory distinction, and what a healthy table looks like at `Proposed` versus `Accepted`.

The template specifies five columns. Treat each as load-bearing:

| Column                   | What goes in it                                                                                                                                                                                                                                                                                    |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Team**                 | The owning team's name. One row per team — combine sub-interfaces under a single team's row in the "Interface" cell.                                                                                                                                                                               |
| **Interface**            | What this breakdown asks of the other team. "API endpoint they will consume," "shared service they own that we extend," "component library extension," "mobile parity for new feature." Specific enough that an engineer on the other team can react to it without re-reading the whole breakdown. |
| **Blocking?**            | Yes/No. Is this team's signoff a hard gate on moving to `Accepted`, or is it advisory (FYI-level)? Get this right — over-marking as Blocking stalls breakdowns; under-marking produces signoffs that get ignored.                                                                                  |
| **Associated breakdown** | Link to the sibling breakdown if the other team is producing their own. Empty when the other team isn't producing a breakdown for this specific interface (advisory rows often have no associated breakdown).                                                                                      |
| **Signoff**              | The named human who signed off, with the date. Not "the team" — a specific person. The template renders this as a checkbox; capture the human + date inline.                                                                                                                                       |

**Rule of thumb on Blocking?:** if the other team owns code the change directly modifies, calls into, or depends on the contract of, signoff is Blocking. If the other team is being informed because their area is adjacent or could be incidentally affected, signoff is advisory.

## Coordination Notes

The template's free-form `Coordination notes` subsection captures anything about the cross-team seams that isn't obvious from the table:

- Which team's PR lands first.
- Whether a temporary API stub is needed.
- Whether one team's work needs to land in a feature branch.
- Any sequencing constraints that fall outside the standard interface-first pattern.

Fill this in when the table alone doesn't tell the full coordination story. Empty is fine when the table is self-explanatory; vague is not.

## Chasing Signoffs

Once the table is built, signoffs become the gating work to move from `Proposed` to `Accepted`. A few rules:

- **Post on the other team's public Slack channel, tagging the named human in the signoff row.** Public channels give the rest of the team visibility and allow self-routing if the tagged person is unavailable. Don't DM — the request loses team-level visibility. The breakdown link (file path or GitHub link) is sufficient — they should be able to evaluate from the doc plus any inline Plan content.
- **Don't accept "looks fine" without a name and date in the signoff column.** A breakdown that moves to `Accepted` with empty signoff cells defeats the artifact.
- **Treat blocking signoffs as blockers.** If a Blocking row has been outstanding for more than a sprint, escalate — to the initiative owner if there's one, to the team's EM if not. Long-open blocking signoffs are usually a symptom that the cross-team interface is contested and needs renegotiation, not just patience.
- **When a signoff surfaces an issue, route it back through `Skill(writing-tech-breakdowns)`.** Material design changes belong in the engineering content, not in Slack threads attached to a signoff request. Update Specification or Plan in the breakdown, re-confirm with anyone who has already signed off, then re-circulate.

### Owner-Mediated Escalation

When the breakdown sits under an initiative and a signoff is contested:

- **Surface to the initiative owner before negotiating directly with the other team.** Cross-team consistency across an initiative is the owner's job — they've seen the same interface from the other team's side and likely have context the team doesn't.
- **The owner can pull Architecture Council in** if the contested interface has architectural implications. Don't escalate to Architecture directly; route through the owner.
- **If there's no owner** (team-scoped breakdown), escalate to the team's EM and the other team's EM. Cross-EM commitments aren't made unilaterally at the IC level — that's a leadership conversation by design.

Run `Skill(navigating-the-initiative-funnel)` for the escalation paths — they're documented there in detail.

## Moving to Accepted

Two gates must close before the breakdown moves from `Proposed` to `Accepted`:

1. **Cross-team signoff** — every blocking signoff is captured in the signoff table with a named human and a date. Advisory signoffs that remain open should be chased to closure but don't block `Accepted` on their own.
2. **Team refinement** — the implementing team has completed a refinement pass on the Tasks section, with refinement feedback folded back into the breakdown and the team confirming the Task decomposition is workable. This skill drives gate 1; gate 2 is owned in `Skill(writing-tech-breakdowns)` and runs in parallel during `Proposed`.

Both gates are required. A breakdown that has every external signoff but hasn't been refined by the implementing team is **not** ready for `Accepted` — the implementing team's understanding and ownership of the work is part of what `Accepted` signals.

The state machine is defined in `Skill(writing-tech-breakdowns)`; confirm the transition rules there. In practice the move to `Accepted` means confirming both gates have closed, updating the Status block at the top of the breakdown (status + Last substantive update), **running the stakeholder-communication checklist below** (announcement, QA contact, Jira story creation, refinement-facilitator handoff for scheduling), and merging the PR.

Once `Accepted`, implementation can begin. Material changes after `Accepted` require either superseding the breakdown or moving it back to `Proposed` and re-circulating affected signoffs and refinement — see the lifecycle rules in `Skill(writing-tech-breakdowns)`.

## The Stakeholder-Communication Checklist (at Accepted)

The template's "When complete, communicate this to stakeholders" preamble checklist runs when **the breakdown document is complete** — i.e., at the `Proposed → Accepted` transition, not at post-implementation `Complete`. By the time implementation ships, all four items below have already happened and the resulting downstream work (test cases, refinement) is well underway.

Run this checklist on the same PR that flips status to `Accepted`:

1. **Verify signoff from all involved teams.** Re-read the signoff table. Every blocking row has a named human and date; every advisory row has a closure note. Any gap here is a blocker on moving to `Accepted`.
2. **Post a link in `#team-eng-tech-breakdowns`** for cross-team visibility. This is the org-wide announcement that the design is settled. Other teams browse this channel to spot cross-cutting changes — skipping the post is invisible until somebody downstream is blindsided.
3. **Contact the responsible QA Engineer** so they can review the breakdown and build test cases against the design. QA leans on the breakdown as the source of truth for test coverage — get the right QA owner involved explicitly. If a QA owner hasn't been identified, post on the team-internal Slack channel to surface them.
4. **Create Jira stories from the Tasks section.** Each row in the breakdown's Tasks section becomes a story carrying the Ticket Shape. **Place each piece in the correct Jira field** — story-specific tech breakdown and breakdown link in Description, acceptance criteria in the Acceptance Criteria custom field (not Description), implementation pointers and test scenarios in Description, parent epic via Epic Link, and Blocked on / Depends on rows as `is blocked by` / `depends on` issue links. The detailed field mapping, link-type rules, and bidirectional-sync taxonomy live in `Skill(writing-tech-breakdowns)` under `references/jira-story-mechanics.md`. Mechanics-level writes are delegated to whichever Jira authoring tooling the engineer has available (e.g., a `jira-manager` or `jira-cli` skill if installed, direct Atlassian MCP write calls, or the Jira UI). After creation, update the Tasks section with a link to each story so the breakdown points forward to the tickets — the bidirectional link is what keeps the artifacts findable from each other later. From this point on, follow the sync rules in `references/jira-story-mechanics.md` for any future edit.
5. **Hand the Task decomposition off to the team's refinement facilitator** for scheduling into refinement sessions. Refinement may already have begun during `Proposed` as part of internal review (see `Skill(writing-tech-breakdowns)`); this step is the formal handoff for sprint scheduling. Without it, the breakdown's stories sit in the backlog instead of being picked up.

## Moving to Complete

When implementation has shipped, the breakdown moves to `Complete`. Only one action here:

- **Move the file to `<team>/complete/`** on the same PR that flips status to `Complete`. CODEOWNERS still routes review to the owning team for files under `complete/`. After this move, the breakdown is a reference artifact — no further edits except corrections to factual errors.

Then merge the PR. The breakdown's new home is the team's `complete/` archive. There's nothing else to do at this transition; the stakeholder-communication work happened at `Accepted`.

## The Rejected Terminal State

The terminal alternative to `Complete`. Use when cross-team review surfaces incompatibilities or blockers that can't be resolved within the breakdown's scope. Preserve the breakdown — it's the historical record of why the approach didn't work — and produce a new breakdown if the work is being re-shaped. Communicate the rejection on `#team-eng-tech-breakdowns` so other teams know not to plan against the original. `Rejected` breakdowns stay in the team's main folder (not under `complete/`) so the rejection state is visible at a glance.

## Common Mistakes

- **Building the signoff table without funnel context.** When an initiative exists, the owner has already done team-identification work. Ignoring that produces drift and duplicated signoffs.
- **Over-marking signoffs as Blocking.** Every blocking row is a hard gate. If half the table is blocking, the breakdown won't move to `Accepted`. Reserve Blocking for teams whose code the change touches or whose contract the change depends on.
- **Under-marking signoffs as Blocking.** Advisory signoffs from teams that own the code being modified produce signoffs that get ignored — and surprises during implementation.
- **Letting signoffs go open without escalation.** A blocking row outstanding for a sprint is a contested interface, not a patience problem. Escalate via the initiative owner or EMs.
- **Negotiating cross-team interfaces directly when there's an initiative owner.** Cross-team consistency is the owner's job. Direct team-to-team negotiation undercuts that and produces designs that diverge across teams in the same initiative.
- **Skipping the file move to `complete/`.** Without it, the team's active folder fills with finished work and CODEOWNERS reviewers can't tell at a glance what needs attention.
- **Running the stakeholder-communication checklist at the wrong transition.** Posting on `#team-eng-tech-breakdowns`, contacting QA, and looping in the refinement facilitator happen at `Accepted`, when the design is settled and downstream work needs to be scheduled. Deferring them to the post-implementation `Complete` transition means QA tests get written after the code lands and refinement is too late to shape sprint pickup.
- **Editing the signoff table to record a signoff that wasn't actually given.** If a signoff is genuinely contingent ("yes, with these caveats"), capture the caveats in the Clarifications Log before moving to `Accepted`. Don't paper over conditional signoffs.
- **Treating the signoff table as the only gate on `Accepted`.** Cross-team signoff is one of two required gates; the other is the implementing team's own refinement pass on the Tasks section. A breakdown with every external signoff but no team refinement isn't ready for `Accepted` — the implementing team's understanding and ownership of the work is part of what the state signals.

## Reference

- [`bitwarden/tech-breakdowns`](https://github.com/bitwarden/tech-breakdowns) — the breakdowns repo. Template at `templates/tech-breakdown.md`. Each team's in-flight work is under `<team>/`; completed work is under `<team>/complete/`.
- Related: `Skill(writing-tech-breakdowns)` — the engineering content of the breakdown and the canonical state machine. `Skill(navigating-the-initiative-funnel)` — load-bearing when the breakdown sits under a BW Initiative; provides the initiative owner, affected-teams list, and escalation paths used throughout this skill. `Skill(architecting-solutions)` (in the `bitwarden-tech-lead` plugin) — the architectural-judgment lens for evaluating contested cross-team interfaces during signoff.
