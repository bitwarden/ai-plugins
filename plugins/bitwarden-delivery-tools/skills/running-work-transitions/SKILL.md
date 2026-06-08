---
name: running-work-transitions
description: Six-phase playbook for ownership transitions in either direction (receiving or originating). Use when a team is about to take on or hand off transferred work — initiative handoffs, framework handoffs, or operational-responsibility moves — when preparing materials or sessions, when the support period is underway, or when running a pulse check or retrospective.
allowed-tools: Skill, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_remote_links, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_issues, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence_cql
---

Bitwarden uses a [Work Transition Playbook](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2521038855) to move ownership of logic, patterns, tooling, or processes between teams. The most common trigger is Phase 4 → 5 of an initiative: a shepherd has finished Scoping & Commitment and a team is about to own implementation. But the playbook is general — Platform might hand a framework to a product team, SRE might hand over a runbook, another product team might transfer an integration they no longer own. Same playbook applies in any direction.

This skill covers both sides of a transition. It complements `Skill(navigating-the-initiative-funnel)`, which covers the funnel mechanics more broadly.

## What "Transition" Actually Means

Read this line from the playbook and make sure both teams act on it: **a successful transition is not the moment documentation is shared or a meeting is held — it is the moment the receiving team is confidently operating independently with the transferred work**.

Everything in the six phases below is in service of that outcome. Sessions, documentation, and pulse checks are instruments, not the goal.

## Which Side?

- **Receiving side.** Another team is handing work over. The receiving team is typically represented by a named primary point of contact ("typically a tech lead or senior engineer"). The job is to evaluate what's being handed over, prepare the team to absorb it, and make the support period efficient.
- **Originating side.** A team is handing work to another team — built a framework or pattern intended for adoption, shepherded a smaller-scope initiative through to implementation by another team, or moved operational responsibilities. The job is to prepare materials that make the receiving team self-sufficient and to support — not lead — once they've taken over.

The phases are the same on both sides; the responsibilities differ. The walkthrough below uses **From the originating side** and **From the receiving side** callouts within each phase. Read both when participants will be on both sides at different points in the same effort (common when shepherding a single-team-adjacent initiative).

## The Six Phases

### Phase 1 — Preparation

The originating team prepares materials before any session is scheduled; the receiving team evaluates those materials before accepting the transition. The bar isn't "everything anyone knows is written down somewhere" — it's "a competent engineer on the receiving team could pick this up and work with it independently."

**From the originating side — produce:**

- **Technical documentation** explaining the approach, patterns, and key decisions. Reference existing ADRs, architecture plans, and PoC pull requests rather than duplicating them — but verify references are current and accessible.
- **A clear description of what is being transferred and what the expected end state looks like.** Don't make the receiving team reverse-engineer scope from a pile of artifacts.
- **Known limitations, edge cases, and trade-offs deliberately made.** Highest-value things to write down because they're the hardest to reconstruct later.
- **Jira organization.** Epics with descriptive summaries that explain scope and expected outcomes. Stories at a level the receiving team can refine — not pre-written sprint plans, not vague placeholders. Link PoC PRs, ADRs, and supporting docs from epic descriptions.
- **A stakeholder map.** Who shaped the approach (shepherd, Architecture Council reviewers, SMEs) and what context they carry. Stakeholders with an interest in progression (engineering leadership, dependent PMs, adjacent teams) — make them aware the transition is occurring and keep them looped through pulse check and retrospective.

**From the receiving side — confirm:**

- **Documentation is adequate.** If the docs are thin, push back — don't accept a transition the team can't sustain.
- **Jira is legible** at a level the team can refine further — not a pre-written sprint plan, not so vague the team has to re-research the scope.
- **Stakeholders and points of contact are identified** on the originating side and among adjacent stakeholders who'll care about progress.
- **A named primary POC is in place on the receiving side** (usually the tech lead, sometimes a senior engineer). The EM is aware and supportive.

**Both sides — evaluate post-handoff effort honestly** along three axes (originating estimates from PoC experience; receiving validates against the reality of their own systems):

- **Implementation and integration** in the receiving team's domain — adapting patterns, wiring integrations, writing tests, updating workflows.
- **Phasing out old processes and code** the new work replaces. The receiving team usually has the deepest knowledge of what the old approach actually does in practice — use it.
- **Ongoing maintenance and bug fixes** after the support period. Default: the receiving team owns everything it adopts. For shared frameworks, the originating team may retain some maintenance — confirm explicitly where the boundary sits.

Surfacing these costs during preparation — before sessions — means both teams enter the handoff with realistic expectations and the receiving team's EM can plan capacity rather than discovering mid-sprint that the transition is larger than anticipated.

### Phase 2 — Transition Sessions

At least two sessions, spaced 1–2 weeks apart. The originating team runs them; the receiving team shows up prepared and comes back with sharper questions the second time.

- **Session 1 (context and approach).** Share materials at least a few business days in advance. In the session: the problem being solved, why this approach was chosen (the why matters as much as the what), walk the PoC or framework, how the work fits the broader initiative, constraints and trade-offs, open Q&A. Mostly listening for the receiving side.
- **Session 2 (hands-on and planning).** The receiving team has now spent time with the code or tooling — bring the questions that only emerge from reading the actual implementation. Discuss how the team will integrate, extend, or schedule the work. Surface documentation gaps. Agree on what the support period looks like.

Both sides decide at the end of Session 2 whether additional sessions are warranted. Complex or high-stakes transitions often warrant them.

### Phase 3 — Support Period

The originating team shifts from leading to supporting. Typical duration: 4–8 weeks, proportional to complexity. The mental model: **available, not assigned**.

**From the originating side:**

- Be reachable asynchronously (Slack, PR comments) for questions about approach, intent, or edge cases.
- Review 1–2 early PRs from the receiving team for alignment with the intended pattern. **Not as a gatekeeper.** Catch misalignment while it's cheap to correct.
- Help evaluate options if production reality surfaces an issue the original approach didn't anticipate. The receiving team shouldn't be left to guess at intent.
- Communicate openly if the support period needs to be extended or shortened. There's no failure in needing more time.

**What the originating team does _not_ do:**

- Quietly resume the work because the receiving team hasn't prioritized it.
- Gatekeep merges. Detailed code review belongs to the receiving team.
- Add scope. The transition is a transfer of what was scoped, not an invitation to extend it.

**From the receiving side — use the originating team for:**

- Approach questions, intent, and edge cases that documentation doesn't cover.
- Early-PR alignment review.
- Evaluating options if a production reality suggests the original approach needs adjustment.

**Don't use them for** gatekeeping the team's work (advisors, not approvers) or doing the work for the team (a transition is a transfer, not a loaner).

A critical framing from the playbook: **a completed transition does not mean the receiving team will begin work immediately**. The transferred work competes with existing priorities — product roadmap commitments, other initiatives, bugs, tech debt. A delay between handoff and active work is normal.

**What is not normal:** the originating team quietly resuming the work because the receiving team hasn't prioritized it. That's a leadership conversation — between both teams and engineering leadership — not a workaround. The funnel's Scoping & Commitment phase is where executive capacity is allocated; if that commitment isn't translating into prioritized work, escalate rather than let the originating team fill the gap.

A practical note on **timing the handoff**: if the originating team knows the receiving team won't act on the work for some time, there's a case for deferring formal sessions until closer to when they're ready, since context decays. But the general guideline is to run sessions when the work is ready to hand off (context is freshest) and treat the support period as beginning when the receiving team starts active work. If there's a long gap, a brief re-orientation session at the point they pick it up restores context without keeping the originating team continuously engaged.

### Phase 4 — Pulse Check (~30 days after transition)

A 15–30 minute conversation, or an async thread, with both sides participating. This is the load-bearing checkpoint — it's where "we handed it off" gets prevented from becoming "it was never picked up."

Questions to cover:

- Has the receiving team begun working with the transferred material? If not, what's blocking the team?
- Are there unanswered questions, or areas where documentation proved insufficient?
- Is the team comfortable with the approach, or working around it in ways that suggest a mismatch?
- Does the support period need adjustment — extended or shortened?

If the team hasn't started at all, escalate jointly — not punitively. Understand whether it's capacity, priority conflict, or a real gap in the transition. Unaddressed, this is where initiative work dies.

### Phase 5 — Retrospective (~90 days after transition)

A real meeting, 45–60 minutes, with both teams. Goals: assess adoption, give feedback on the transition process, capture lessons for future transitions.

Topics:

- **Adoption assessment.** Is the work being used as intended? Has the receiving team extended it? Are there areas of drift or non-adoption?
- **Transition process feedback.** What worked? What was missing from documentation, sessions, or support period? What would have made it smoother?
- **Lessons for future transitions.** What should change about the playbook itself?
- **Remaining gaps.** Outstanding issues, additional documentation needed, further support required.

Document findings. The most valuable output from the originating side is honest acknowledgment of what the documentation, sessions, or support failed to cover — process improvements feed back into the playbook itself.

### Phase 6 — Closure

The transition is complete when:

- The receiving team is operating independently with the transferred work.
- The support period has concluded (or been explicitly ended early by mutual agreement).
- The retrospective has been conducted and findings documented.
- Outstanding action items have owners and timelines.

Both teams need the signal: the receiving team is autonomous, and the originating team's involvement has concluded unless explicitly re-engaged. **From the originating side:** don't linger as a "just-in-case" reviewer past closure — that's the soft form of refusing to let go.

## Adapting the Playbook

The six phases describe a general process. Scale them to the work — this applies to both sides:

- **Smaller transitions** (single pattern, limited scope): compress the timeline. The pulse check can be a Slack thread; the retrospective can fold into a regular team retro.
- **Larger transitions** (multi-team, high complexity): expect more than two sessions, a longer support period, a more formal retrospective.
- **Urgent transitions** (departures, reorganizations): compress preparation if necessary, but do not skip the support period or the follow-up checkpoints. That's where most of the value lives.

The one thing that should not be skipped regardless of scale is the **30-day pulse check**. Everything else can be scaled; that one is the mechanism that prevents silent failure.

## Common Mistakes

**From the receiving side:**

- **Accepting a transition with thin documentation.** The receiving team will pay for it during Implementation. Push back during Preparation.
- **Treating sessions as the goal.** Sessions are instruments. If the receiving team isn't operating independently 90 days later, the transition failed regardless of how many sessions were run.
- **Leaving capacity questions unanswered.** "We'll pick it up when we can" is how transitions die. If there's no allocated capacity, that's a leadership conversation before the transition, not after.
- **Quietly working around the transferred approach.** Drift is cheaper to catch in a pulse check than in a production incident. Surface it.
- **Letting the originating team resume the work.** If the receiving team can't prioritize, escalate to leadership. Don't accept help that re-creates the original ownership.

**From the originating side:**

- **Running sessions before documentation is ready.** A session held to compensate for thin docs is a session that just produces a list of follow-ups. Prepare materials first, schedule sessions second.
- **Filling capacity gaps the receiving team should escalate.** If the receiving team isn't prioritizing the work, the right response is a leadership conversation about commitment, not quietly continuing the effort. It will undermine the transfer of ownership.
- **Skipping evaluation of phase-out cost.** The receiving team often knows what the old thing actually does in practice better than the originating team does. Plan the decommissioning explicitly.
- **Treating the support period as continued ownership.** The originating team is an advisor during this phase. Reviews are for alignment, not for approval. Merges are not theirs.
- **Lingering past closure.** "Just keep watching for a while" is the soft form of refusing to let go. The receiving team should know exactly when it's autonomous.
- **Skipping the retrospective.** It's the only mechanism that improves the playbook. If something went poorly, that's the venue to surface it — for the next transition's benefit.

## Reference

- [Work Transition Playbook](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2521038855) — canonical. Fetch via `get_confluence_page` for the full phase-by-phase detail, summary table, and adaptation guidance.
- Related: `Skill(navigating-the-initiative-funnel)` for the initiative context that often triggers a transition; `Skill(choosing-collaboration-model)` for picking a collaboration model when the transition involves cross-team code changes (framework rollout, codebase handoff, operational responsibility move) — different phases of a transition often use different models; `Skill(architecting-solutions)` for the architectural judgment to apply when evaluating what's being handed over (in either direction).
