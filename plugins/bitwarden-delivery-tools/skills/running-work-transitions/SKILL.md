---
name: running-work-transitions
description: Six-phase playbook for running ownership transitions in either direction — receiving work from another team (initiative handoffs from shepherds, frameworks from Platform, operational responsibilities from SRE), or originating a transition (handing off a built framework, transitioning a shepherded initiative, or moving operational responsibilities). Applies Bitwarden's Work Transition Playbook from whichever side a team is on. Use when a team is about to take on or hand off transferred work, when preparing materials or sessions, when the support period is underway, or when running a pulse check or retrospective on a handoff.
allowed-tools: Skill, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page
---

Bitwarden uses a [Work Transition Playbook](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2521038855) to move ownership of logic, patterns, tooling, or processes between teams. The most common trigger is Phase 4 → 5 of an initiative: a shepherd has finished Scoping & Commitment and a team is about to own implementation. But the playbook is general — Platform might hand a framework to a product team, SRE might hand over a runbook, another product team might transfer an integration they no longer own. Same playbook applies in any direction.

This skill covers both sides of a transition. It complements `Skill(navigating-the-initiative-funnel)`, which covers the funnel mechanics more broadly.

## What "Transition" Actually Means

Read this line from the playbook and make sure both teams act on it: **a successful transition is not the moment documentation is shared or a meeting is held — it is the moment the receiving team is confidently operating independently with the transferred work**.

Everything in the six phases below is in service of that outcome. Sessions, documentation, and pulse checks are instruments, not the goal.

## Which Side?

- **Receiving side.** Another team is handing work over. The receiving team is typically represented by a named primary point of contact (the playbook calls this out explicitly — "typically a tech lead or senior engineer"). The job is to evaluate what's being handed over, prepare the team to absorb it, and make the support period efficient.
- **Originating side.** A team is handing work to another team. This is the case when a team built a framework or pattern intended for adoption by other teams, when it has shepherded a smaller-scope initiative through to implementation by another team, or when operational responsibilities are shifting. The job is to prepare materials that make the receiving team self-sufficient and to support — not lead — once they've taken over.

The phases are the same on both sides; the responsibilities differ. Read both sections when participants will be on both sides at different points in the same effort (common when shepherding a single-team-adjacent initiative).

## The Six Phases, From the Receiving Side

### Phase 1 — Preparation

Before any transition session is scheduled, the originating team prepares materials. The receiving team's job is to evaluate those materials before accepting the transition.

Things to confirm:

- **Documentation is adequate.** A competent engineer on the receiving team should be able to take the docs and work with the material independently. If the docs are thin, push back — don't accept a transition the team can't sustain.
- **Jira is legible.** Epics have descriptive summaries. Stories exist at a level of detail the receiving team can refine further — not so specific that the team is handed a pre-written sprint plan, not so vague that the team has to re-research the scope.
- **Stakeholders and points of contact are identified.** The receiving team knows who from the originating side carries context that may be needed during the support period. The receiving team also knows which adjacent stakeholders (leadership, PMs, other teams) will care about progress.
- **A named primary POC is in place on the receiving side** (usually the tech lead, sometimes a senior engineer). The EM is aware and supportive.
- **Post-handoff effort is evaluated honestly.** Transitions that only plan for "adopting the new thing" underestimate the true cost. Evaluate three axes explicitly:
  - **Implementation and integration.** What effort is required to put the transferred work into practice in the receiving team's domain? Adapting patterns, wiring integrations, writing tests, updating workflows.
  - **Phasing out old processes and code.** If the new work replaces something that already exists, decommissioning that thing is its own scope. The receiving team usually has the deepest knowledge of what the old approach actually does in practice — use it.
  - **Ongoing maintenance and bug fixes.** Once the support period ends, who owns what? For most transitions, the receiving team owns everything it adopted. For shared frameworks or libraries, the originating team may retain some maintenance — confirm explicitly where the ownership boundary sits.

If any of those are unclear, name it now. The preparation phase is where gaps are cheapest to fill.

### Phase 2 — Transition Sessions

At least two sessions, spaced 1–2 weeks apart. The receiving team's job is to show up prepared and come back with sharper questions the second time.

- **Session 1 (context and approach).** Review the documentation before the session — ideally a few business days in advance. In the session: understand the problem being solved, why this approach was chosen, walk the PoC or framework, understand how the work fits into the broader initiative. Open Q&A. This session is mostly listening.
- **Session 2 (hands-on and planning).** By now the receiving team should have spent time with the code or tooling. Bring the questions that only emerge from reading the actual implementation. Discuss how the team will integrate, extend, or schedule the work. Surface gaps in the documentation. Agree on what the support period looks like.

Additional sessions are warranted for complex or high-stakes transitions. Both sides decide at the end of Session 2 whether more are needed.

### Phase 3 — Support Period

After the sessions, the originating team stays available — but shifts from leading to supporting. Typical duration: 4–8 weeks, proportional to complexity.

What to use the originating team for:

- Approach questions, intent, and edge cases that documentation doesn't cover.
- Early-PR alignment review — they catch misalignment with the intended pattern while it's cheap to correct.
- Evaluating options if a production reality suggests the original approach needs adjustment.

What not to use them for:

- Gatekeeping the receiving team's work. They're advisors, not approvers.
- Doing the work for the receiving team. A transition is a transfer, not a loaner.

A critical framing from the playbook: **a completed transition does not mean the receiving team will begin work immediately**. The transferred work competes with the team's existing priorities — product roadmap commitments, other initiatives, bugs, tech debt. A delay between handoff and active work is normal and expected.

**What is not normal:** the originating team quietly resuming the work because the receiving team hasn't prioritized it. That's a leadership conversation — between both teams and engineering leadership — not a workaround. The funnel's Scoping & Commitment phase is where executive capacity is allocated; if that commitment isn't translating into prioritized work, escalate rather than let the originating team fill the gap.

### Phase 4 — Pulse Check (~30 days after transition)

A 15–30 minute conversation, or an async thread. This is the load-bearing checkpoint — it's where "we handed it off" gets prevented from becoming "it was never picked up."

Questions to cover:

- Has the receiving team begun working with the transferred material? If not, what's blocking the team?
- Are there unanswered questions, or areas where documentation proved insufficient?
- Is the team comfortable with the approach, or working around it in ways that suggest a mismatch?
- Does the support period need adjustment — extended or shortened?

If the team hasn't started at all, escalate — not punitively. Understand whether it's capacity, priority conflict, or a real gap in the transition. Unaddressed, this is where initiative work dies.

### Phase 5 — Retrospective (~90 days after transition)

A real meeting, 45–60 minutes, with both teams. Goals: assess adoption, give feedback on the transition process, capture lessons for future transitions.

Topics:

- **Adoption assessment.** Is the work being used as intended? Has the receiving team extended it? Are there areas of drift or non-adoption?
- **Transition process feedback.** What worked? What was missing from documentation, sessions, or support period? What would have made it smoother?
- **Lessons for future transitions.** What should change about the playbook itself?
- **Remaining gaps.** Outstanding issues, additional documentation needed, further support required.

Document findings. If the retrospective surfaces process improvements, push them back into the playbook — Bitwarden's transitions get better when teams add what they learned.

### Phase 6 — Closure

The transition is complete when:

- The receiving team is operating independently with the transferred work.
- The support period has concluded (or been explicitly ended early by mutual agreement).
- The retrospective has been conducted and findings documented.
- Outstanding action items have owners and timelines.

At closure, formally acknowledge the transition is complete. Both teams need the signal: the receiving team is autonomous, the originating team is no longer on the hook unless explicitly re-engaged.

## The Six Phases, From the Originating Side

### Phase 1 — Preparation

The originating team prepares the materials the receiving team will rely on. The bar isn't "everything anyone knows is written down somewhere" — it's "a competent engineer on the receiving team could pick this up and work with it independently."

What to produce:

- **Technical documentation** explaining the approach, patterns, and key decisions. Reference existing ADRs, architecture plans, and PoC pull requests rather than duplicating them — but verify the references are current and accessible.
- **A clear description of what is being transferred and what the expected end state looks like for the receiving team.** Don't make them reverse-engineer scope from a pile of artifacts.
- **Known limitations, edge cases, and trade-offs deliberately made.** These are the highest-value things to write down because they're the hardest to reconstruct later. Anything that would surprise a careful reader belongs here.
- **Jira organization.** Epics with descriptive summaries that explain scope and expected outcomes for the receiving team's area. Stories at a level the receiving team can refine — not pre-written sprint plans, not vague placeholders. Link PoC PRs, ADRs, and supporting docs from epic descriptions.
- **A stakeholder map.** On the originating side: who shaped the approach (shepherd, Architecture Council reviewers, subject-matter experts) and what context they carry. Stakeholders with an interest in progression (engineering leadership, dependent PMs, adjacent teams). Make those people aware the transition is occurring and keep them in the loop through pulse check and retrospective.

Then **evaluate post-handoff effort honestly with the receiving team** — not for them. The playbook calls out three axes the originating side is well-positioned to estimate from PoC experience, but the receiving team must validate against the reality of their own systems:

- **Implementation and integration** in the receiving team's domain.
- **Phasing out old processes and code** the new work replaces — often where hidden cost lives.
- **Ongoing maintenance ownership** after the support period. Default: the receiving team owns everything it adopts. For shared frameworks, the originating team may retain some maintenance — confirm explicitly where the boundary sits.

Surfacing these costs during preparation — before the transition sessions — means both teams enter the handoff with realistic expectations. It also helps the receiving team's EM plan capacity rather than discovering mid-sprint that the transition is larger than anticipated.

### Phase 2 — Transition Sessions

The originating team runs the sessions. Two minimum, 1–2 weeks apart.

- **Session 1 (context and approach).** Share materials at least a few business days in advance so the receiving team can review independently. In the session: cover the problem being solved and why this approach was chosen (the why matters as much as the what), walk the PoC or framework, explain how the work fits the broader initiative or strategy, name the constraints and trade-offs, leave room for open Q&A.
- **Session 2 (hands-on and planning).** By now the receiving team has spent time with the code. Expect sharper questions. Address gaps that emerged from their independent review, discuss how they plan to integrate or schedule the work, identify any documentation gaps that need filling, agree on the support-period structure.

Decide together at the end of Session 2 whether additional sessions are warranted. For complex or high-stakes work they often are.

### Phase 3 — Support Period

The originating team shifts from leading to supporting. Typical duration: 4–8 weeks, proportional to complexity. The mental model: **available, not assigned**.

What the originating team does during the support period:

- Be reachable asynchronously — Slack, PR comments — for questions about approach, intent, or edge cases.
- Review 1–2 early PRs from the receiving team for alignment with the intended pattern. **Not as a gatekeeper.** Catch misalignment while it's cheap to correct.
- Help evaluate options if production reality surfaces an issue the original approach didn't anticipate. The receiving team should not be left to guess at intent.
- Communicate openly if the support period needs to be extended or shortened. There is no failure in needing more time.

What the originating team does **not** do:

- Quietly resume the work because the receiving team hasn't prioritized it. The playbook is explicit on this: a delay between handoff and active work is normal. If significant delay emerges, the right response is a priority-alignment conversation between the originating team, the receiving team, and engineering leadership — not a quiet resumption that re-creates the original ownership. The funnel's Scoping & Commitment phase is where executive commitment was established; if that commitment isn't translating into prioritized work, it's a leadership discussion, not a heroism opportunity.
- Gatekeep merges. Detailed code review belongs to the receiving team, just like every other piece of code in their domain.
- Add scope. The transition is a transfer of what was scoped, not an open invitation to extend it.

A practical note on **timing the handoff itself**: if the originating team knows the receiving team won't act on the work for some time, there's a case for deferring the formal sessions until closer to when they're ready, since context decays. But the general guideline is to run the sessions when the work is ready to hand off (context is freshest) and treat the support period as beginning when the receiving team starts active work. If there's a long gap, a brief re-orientation session at the point they pick it up restores context without keeping the originating team continuously engaged.

### Phase 4 — Pulse Check (~30 days after transition)

The originating team participates. Same questions as the receiving side — has work begun, are documents sufficient, is the support period sized right, is the team working around the approach in ways that suggest a mismatch.

If the pulse check reveals work hasn't been picked up at all, this is the moment to escalate jointly with the receiving team — not punitively, but to understand whether there's a capacity issue, priority conflict, or a gap in the transition itself. Unaddressed, this is where initiative work goes to die.

### Phase 5 — Retrospective (~90 days after transition)

The originating team participates. 45–60 minutes, both teams. Goals: assess adoption, gather feedback on how the transition itself went, capture lessons for future transitions.

The most valuable output from the originating side: honest acknowledgment of what the documentation, sessions, or support failed to cover. Process improvements should feed back into the playbook itself — Bitwarden's transitions get better when teams add what they learned.

### Phase 6 — Closure

The originating team acknowledges the transition is complete and steps back. The signal matters: the receiving team is autonomous, and the originating team's involvement has concluded unless explicitly re-engaged. Don't linger as a "just-in-case" reviewer past closure — that's a soft form of refusing to let go.

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
- Related: `Skill(navigating-the-initiative-funnel)` for the initiative context that often triggers a transition; `Skill(architecting-solutions)` for the architectural judgment to apply when evaluating what's being handed over (in either direction).
