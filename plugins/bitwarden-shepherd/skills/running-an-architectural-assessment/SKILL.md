---
name: running-an-architectural-assessment
description: Phase 2 (Research) deep-dive playbook — drafts the Architectural Assessment.
when_to_use: Use when an initiative has cleared Phase 1 Identification and the shepherd is producing the Architectural Assessment for Architecture Council. Triggers — "starting Research phase", "drafting the Architectural Assessment", "comparing solution options". Not for PoC (use `running-a-proof-of-concept`).
allowed-tools: Skill, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_remote_links, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_issues, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence_cql
---

Phase 2 (Research) deep-dive playbook for an initiative shepherd. Deliverable: an **Architectural Assessment** — a Confluence page in the EN-space assessments folder that captures the refined problem statement, current state, 2–4 evaluated solution options, and a recommendation with rationale. Time budget: 3–5 weeks, 40–80 hours of shepherd time. Splits into Part A (~weeks 1–2) understanding the problem, Part B (~weeks 3–5) finding the right direction.

## Part A: Understanding the Problem (~Weeks 1–2)

### Stakeholder Interviews

Interview **3–5 people** affected by or knowledgeable about the problem. Cast wider when the initiative spans many teams or hits operational systems; cast narrower when it's a clear technical question.

Who to talk to:

- Tech leads on the teams whose codebases will change.
- Engineers who have hit the problem repeatedly and have working models of it (even if not the tech lead).
- SRE, BRE, DbOps, AppSec, or QA leads when the problem touches their domain.
- Anyone who attempted a related approach before — even if it failed. Especially if it failed.

What to ask:

- "Walk me through how this problem shows up for your team in practice."
- "What workarounds exist today?"
- "What attempts were made before and why did they not stick?"
- "If we did nothing here for another quarter, what changes?"
- "What constraints — technical, organizational, timing — would shape a solution?"

What to document:

- Each interviewee's perspective in their own framing (paraphrase but keep their language).
- Quantified pain wherever possible. "~3 bugs per quarter," "~4 hours per sprint lost to this," "incident on 2026-02-14 traced to this." Vague pain produces vague proposals.
- Constraints, especially the implicit ones — security commitments, V+/-2 compatibility, self-hosted, multi-client parity.
- Disagreements between interviewees. They are signal, not noise.

### Current-State Analysis

Survey existing implementations across the codebase. The shape of the survey depends on the initiative — error handling, observability, auth, data access, build/test tooling. Look for:

- **Inconsistencies.** Five teams solving the same problem five ways. Two services with diverged versions of a shared pattern.
- **Workarounds.** Code that exists only because the desired pattern doesn't. Comments referencing tickets that were never resolved.
- **Technical debt.** Old patterns left in place because rewriting wasn't worth the cost — but the cost of leaving them is now bigger than the rewrite.
- **Impact.** Where possible, attach numbers: bug frequency in the area, performance metrics, on-call pages tied to the area, time spent in code review on this kind of code.

### Historical Context

- Read past PRs, design docs, and Slack threads on the topic. Search Confluence for prior assessments in the same problem space.
- Find earlier shepherds, EMs, or engineers who pushed related work. Brief conversations save weeks of rediscovery.
- Identify why previous approaches did or did not stick. The reasons usually inform what will succeed this time.

## Part B: Finding the Right Direction (~Weeks 3–4)

### Solution Research

Research patterns from industry, comparable codebases, and Bitwarden's own prior art. The goal at this stage is **breadth, then trade-offs** — not depth into the favorite.

- Identify **2–4 candidate approaches**. Fewer than 2 means you skipped the comparison; more than 4 usually means you haven't classified them well.
- For each approach, document trade-offs explicitly: complexity, migration cost, performance, security posture, operational implications, self-hosted impact, V+/-2 compatibility, who builds the framework, who adopts it.
- Pair up with current or past shepherds whose initiatives are adjacent. Sharing findings catches dependencies and conflicts early.
- Bring `Skill(architecting-solutions)` from `bitwarden-tech-lead` into play when the trade-offs are inside one team's codebase — that skill carries the team-scope architectural judgment heuristics.

Be honest about the leading candidate but write the assessment as if any of the 2–4 might win. If you only document one approach seriously, leadership and Architecture Council can't actually make the decision — they're rubber-stamping yours.

### The Architectural Assessment Document

Place under the EN-space assessments folder (the funnel doc links the canonical location). Follow the "Architectural Assessments" template; the sections below are the ones the funnel page specifies.

- **Problem statement (refined from research).** The version you can write now that you couldn't have written at Identification.
- **Current state analysis.** Inconsistencies, workarounds, quantified impact. Reference specific code or ticket evidence.
- **Solution options considered (2–4).** For each: a brief description, key trade-offs, rough effort estimate, risks. Don't write a full proposal for each — a clear-eyed comparison is what's needed.
- **Recommended approach.** Pick one. The funnel doc is explicit that this is what leadership decides on; equivocating defeats the purpose of the assessment.
- **Rationale.** Why this option, not the others. Tie back to the constraints surfaced in interviews and the impact in current-state analysis.
- **Loose high-level effort estimate.** Reference past initiatives where helpful. T-shirt size or weeks-of-shepherd-plus-weeks-of-team is sufficient.
- **Risks and open questions.** What could invalidate the recommendation. What needs PoC to answer.

Strong examples from the funnel doc:

> **Problem:** "Inconsistent state management across web vault, browser extension, and desktop app causes sync bugs"
> **Solutions evaluated:** RxJS observables, Redux Toolkit, Zustand, custom event system
> **Recommendation:** Redux Toolkit with clear migration path
> **Rationale:** TypeScript support, dev tools, team familiarity, gradual adoption path
> **Next step:** Prove it works in browser extension settings module

Weak patterns to avoid (also from the funnel doc):

- "We should use GraphQL because it's modern" — no problem analysis, no alternatives.
- "Smaller services would solve our scaling issues" — no current-state analysis, no trade-off evaluation.

### Socializing the Draft

- Share the draft with the people you interviewed. They will catch misrepresentation of their team's reality faster than anyone else.
- Share with adjacent shepherds. Cross-initiative conflicts are cheapest to surface here.
- For major initiatives, present an **optional preview at Architecture Council** before the formal Phase 3 PoC review. Council input at this stage is shaped guidance, not a gate.
- Refine based on input. The first draft and the version that goes to the decision-makers should not be the same document.

## Exit Criteria

The funnel doc specifies the gate at the end of Phase 2:

- **Deliverable:** Completed Architectural Assessment document with 2–4 solution options and a recommended approach.
- **Decision maker:** Engineering leadership with Architecture Council input.
- **Possible decisions:** Proceed to PoC / Continue Research (extend 1–2 weeks) / Hold (revisit in a future quarter) / Decline.

When you bring the assessment to the decision-makers, you need:

- A 5–10 minute walkthrough that can stand alone — problem, options, recommendation, rationale, risks.
- A clear ask. Almost always "approval to start a PoC validating Option X in area Y."
- Honest acknowledgment of open questions the PoC is meant to answer.

## Updates to the BW Initiative

During Research, update the BW Initiative (see [Idea-Based Initiatives](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2785181779) for the canonical anatomy):

- **Description:** Refine if the problem understanding has shifted materially. Stay at the summary level — the Architectural Assessment is the detailed artifact.
- **"Relates to" links:** This is when the link inventory grows fastest. Every prior attempt, adjacent team's work, existing tooling — link it.
- **Comments:** Use comments to record significant research findings, decision points, and stakeholder feedback that doesn't belong in the assessment but should sit on the initiative timeline.
- **ARCH idea status:** Update to "2️⃣ Research" in JPD.

## Common Mistakes

- **Writing the assessment to justify a predetermined answer.** Leadership can usually tell. The assessment is supposed to be the place where the team's judgment shows up, not where it gets concealed.
- **Skipping quantification.** "This causes pain" is harder to act on than "this caused ~6 sprint-hours of debugging over the last 3 sprints." Get the numbers wherever you can.
- **Not naming what failed before.** If a prior attempt didn't stick, the assessment that doesn't engage with that history will produce a recommendation that doesn't either.
- **Treating Architecture Council as a gate to be passed.** The Council is input. You own the recommendation. Bring real questions, not a pitch.
- **Over-investing in Research.** The PoC is where the approach gets validated in real code. If Research has stretched past 5 weeks, ask whether you're avoiding the PoC because you suspect it will reveal something.

## Reference

- [Software Initiative Funnel](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/584515614) §2 — canonical phase description, entry/exit criteria, examples.
- [Idea-Based Initiatives](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2785181779) — how to update the BW Initiative through Research.
- [Technical Strategy Ideas](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2344517656) — the upstream TSI's Stakeholder & Engagement Map informs which friction points to surface in the assessment.
- Related: `Skill(shepherding-an-initiative)` for the umbrella playbook, `Skill(running-a-proof-of-concept)` for what Research feeds into, `Skill(architecting-solutions)` (in `bitwarden-tech-lead`) for the team-scope architectural judgment heuristics to apply when options live inside one team's domain.
