---
name: championing-a-strategy-idea
description: Primary-Owner playbook for shepherding a Technical Strategy Idea through Architecture's pre-funnel evaluation into the Software Initiative Funnel.
when_to_use: Use when driving a specific TSI as its named Primary Owner. Triggers — "I think Bitwarden should…", "I'm Primary Owner on ARCH-…", "running the Adoption Retrospective". Not for peer-reviewer or portfolio work (use `curating-the-strategy-ideas-backlog`).
allowed-tools: Skill, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_remote_links, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_issues, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence_cql
---

Primary-Owner playbook for shepherding a [Technical Strategy Idea](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2344517656) (TSI) through Architecture's pre-funnel evaluation. Spans filing the ARCH idea, pairing with a peer reviewer, completing the Stakeholder & Engagement Map (with Known Friction Points), presenting at Architecture Council, navigating quarterly prioritization, and running the Adoption Retrospective at Implementation handoff. Time horizon: driven by the quarterly review cadence, not a fixed clock.

For the Peer Reviewer / portfolio-curator side use `Skill(curating-the-strategy-ideas-backlog)`; for the team-tech-lead-as-contributor framing (filing well, driving passes to a Staff+ owner) use `Skill(contributing-to-technical-strategy)` in `bitwarden-tech-lead`.

## The Shepherding Model

Per the TSI page, every idea in active status has two Architecture-side roles assigned:

- **Primary Owner.** Drives the idea through the pipeline. Writes the problem statement, conducts research, presents at Architecture Council, shepherds the transition to the funnel. Accountable for progress. **This is you when invoking this skill.**
- **Peer Reviewer.** A second Architecture engineer who acts as a sounding board, stays informed on the idea's progress, and provides a constructive challenge function. Not a co-owner — their job is asking the hard questions, catching cross-initiative conflicts, and ensuring stakeholder engagement is thorough.

The pairing matters. The TSI page is explicit: "No single engineer should carry more than two active reviewer assignments at a time, primary or peer." If you are taking on a Primary Owner role and already have two active assignments, surface that — overloaded review defeats its purpose and stalls ideas you've nominally taken on but can't actually drive.

## The Arc: From Thesis to Funnel Intake

Roughly:

1. **Capture.** File the ARCH idea with a lightweight first pass — Problem / Opportunity Statement, Strategic Alignment, rough RICE, theme, customer segments, roadmap placement.
2. **Pair.** Get a peer reviewer assigned. Begin sharing progress with them at the biweekly architecture working session.
3. **Sharpen with peer review.** Together complete the **Stakeholder & Engagement Map** before the idea moves from Backlog to Research. This is the gate.
4. **Research.** Refine the Problem Statement, run stakeholder conversations using the engagement approaches you committed to, surface findings.
5. **Present at Architecture Council.** The peer reviewer attends as informed ally.
6. **Earn intake at quarterly prioritization.** Engineering leadership decides whether this idea enters the funnel — and on what roadmap timing.
7. **Transition to the funnel.** Create the BW Initiative, link it back to the ARCH idea, update statuses, and hand off to `Skill(shepherding-an-initiative)` for the funnel arc.

After implementation completes on the funnel side, you and the peer reviewer run an **Adoption Retrospective** focused on influence effectiveness. That comes back here, not to the funnel skills — see the bottom of this skill.

## Filing the Idea (Capture)

The TSI template lives in JPD under the `ARCH` project. The most-load-bearing sections for the Primary Owner are:

- **Problem / Opportunity Statement.** Be specific about current state, pain, and opportunity. The TSI page's example bar: "Five different error handling patterns exist across clients, causing debugging difficulty and user confusion" — not "Error handling is inconsistent." Quantify wherever possible.
- **Strategic Alignment.** Which OKRs, themes, or architectural principles does this support? Which other initiatives does it depend on or enable?
- **Proposed Direction.** Conceptual approach only. Don't design the solution — that comes during funnel Research. Build vs. buy vs. integrate at the rough level.
- **Operational & Quality Considerations.** Key metrics / SLIs, performance constraints, testability, self-hosted vs. cloud, compliance touchpoints.
- **Validation Approach.** What a minimal PoC would look like, success signals, assumptions to test.
- **Rough Sizing.** T-shirt, expected duration, complexity factors.
- **RICE.** Honest. Confidence is what it is — inflating it produces a backlog that lies. The TSI page's RICE scoring page documents the rubric.

You can file with `Skill(contributing-to-technical-strategy)` in `bitwarden-tech-lead` as a reference for template mechanics. That skill is the contributor-side framing; everything past filing — pairing, mapping, sharpening, presenting, prioritizing — is this skill's territory.

## The Stakeholder & Engagement Map (the Research Gate)

The single highest-leverage thing this skill does well. Per the TSI page, ideas do not advance from Backlog to Research without a complete map, jointly completed by Primary Owner and Peer Reviewer. The map has five fields:

- **Decision makers.** Specific people or roles — not just team names — and the aspect each has authority over. "VP Engineering for resource allocation; SRE Lead for operational ownership."
- **Must consult.** People with expertise or context that will _materially affect direction_. Input sought during Research, not after. Distinguishing must-consult from must-inform is what stops ideas from being shaped in a vacuum.
- **Must inform.** People affected by the outcome who need to stay aware. They shouldn't be surprised when the initiative reaches them.
- **Known friction points.** Where disagreement, resistance, or competing priorities will come from. Honest. Named. _Before_ Research starts. The TSI page is explicit: "Naming friction upfront is how good ideas avoid becoming technically sound proposals that stall at adoption." This is the field where Primary Owners are most tempted to soften. Resist.
- **Engagement approach.** How each group will be engaged. The TSI page lists the menu: 1:1 conversations, RFC-style Confluence review, Architecture Council presentation, attending a team sprint review, async Confluence review. Match the approach to the stakeholder's communication style and the sensitivity of the topic.

Two questions the Peer Reviewer should be pushing on, and you should be pushing yourself on first:

- **Have we named the friction we already know about?** "We expect resistance from Team X because Y" is a more credible idea than one that presents only the upside.
- **Is the engagement approach honest about influence?** If the map says "RFC for Platform team" but you actually need a 1:1 with the Platform tech lead before the RFC has any chance of getting reviewed, name that.

The map is also a living document. As Research surfaces new stakeholders or friction, update it. The Adoption Retrospective at the end of the arc will ask whether the map was accurate — write it to be checkable later.

## Refining Through Research (Pre-Funnel)

The TSI Research phase is lighter than the funnel's Research phase — you are _not_ yet producing an Architectural Assessment. You are sharpening understanding enough that the idea is ready to be presented and prioritized.

- **Refine the Problem / Opportunity Statement.** Update as evidence accumulates. The version that goes to Architecture Council should be sharper than the version that was filed.
- **Run the engagement approaches you committed to.** 1:1s, RFC reviews, attending team sprint reviews. Each conversation usually surfaces something the map didn't predict — update the map.
- **Share progress with the peer reviewer** at the biweekly architecture working session. The Peer Reviewer's job here is to ask the questions you've stopped asking yourself.
- **Update RICE.** As Confidence sharpens, the score should change. An honest dropping Confidence often signals "needs PoC before commitment" — which is fine; that's what Research, then PoC, are for.

## Presenting at Architecture Council

When the idea is ready — map complete, problem statement sharp, friction acknowledged, engagement approach validated by some early conversations — bring it to Architecture Council.

- **The Peer Reviewer attends as informed ally.** They can help field questions and support the discussion. The TSI page notes that "the Architecture group aligns internally before the session through their biweekly working session" — use that.
- **Format the presentation around the thesis.** Lead with the problem and the strategic alignment, not with a proposed solution. The Council's job is to validate that this idea deserves resources, not to design it.
- **Bring the friction with you.** Council will ask. Better to lead with the honest version than to be drawn out by questioning.
- **Take the input seriously.** If Council surfaces a cross-initiative conflict or a stakeholder you hadn't mapped, that goes back into the map.

What Architecture Council provides at this stage: cross-initiative awareness, validation of strategic alignment, surface concerns about timing or conflict, sometimes a recommendation about engagement approach.

What it does not provide: a green light independent of the engineering-leadership prioritization that follows. The Council recommends; leadership prioritizes; both inform whether the idea earns funnel intake.

## Earning Funnel Intake at Quarterly Prioritization

Per the [Architecture / Engineering Operating Model](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/1286963201), Architecture brings prioritized ideas to engineering leadership quarterly (60 minutes, deep review) with monthly lightweight updates (15–20 min) in between.

Your job leading into the quarterly review:

- **Make sure the idea is on the agenda.** Architecture decides which ideas to present; coordinate with the Architecture group lead in the biweekly working session.
- **Be prepared to present a Now / Next / Later case.** The Operating Model uses these lanes. Where do you think this idea belongs? Why? What changes if it slips a quarter?
- **Be honest about the resource ask.** If approved, who shepherds it (you or someone else)? Which teams are likely affected? What's the rough timeline?
- **Bring the friction forward.** Leadership is more likely to commit to an idea that names where disagreement will arise than to one that hides it.

If approved, the idea transitions to the funnel at Phase 1 Identification. Per the TSI page and [Idea-Based Initiatives](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2785181779):

- A new **BW Initiative** is created in the BW project under Jira.
- A **work-item link** is established from the BW initiative back to the ARCH idea — the foundational traceability link.
- A **shepherd is assigned** (often you; sometimes a different Staff+ engineer with the right domain expertise — surface preference, don't assume).
- A **peer reviewer is assigned** for the funnel arc (often the same peer reviewer, sometimes rotated for breadth).
- The **Stakeholder & Engagement Map** is finalized if not already complete.
- The **ARCH idea status** is updated to "1️⃣ Identification" in JPD.

From here, hand off to `Skill(shepherding-an-initiative)` for the umbrella playbook of the funnel arc. The arc you've just driven becomes the upstream context for that work.

## When the Idea Is Declined or Held

Per the TSI page, decline reasons are recorded explicitly:

- Not aligned with strategy.
- Insufficient value (cost > benefit, even after considering different approaches).
- Better handled elsewhere (team-level work, product processes, other channels).
- Timing (external factors, dependencies).
- Superseded by a related idea or existing initiative.
- Resolved through other means.

Document the rationale on the idea in JPD before moving it to Declined. The institutional memory matters — six months later, someone may surface the same pattern and benefit from knowing what was concluded.

Held ideas are different from declined. If timing is wrong but the thesis remains valid, push for "Later" rather than Declined and revisit at the next quarterly review.

## The Adoption Retrospective (After Implementation Handoff)

This is the conclusion of the championing arc and it lives here, not in the funnel skills. Per the TSI page, when the initiative reaches Implementation and begins its [Work Transition Playbook](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2521038855) handoff, the Primary Owner and Peer Reviewer run a brief retrospective focused on **influence effectiveness** — not delivery mechanics.

Four questions, all about how Architecture used its influence to land this thesis:

- **What engagement approaches worked to gain adoption?** Which 1:1s shifted positions? Which RFC reviews actually moved the work? Which Council presentations earned commitment?
- **Where did we lack mandate, and how did we navigate it?** Architecture doesn't have authority to assign work to teams; the engagement approaches are how influence substitutes for mandate. When that substitution worked — and when it didn't — informs the next idea.
- **Where did we discover disagreements late that should have been surfaced earlier?** This is the post-mortem on the Stakeholder & Engagement Map's "Known Friction Points" field. Friction we surfaced early is friction we navigated. Friction we discovered during Implementation is friction the map missed.
- **What would we do differently on the next initiative?** Practical, transferable lessons.

The TSI page directs that findings are "shared in the Architecture working session and captured as a comment on the original idea for institutional memory." Both venues matter — the working session improves Architecture's collective practice; the comment ensures the next person who finds this idea has the retrospective context.

This is distinct from the funnel's end-of-Implementation retrospective in `Skill(coordinating-implementation-across-teams)` — that one is shepherd + receiving tech leads, focused on execution. The Adoption Retrospective is Architecture-internal (Primary Owner + Peer Reviewer), focused on influence.

## Common Mistakes

- **Filing the idea, then drifting.** Filing isn't championing. Take the Primary Owner assignment seriously: pair, map, present, prioritize. Otherwise the idea stalls in Backlog.
- **Soft-pedaling Known Friction Points.** The map is where ideas become credible or stay theoretical. The Peer Reviewer's job is to push on this; if you find yourself softening their pushback, that's signal.
- **Treating Architecture Council as a gate to pass.** Council is input. Bring real questions, not a pitch. Most strong ideas come out of Council with shape changes.
- **Skipping the Adoption Retrospective.** The funnel retrospective covers delivery; this one covers influence. Without it, Architecture's collective practice doesn't get better at the thing it most needs to be good at.
- **Overloading the Peer Reviewer.** TSI page rule: no more than two active reviewer assignments per Architecture engineer. If your reviewer is overloaded, their challenge function decays. Surface it.
- **Pre-scoping during championing.** The Proposed Direction is conceptual. Detailed solution design is funnel Research's job, not yours yet. Premature scoping closes options the Council might have opened.

## Reference

- [Technical Strategy Ideas](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2344517656) — canonical TSI template, Shepherding Model (Primary Owner / Peer Reviewer), Stakeholder & Engagement Map, Adoption Retrospective.
- [Idea-Based Initiatives](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2785181779) — how an approved ARCH idea becomes a BW Initiative at Phase 1 of the funnel.
- [Architecture / Engineering Operating Model](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/1286963201) — the quarterly prioritization review and Now/Next/Later portfolio that decides which ideas enter the funnel.
- [Software Initiative Funnel](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/584515614) — where approved ideas go (Identification onward).
- [Architecture Council](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/751698031) — the venue you present to during championing and again during funnel Research/PoC.
- Related: `Skill(curating-the-strategy-ideas-backlog)` for the Peer-Reviewer / portfolio-curator side of the same Shepherding Model; `Skill(shepherding-an-initiative)` for what happens once your idea earns funnel intake; `Skill(contributing-to-technical-strategy)` (in `bitwarden-tech-lead`) for the team-tech-lead-as-contributor side of filing.
