---
name: writing-tech-breakdowns
description: DEPRECATED — superseded by `starting-breakdown` and `developing-breakdown-spec`. Retained for historical reference only. Drafted engineering work breakdowns following the Bitwarden Tech Breakdown template; covered starting a new tech breakdown, the scope checklist, specification child pages, open questions, and the status lifecycle (IN PLANNING / IN PROGRESS / PROPOSED / ACCEPTED / COMPLETE).
allowed-tools: Skill, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_remote_links, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_issues, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence_cql
---

> **Deprecated.** Superseded by `Skill(starting-breakdown)` and `Skill(developing-breakdown-spec)` (introduced in `bitwarden-delivery-tools` 1.4.0). New breakdowns should use the successor skills; the content below remains as historical reference until later work folds the status lifecycle and remaining sections into successor skills.

Bitwarden's [Tech Breakdown Template](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2920349776) is the standard artifact a team produces before implementation begins on a non-trivial change. It captures the technical design — what's being built, what it touches, what alternatives were considered, what the cross-team impact is — at the level of fidelity another engineer or another team can act on. This skill is the working playbook for drafting the engineering content (Parts 1, 2, 4, 5, 6) and managing the document's status lifecycle. Part 3 (cross-team signoffs) and the completion-communication checklist live in the companion skill `Skill(coordinating-cross-team-breakdown)`.

When the canonical template structure is needed, fetch page `2920349776` via `get_confluence_page`; this document is the operating summary, not the source of truth.

## Who Drafts a Tech Breakdown

The tech lead traditionally owns the breakdown for the team's work, but software engineers contribute heavily to or fully draft sections. Two common ownership patterns:

- **Engineer-led:** an engineer picks up a piece of scope and drafts the breakdown end-to-end, with the tech lead reviewing before it moves to PROPOSED.
- **Tech-lead-led:** the tech lead frames the problem, populates Parts 1 and 2 with the team, and divides Part 4 specification artifacts among engineers.

This skill is written for whoever is at the keyboard. The activities are the same; the review path differs.

## Before You Start: Orient on the Initiative

If the change exists under a larger BW Initiative — an epic the team received from a shepherd through the Software Initiative Funnel — **run `Skill(navigating-the-initiative-funnel)` first**. It surfaces the context that feeds multiple parts of the breakdown:

- The originating initiative epic, its architecture plan, and the PoC PRs the shepherd produced — these are the source material for Parts 1, 2, and 4.
- The shepherd's stated success criteria and constraints — Part 2 questions get answered against these, not against guesses.
- Sibling teams' epics under the same initiative — these populate the "Related breakdowns" link in Part 1 and seed Part 3's signoff table (handled in `Skill(coordinating-cross-team-breakdown)`).
- The shepherd themselves — escalate ambiguous scope or cross-team interface questions to them rather than resolving unilaterally.

If no initiative exists — the work is purely team-scoped — skip this step and note it explicitly in Part 1 ("not part of an active initiative"). A breakdown without an initiative is fine; a breakdown drafted in a vacuum when an initiative exists is not.

## Starting a New Breakdown

The template lives in the team's "Tech Breakdown" folder in Confluence. Setup steps from the template's preamble:

1. **Copy the template** into the team's folder. Don't edit the template page directly.
2. **Switch permissions to view-only** via the lock icon in the upper right. Tech breakdowns are reference artifacts after they're ACCEPTED — they should not be silently re-edited.
3. **Delete the template checklist** at the top once the copy is made.
4. **Fill the header block:** Owner (the human accountable, not a team), Deadline (when the breakdown itself is expected to be done — not when implementation ships), Status (start at `IN PLANNING`).

The header block is metadata that downstream readers — QA, refinement facilitators, other teams — rely on. Don't leave it blank.

## The Status Lifecycle

The template defines six states. Move through them deliberately — status is how cross-team consumers know whether to engage:

- **IN PLANNING** — expected, but not actively being worked on. Use when the breakdown is committed to but the team hasn't started drafting. Don't sit here for long; it's the weakest signal of intent.
- **IN PROGRESS** — actively being drafted. Parts 1, 2, and any Part 4 child pages are being filled in. Cross-team review is not yet appropriate.
- **PROPOSED** — ready for review. Parts 1, 2, 4, 5 are complete; Part 3's signoff table identifies who needs to review. **This is the gate to `Skill(coordinating-cross-team-breakdown)`** — once the doc reaches PROPOSED, the work shifts from authoring to coordination.
- **ACCEPTED** — all affected teams have signed off via Part 3. The breakdown is now the agreed-on technical design. The team can begin implementation. Implementation should not begin before this state when cross-team interfaces are involved.
- **COMPLETE** — implementation has shipped and the completion-communication checklist (handled in `Skill(coordinating-cross-team-breakdown)`) has run.
- **REJECTED** — review surfaced incompatibilities or blockers that can't be resolved. The breakdown is preserved as historical record; a new breakdown supersedes it.

Two state-transition rules worth holding in mind:

- **Don't skip PROPOSED.** Moving straight from IN PROGRESS to ACCEPTED hides the cross-team review work and produces signoffs that read like rubber stamps.
- **Don't reopen ACCEPTED for material changes.** If the design needs to change after teams have signed off, either supersede with a new breakdown or push the change back to PROPOSED and re-run the relevant signoffs. Silent edits after ACCEPTED defeat the point of the artifact.

If the lifecycle on the canonical page differs from what's described here, the canonical page wins — fetch it via `get_confluence_page` on page `2920349776`.

## Part 1: The Problem Overview

Three fields. Each is short but load-bearing.

### Feature description and overview

Link the Jira epic or story, the Product feature document, and the design files. Then write one or two paragraphs framing the problem in the team's voice — what's being built, who it's for, why now. **Do not paste the Product spec.** A breakdown is a technical document; the problem section is the bridge from Product intent to engineering work, not a copy of the requirements.

If the Product feature document is incomplete or contradicts what the team has been told, surface it here as an open question (Part 5) rather than guessing. Ambiguous Product intent is the single biggest source of churn in breakdowns.

### Related breakdowns

If this work is part of a larger initiative — almost always when a shepherd is involved — link sibling teams' breakdowns here. Use `Skill(navigating-the-initiative-funnel)` to find them, or ask the shepherd directly. Cross-linking matters: a reader landing on this breakdown should be able to trace back to the initiative and across to peer-team work in two clicks.

For team-scoped work with no parent initiative, write "Not part of an active initiative" rather than leaving the field blank.

### Are there alternative solutions that could accomplish the Product requirements with less effort?

Answer honestly. The point of this field is to force the question — "could we satisfy Product with a smaller change?" — not to produce a long alternatives table. One or two sentences is usually right. If a smaller approach exists and is being rejected, name the reason.

**Distinction from Part 4:** Part 1's alternatives are "could we not build this in this shape at all?" Part 4's per-artifact alternatives are "given we're building this, which designs did we reject for each component?" Don't conflate them.

## Part 2: The Breakdown Scope Checklist

This is the heart of the breakdown — a systematic survey of what the change touches. Each question has a yes/no flavor, but the value is in the follow-ups: when "yes," what's the actual scope, and what does it imply for compatibility, security, and other teams.

Apply architectural judgment as you answer. **Use `Skill(architecting-solutions)` (in the `bitwarden-tech-lead` plugin) as the lens** — blast-radius assessment, dual-data-access parity, V±2 client compatibility, multi-client reality. Don't re-derive those principles here; reach for the skill.

The canonical checklist on page `2920349776` is authoritative. Here is the operating summary:

### Database changes

If yes, list the tables, columns, and indexes affected. Then ask: **will these changes need to be backwards compatible** under Bitwarden's [EDD (Evolutionary Database Design) model](https://contributing.bitwarden.com/contributing/database-migrations/edd)? Self-hosted instances cannot roll back migrations. If the change is backwards-incompatible, the rollout must be phased — make the phasing explicit here.

### API changes

If yes, list the endpoints and contract changes. Then ask:

- **Backwards compatibility** — same constraint as DB: clients in the wild are at varying versions. V±2 client compatibility is the standard lens.
- **Unauthenticated endpoints** — if any new endpoint is unauthenticated, **this requires Architecture Review**. Flag it explicitly and do not treat the breakdown as PROPOSED-ready until Architecture is in the loop.

### UI components

What components are touched, added, or changed? Then:

- **Shared team-owned components.** If shared components change, consider splitting those changes into their own tasks/PRs so they can be verified and tested independently. Re-testing all shared use cases together is the failure mode.
- **Component Library (base) changes.** If a base component is being modified, alert the Design System team and discuss whether they can support the work by Product/Design's timeline. If they can't, request their approval for the API/UI changes the team will make.
- **New components** — list them. For each, ask whether it's a candidate for the Component Library. If yes, alert the Design System team and discuss how to shape the component's API for future Component Library extraction.

### SDK changes

If the work touches the SDK, ask all four:

- Changes to public FFI-exposed APIs?
- Changes to public SDK internal APIs?
- Changes to team-internal SDK internal APIs?
- Opportunity to **move existing logic to the SDK** — this is the question most often skipped. If TypeScript logic could live in the SDK and be shared across clients, the breakdown is the right place to surface it.

### Services touched

List the services. If touching pre-existing TypeScript services, **ask whether the work should include migrating to a high-level SDK method** rather than extending the TypeScript service. Don't extend without weighing this — it's how SDK adoption stalls.

### Hosting

Is this feature supported on Self-Hosted, Cloud, or both? Self-hosted has constraints (no rollback for DB migrations, longer upgrade lag, no centralized infrastructure to lean on) that change the design.

### Feature flagging

Will this feature be feature-flagged, or live on a long-lived feature branch? If flagged, where is the flag enforced — server-side, client-side, both? Which UI surfaces and services are gated by it? Long-lived feature branches are usually a smell; surface them so the team can decide whether the change is really shaped right.

### Security considerations

Answer all three:

- **Cryptographic work** — does it need internal review, external review, or a security proof? If unsure, treat as needing internal review; route through `Skill(bitwarden-security-context)` (in the `bitwarden-security-engineer` plugin).
- **Existing security definitions** — are there ones in this area? Can new ones be built? `Skill(threat-modeling)` (in the `bitwarden-security-engineer` plugin) is the source for definition format.
- **Breaking changes** — will any existing security definitions be invalidated by this work? If yes, the breakdown is incomplete until Security Engineering is consulted.

### Testing considerations

What testing is required beyond the standard unit/integration coverage? Cross-platform tests, performance tests, security tests, load tests, manual QA flows. Note who runs each — the team, QA, security, another team.

### Technical debt considerations

What tech debt could be paid off opportunistically while this work is in progress? Be selective — pulling unrelated cleanup into the scope is how breakdowns balloon. The right answer is often "none, but document candidates for future work."

### Developer-environment differences

Does the solution need different behavior in developer environments — different defaults, mock backends, separate config? Note them so the team isn't surprised when local-vs-prod parity breaks.

## Part 4: Specification Artifacts

Larger breakdowns produce one or more child pages — specification documents that go deeper than the breakdown can. Each child page covers one major component or decision area: an API contract, a data schema, a UI component API, a cryptographic scheme.

Link each artifact in Part 4's table. For each, verify before the breakdown moves to PROPOSED:

- **The public interface is defined.** API contracts, data schemas, component APIs are spelled out at the level another team or engineer can code against.
- **Key behaviors and edge cases are covered.** Use Part 2's checklist as the lens — if the artifact touches DB, API, UI, SDK, hosting, the corresponding considerations show up in the spec.
- **Alternatives considered are listed.** For each significant design decision, name the alternatives and why they were rejected. This is Part 4's alternatives section — different from Part 1's "could we not build this at all."
- **The artifact has been reviewed by affected teams** from Part 3's cross-team table. This is the bridge into `Skill(coordinating-cross-team-breakdown)` — Part 4 child pages often need their own per-team review before the parent breakdown can move to ACCEPTED.

If the breakdown is small enough that no child pages are needed, say so explicitly: "Specification is contained in Part 2 above; no separate artifacts required." Don't leave Part 4 silently empty.

## Part 5: Open Questions

Track every unresolved question with an owner and (ideally) a target resolution date. Open questions are not a sign of an incomplete breakdown — they're the explicit acknowledgment of what the team doesn't yet know. Hidden assumptions are the failure mode; tracked questions are healthy.

Move questions to closed (or delete them, with the resolution captured in Parts 1–4 as appropriate) as they're answered. A breakdown shouldn't reach ACCEPTED with material questions still open — if a question is blocking, treat it as a blocker and don't move to PROPOSED.

## Part 6: AI Context

This block exists for Claude (and future engineers using Claude) coming back to the breakdown later. Populate it explicitly:

- **What this page is.** One sentence: the breakdown for `<feature>`, owned by `<team>`, currently at `<status>`.
- **What to read first.** The linked Jira epic, the originating initiative (if any), the architecture plan section, the PoC PRs, the Product spec.
- **What to read next.** Part 4 child pages relevant to the task at hand.
- **Known sharp edges.** Anything an engineer or AI assistant should know that isn't obvious from reading the doc top-to-bottom — assumed prior context, deliberately unfinished sections, known wrong information awaiting update.

A populated AI Context block is what makes the breakdown useful in future Claude conversations. Skipping it is a tax on every future read.

## When You Move to PROPOSED

Once Parts 1, 2, 4, and 5 are complete and the team has reviewed internally, set status to `PROPOSED`. Then **invoke `Skill(coordinating-cross-team-breakdown)`** — the work shifts from authoring (this skill) to cross-team coordination (the companion skill). The companion skill owns:

- Building or populating the Part 3 signoff table.
- Walking the cross-team checklist (mobile changes, components outside the team's domain, dependencies on other teams' services, APIs built for other teams).
- Chasing signoffs to move from PROPOSED to ACCEPTED.
- Running the completion-communication checklist before the breakdown moves to COMPLETE.

The state machine lives in this skill; the cross-team workflow lives in the companion. They compose by cross-reference, not auto-invocation.

## Common Mistakes

- **Drafting in a vacuum.** Initiative context — the shepherd, sibling teams' epics, the architecture plan — is the input that makes Parts 1 and 3 correct. Skipping `Skill(navigating-the-initiative-funnel)` when an initiative exists is the most common upstream error.
- **Pasting Product spec into Part 1.** The breakdown is a technical document. Link the spec; don't reproduce it.
- **Treating Part 2 as a yes/no checklist.** The value is in the follow-ups. "Yes, DB changes" with no scope and no compatibility analysis is no better than skipping the question.
- **Skipping Part 4 alternatives.** "We picked this design" without "we considered and rejected these" is a breakdown that hides its own decisions. Future readers — and reviewers in Part 3 — need the alternatives to assess the choice.
- **Leaving Part 6 empty.** The AI Context block is cheap to populate while drafting and expensive to reconstruct later.
- **Moving to ACCEPTED without all Part 3 signoffs.** The whole point of the state is that affected teams have signed off. Treating it ceremonially produces breakdowns that nobody trusts.
- **Editing an ACCEPTED breakdown silently.** If the design needs to change materially, supersede or move back to PROPOSED — don't quietly revise.

## Reference

- [Tech Breakdown Template](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2920349776) (page `2920349776`) — canonical. Fetch via `get_confluence_page` for the full template, the literal field labels, and the latest status definitions.
- [EDD — Evolutionary Database Design](https://contributing.bitwarden.com/contributing/database-migrations/edd) — referenced in Part 2 for DB-change backwards compatibility.
- Related: `Skill(navigating-the-initiative-funnel)` — load-bearing when the breakdown sits under a BW Initiative; provides the shepherd, sibling-team, and architecture-plan context that feeds Parts 1, 2, 3. `Skill(coordinating-cross-team-breakdown)` — Part 3 signoffs, cross-team checklist, and the completion-communication workflow that closes the breakdown. `Skill(architecting-solutions)` (in the `bitwarden-tech-lead` plugin) — the architectural-judgment lens to apply through Part 2.
