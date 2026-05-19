---
name: coordinating-cross-team-breakdown
description: Coordinate cross-team review and signoff for a Bitwarden Tech Breakdown. Use when identifying affected teams, building the Part 3 signoff table, chasing signoffs to move from PROPOSED to ACCEPTED, or running the completion-communication checklist before COMPLETE.
allowed-tools: Skill, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_remote_links, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_issues, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence_cql
---

This is the cross-team half of Bitwarden's [Tech Breakdown Template](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2920349776). It covers Part 3 (the signoff table and cross-team checklist) and the completion-communication checklist that closes the breakdown. The engineering content of the breakdown — Parts 1, 2, 4, 5, 6 — lives in `Skill(writing-tech-breakdowns)`; the canonical state machine (`IN PLANNING → IN PROGRESS → PROPOSED → ACCEPTED → COMPLETE`) is documented there. This skill is what runs when the breakdown reaches `PROPOSED` and what runs again when implementation lands and the breakdown is ready to move to `COMPLETE`.

When the canonical template is needed, fetch page `2920349776` via `get_confluence_page`.

## Identifying Affected Teams

The signoff table is only as useful as the team list that feeds it. Two sources, in order:

### 1. The Initiative, via the funnel

If the breakdown sits under a BW Initiative, **run `Skill(navigating-the-initiative-funnel)`** to pull:

- The initiative's affected-teams list — the shepherd has typically identified this during Scoping & Commitment.
- Sibling teams' epics under the same initiative — these become rows in the signoff table, and each links to the sibling team's own breakdown in the "Associated Other Team Breakdown" column.
- The shepherd themselves — they hold the cross-team coordination context this skill is built around. Loop them in early, especially if a signoff is going to be contentious.

The funnel-first approach is the default when an initiative exists. It produces a signoff list that reflects the same affected-teams picture the shepherd is reporting to leadership. Drift between the two is itself a signal worth surfacing.

### 2. The cross-team checklist, for team-scoped work or initiative gaps

When no initiative exists, or when the initiative's affected-teams list is missing rows that the work clearly touches, walk the Part 3 cross-team checklist directly. Each question maps to potential signoff rows:

- **Will there be mobile changes?** If yes, the Mobile team is on the list — and any mobile changes need to be defined as separate Jira stories that are moved to the Mobile team's board. Mobile work is structurally separate; don't fold it into the originating team's stories.
- **Components, services, or files outside the team's domain?** Each affected area implies the owning team is on the list. **Contact their tech lead and EM via DM** to evaluate impact before adding them — surprise signoff requests don't work well. If a sibling team's breakdown for related work already exists, link it in the "Associated Other Team Breakdown" column.
- **Reliance on other teams' services?** Significant reliance triggers two checks: is the dependency stable (no major tech debt flagged in that area, no near-term replacements planned), and is the other team aware of the volume/shape of the usage. The owning team is on the signoff list. If their tech debt is a real risk, surface it as a Part 5 open question in the breakdown.
- **Building an API or service for another team?** If yes, **consider producing the interface first** so the consuming team can code against it while implementation is in flight. The consuming team needs to be consulted twice: once after the interface design is complete (the breakdown level), and again at the PR stage of the implementation. Both reviews go on the signoff list.

## The Part 3 Signoff Table

A worked example with both in-flight and fully-signed-off shapes lives at `${CLAUDE_PLUGIN_ROOT}/skills/coordinating-cross-team-breakdown/examples/signoff-table.md`. Use it as a shape reference for what good cells look like, the Blocking-vs-advisory distinction, and what a healthy table looks like at PROPOSED versus ACCEPTED.

The template specifies five columns. Treat each as load-bearing:

| Column                              | What goes in it                                                                                                                                                                                                                                          |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Team**                            | The owning team's name. One row per team — combine sub-interfaces under a single team's row in the "Describe interface" cell.                                                                                                                            |
| **Describe interface**              | What this breakdown asks of the other team. "API endpoint they will consume," "shared service they own that we extend," "component library extension," "mobile parity for new feature." Specific enough that the other team's tech lead can react to it. |
| **Blocking?**                       | Yes/No. Is this team's signoff a hard gate on moving to ACCEPTED, or is it advisory (FYI-level)? Get this right — over-marking as Blocking stalls breakdowns; under-marking produces signoffs that get ignored.                                          |
| **Associated Other Team Breakdown** | Link to the sibling breakdown if the other team is producing their own. Empty when the other team isn't producing a breakdown for this specific interface (advisory rows often have no associated breakdown).                                            |
| **Signoff**                         | The named human who signed off, with the date. Not "the team" — a specific tech lead, engineer, or EM. Empty until signoff is received.                                                                                                                  |

**Rule of thumb on Blocking?:** if the other team owns code the change directly modifies, calls into, or depends on the contract of, signoff is Blocking. If the other team is being informed because their area is adjacent or could be incidentally affected, signoff is advisory.

## Chasing Signoffs

Once the table is built, signoffs become the gating work to move from `PROPOSED` to `ACCEPTED`. A few rules:

- **Reach out directly to the named human in the other team's signoff row.** A DM to a tech lead beats an @-channel post; an @-channel post beats nothing. The breakdown link is sufficient — they should be able to evaluate from the doc plus any linked Part 4 artifacts.
- **Don't accept "looks fine" without a name and date in the signoff column.** A breakdown that moves to ACCEPTED with empty signoff cells defeats the artifact.
- **Treat blocking signoffs as blockers.** If a Blocking row has been outstanding for more than a sprint, escalate — to the shepherd if there's one, to the team's EM if not. Long-open blocking signoffs are usually a symptom that the cross-team interface is contested and needs renegotiation, not just patience.
- **When a signoff surfaces an issue, route it back through `Skill(writing-tech-breakdowns)`.** Material design changes belong in the engineering content, not in Slack threads attached to a signoff request. Update Parts 1–4 in the breakdown, re-confirm with anyone who has already signed off, then re-circulate.

### Shepherd-Mediated Escalation

When the breakdown sits under an initiative and a signoff is contested:

- **Surface to the shepherd before negotiating directly with the other team's tech lead.** Cross-team consistency across an initiative is the shepherd's job — they've seen the same interface from the other team's side and likely have context the team doesn't.
- **The shepherd can pull Architecture Council in** if the contested interface has architectural implications. Don't escalate to Architecture directly; route through the shepherd.
- **If there's no shepherd** (team-scoped breakdown), escalate to the team's EM and the other team's EM. Cross-EM commitments aren't made unilaterally at the IC level — that's a leadership conversation by design.

Run `Skill(navigating-the-initiative-funnel)` for the escalation paths — they're documented there in detail.

## The Cross-Team Checklist, Walked Once

Independent of the signoff table, Part 3's cross-team checklist is also a forcing function on the breakdown itself. Walk it explicitly before considering Part 3 complete:

- **Mobile changes** — defined as separate Jira tasks/stories on the Mobile team's board. Don't fold mobile work into the originating team's stories; the Mobile team owns its sprint and its codebase.
- **Components/services/files outside the team's domain** — already accounted for in the "Related breakdowns" linkage from Part 1? If not, contact the affected team's tech lead and EM via DM, then add them to the signoff list. Don't surface dependencies during cross-team review for the first time.
- **Using other teams' services** — verify the dependency is stable. Check publicly visible tech debt indicators, recent incidents, or planned deprecations. If concerns exist, raise them as Part 5 open questions in the breakdown.
- **Building APIs for another team** — the interface-first pattern. Produce the contract early, consult the consuming team at design and at PR.

This walk is fast on a small breakdown and material on a large one. Don't skip it for the latter.

## Moving to ACCEPTED

The breakdown moves from `PROPOSED` to `ACCEPTED` when **every blocking signoff is captured in the Part 3 table with a named human and a date**. Advisory signoffs that remain open are not a gate; they should be chased to closure but don't block ACCEPTED.

The state machine is defined in `Skill(writing-tech-breakdowns)`; confirm the transition rules there. In practice the move to ACCEPTED means setting the status field at the top of the breakdown and recording the transition date.

Once ACCEPTED, implementation can begin. Material changes after ACCEPTED require either superseding the breakdown or moving it back to PROPOSED and re-circulating affected signoffs — see the lifecycle rules in `Skill(writing-tech-breakdowns)`.

## The Completion-Communication Checklist

When implementation has shipped and the breakdown is ready to move to `COMPLETE`, run the closing checklist from the template:

1. **Verify signoff from all involved teams.** Re-read Part 3. Every blocking row has a named human and date; every advisory row has a closure note. If anything is still open, close it before marking COMPLETE.
2. **Post a link in `#team-eng-tech-breakdowns`** for cross-team visibility. This is the org-wide announcement that the breakdown landed. Other teams browse this channel to spot cross-cutting changes — skipping the post is invisible until somebody downstream is blindsided.
3. **Contact the responsible QA Engineer** so they can review the breakdown and build test cases against the design. QA leans on the breakdown as the source of truth for test coverage — get the right QA owner involved explicitly. If a QA owner hasn't been identified, post on the team-internal Slack channel to surface them.
4. **Contact the refinement facilitator for the team** to make sure the resulting tasks can be included in the next refinement session. This is the bridge from breakdown to sprint planning — without it, the breakdown's stories sit in the backlog instead of being picked up.

Then set status to `COMPLETE`. The breakdown is now a reference artifact — no further edits except corrections to factual errors.

## The REJECTED Terminal State

The terminal alternative to COMPLETE. Use when cross-team review surfaces incompatibilities or blockers that can't be resolved within the breakdown's scope. Preserve the breakdown — it's the historical record of why the approach didn't work — and produce a new breakdown if the work is being re-shaped. Communicate the rejection on `#team-eng-tech-breakdowns` so other teams know not to plan against the original.

## Common Mistakes

- **Building the signoff table without funnel context.** When an initiative exists, the shepherd has already done team-identification work. Ignoring that produces drift and duplicated signoffs.
- **Over-marking signoffs as Blocking.** Every blocking row is a hard gate. If half the table is blocking, the breakdown won't move to ACCEPTED. Reserve Blocking for teams whose code the change touches or whose contract the change depends on.
- **Under-marking signoffs as Blocking.** Advisory signoffs from teams that own the code being modified produce signoffs that get ignored — and surprises during implementation.
- **Letting signoffs go open without escalation.** A blocking row outstanding for a sprint is a contested interface, not a patience problem. Escalate via the shepherd or EMs.
- **Negotiating cross-team interfaces directly when there's a shepherd.** Cross-team consistency is the shepherd's job. Direct tech-lead-to-tech-lead negotiation undercuts that and produces designs that diverge across teams in the same initiative.
- **Skipping the completion-communication checklist.** Posting on `#team-eng-tech-breakdowns`, contacting QA, and looping in the refinement facilitator are the mechanisms that translate a finished breakdown into actual downstream work. Skipping them produces breakdowns that ship code but never reach the teams that need to know.
- **Editing the signoff table to record a signoff that wasn't actually given.** If a signoff is genuinely contingent ("yes, with these caveats"), capture the caveats in Part 5 as open questions before moving to ACCEPTED. Don't paper over conditional signoffs.

## Reference

- [Tech Breakdown Template](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2920349776) (page `2920349776`) — canonical. Fetch via `get_confluence_page` for the full Part 3 table format and the completion-communication checklist.
- Related: `Skill(writing-tech-breakdowns)` — the engineering content of the breakdown and the canonical state machine. `Skill(navigating-the-initiative-funnel)` — load-bearing when the breakdown sits under a BW Initiative; provides the shepherd, affected-teams list, and escalation paths used throughout this skill. `Skill(architecting-solutions)` (in the `bitwarden-tech-lead` plugin) — the architectural-judgment lens for evaluating contested cross-team interfaces during signoff.
