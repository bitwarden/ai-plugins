---
name: writing-tech-breakdowns
description: Draft engineering work breakdowns following the Bitwarden Tech Breakdown template. Use when starting a new tech breakdown, filling in the scope checklist, drafting specification child pages, capturing open questions, or moving the doc between status states (IN PLANNING / IN PROGRESS / PROPOSED / ACCEPTED / COMPLETE).
allowed-tools: Skill, Read, Edit, Write, Bash, Glob, Grep, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_remote_links, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_issues, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence_cql
---

Bitwarden's Tech Breakdown is the standard artifact a team produces before implementation begins on a non-trivial change. It captures the technical design (what's being built, what it touches, what alternatives were considered, what the cross-team impact is) at the level of fidelity another engineer or another team can act on. This skill is the working playbook for drafting the engineering content (Specification, Clarifications Log, Plan, Tasks, Agent Context) and managing the document's status lifecycle. Cross-team engagement and the completion-communication checklist live in the companion skill `Skill(coordinating-cross-team-breakdown)`.

## Canonical source

The canonical template lives in the [`bitwarden/tech-breakdowns`](https://github.com/bitwarden/tech-breakdowns) repo at `templates/tech-breakdown.md`. Each breakdown is a self-contained markdown file checked into that repo under the owning team's folder. The single-artifact format is deliberate: AI agents start cold and cannot reassemble context spread across linked pages and tickets, so the whole architectural picture lives in one document.

Read `templates/tech-breakdown.md` directly when you need literal headings, checklists, or field labels; this skill is the operating summary, not the source of truth. If the repo isn't cloned locally, clone `bitwarden/tech-breakdowns` or fetch the template path through `gh` before starting.

## Before You Start: Orient on the Initiative

If the change exists under a larger BW Initiative (an epic the team received from a shepherd through the Software Initiative Funnel), **run `Skill(navigating-the-initiative-funnel)` first**. It surfaces the context that feeds multiple parts of the breakdown:

- The originating initiative epic, its architecture plan, and the PoC PRs the shepherd produced — these are the source material for Specification and Plan.
- The shepherd's stated success criteria and constraints — Plan questions get answered against these, not against guesses.
- Sibling teams' epics under the same initiative — these seed the Cross-team engagement section (handled in `Skill(coordinating-cross-team-breakdown)`).
- The shepherd themselves — escalate ambiguous scope or cross-team interface questions to them rather than resolving unilaterally.

If no initiative exists (the work is purely team-scoped) skip this step and note it explicitly in Specification ("not part of an active initiative"). A breakdown without an initiative is fine; a breakdown drafted in a vacuum when an initiative exists is not.

## Before You Start: Check for Collisions in the Same Codebase

Before drafting, **scan for other in-flight work touching the same repos, modules, or files**. Two teams shaping overlapping changes in the same domain produces wasted design effort at best and merge-conflict-driven rework at worst. The check is cheap; the cost of skipping it is high.

Run this scan in two places, against the affected repos you'll list in Agent Context's "Repos affected":

1. **In-flight tech breakdowns from other teams.** Search the `bitwarden/tech-breakdowns` repo across all teams' folders (not just your own; exclude `**/complete/**`). Look for breakdowns whose Agent Context names the same repos, Plan subsections discuss the same modules, or Tasks-section `Affected files` overlap with yours. A simple `grep -ri <repo-name> bitwarden/tech-breakdowns/` (excluding `complete/`) is a reasonable first pass; refine with file-path searches once you've identified candidates.
2. **Open PRs in the affected repos.** For each repo on your "Repos affected" list, run `gh pr list -R bitwarden/<repo> --state open --json number,title,headRefName,files` (or equivalent) and look for PRs touching the same paths your breakdown's Tasks section will. Long-lived feature branches and renovate/refactor PRs are the common collision sources.

When a collision is found:

- **Link the colliding work** in the Cross-team engagement section's `Coordination notes` (other team's breakdown) or in the Plan's `Current State` (open PR). Future readers should be able to see the overlap from the breakdown itself.
- **Contact the owning team on their public Slack channel** (tag the named human if known) to align on sequencing, scope boundary, or whether the work should merge into a single breakdown. Don't draft in parallel and discover the conflict at signoff time.
- **Add the affected team to the signoff table** (handled in `Skill(coordinating-cross-team-breakdown)`) if their work overlaps with yours enough that they need to evaluate your design. Treat overlap as a signoff trigger, not just a coordination note.
- **Capture unresolved overlap as a Clarifications Log entry** if alignment can't be reached quickly. Don't move to `Proposed` with an unresolved collision in the same domain.

Re-run this scan when status flips to `Proposed`. New work can appear in the gap between starting and circulating; a colliding PR that opened mid-draft is exactly the kind of surprise that derails cross-team review.

## Starting a New Breakdown

The breakdown is a markdown file in the `bitwarden/tech-breakdowns` repo. Setup steps from the template's preamble:

1. **Copy the template** at `templates/tech-breakdown.md` into the team's folder (`<team>/`). Don't edit the template itself.
2. **Rename the file** to include the Jira key (epic, task, or story) plus a short human-readable slug (for example, `<team>/PM-12345-pin-protected-key-envelope.md`).
3. **Delete the template checklist** at the top once the file is in place.
4. **Fill the Status block:**
   - `Status:` — start at `In Planning`.
   - `Last substantive update:` — today's date + a one-line note ("initial draft").
   - `Active owner / contact:` — the specific human to ping for clarifications, not a team.
5. **Open a PR** to the `tech-breakdowns` repo. CODEOWNERS routes review to the owning team. The PR is how status transitions happen; "Last substantive update" gets bumped on every PR that changes content.

The Status block is metadata that downstream readers (QA, refinement facilitators, other teams) rely on. Don't leave fields blank.

## The Status Lifecycle

The template defines six states. Move through them deliberately — status is how cross-team consumers know whether to engage:

- **In Planning** — expected, but not actively being worked on. Use when the breakdown is committed to but the team hasn't started drafting.
- **In Progress** — actively being drafted. Specification, Plan, and supporting sections are being filled in. Cross-team review is not yet appropriate. Intra-team discussion may occur at this stage to flesh out questions.
- **Proposed** — ready for review. Specification, Plan, Tasks, Agent Context are complete; the Cross-team engagement signoff table identifies who needs to review. **Two parallel streams of review run during this state**: cross-team signoff (handled in `Skill(coordinating-cross-team-breakdown)`) and the team's own refinement pass on the Tasks decomposition. Both must complete before the breakdown can move to `Accepted`. Loop the team's refinement facilitator in immediately when status flips to `Proposed`; refinement feedback that surfaces missing or wrong-shaped tasks goes back into the Tasks section in the same PR cycle, in parallel with cross-team signoff iteration.
- **Accepted** — two gates have closed: **(a)** all affected teams have signed off in the Cross-team engagement table, **and (b)** the team has completed a refinement pass on the Tasks section, with refinement feedback folded back into the breakdown and the Tasks decomposition understood and accepted by the implementing team. Both gates are required — cross-team signoff without team refinement produces tasks that look fine externally but get re-litigated in sprint planning; team refinement without signoff produces a design the rest of the org hasn't agreed to. The stakeholder-communication checklist (signoff verification, cross-team channel post, QA contact, Jira story creation from the Tasks section, refinement-facilitator handoff for scheduling) also runs on the same transition. The breakdown is now the agreed-on technical design. Implementation can begin. Implementation should not begin before this state when cross-team interfaces are involved.
- **Complete** — implementation has shipped. The file is moved to `<team>/complete/` on the same PR that flips status to `Complete`.
- **Rejected** — review surfaced incompatibilities or blockers that can't be resolved. The breakdown is preserved as historical record; a new breakdown supersedes it.

Two state-transition rules worth holding in mind:

- **Don't skip Proposed.** Moving straight from In Progress to Accepted hides the cross-team review work and produces signoffs that read like rubber stamps.
- **Don't reopen Accepted for material changes.** If the design needs to change after teams have signed off, either supersede with a new breakdown or push the change back to Proposed and re-run the relevant signoffs. Silent edits after Accepted defeat the point of the artifact. CODEOWNERS review on each PR is the enforcement mechanism.

Files under `**/complete/**` are point-in-time records, not source of truth. Treat them as historical and don't edit them except to correct factual errors.

## Specification

The WHAT and WHY. After reading this section a reader should know what is being built, who benefits, and what success looks like, without yet knowing how it will be built.

### Description

Two or three sentences. Concrete enough that someone unfamiliar with the project can picture the end state. Link the Jira epic, the Product feature document, and design files. **Do not paste the Product spec** — the breakdown is a technical document, and the description is the bridge from Product intent to engineering work.

If the Product feature document is incomplete or contradicts what the team has been told, surface it in the Clarifications Log rather than guessing. Ambiguous Product intent is the single biggest source of churn.

### User Value

Why this matters, stated in observable terms. What changes for the customer, the business, or the engineering org once this ships. Avoid internal milestones; describe the outcome a stakeholder could verify.

### Functional Requirements

A bullet list of what this initiative or epic produces. Each bullet is a deliverable, not a task. Tasks live in the Tasks section; this is the contract with stakeholders.

### Alternatives

For each rejected alternative: one paragraph naming the option, why it was rejected, and the trade-off the rejection accepts. This is the single best defense against re-litigation later. Don't conflate with per-layer alternatives in Plan — Specification alternatives are "could we satisfy Product with a smaller change?", while Plan alternatives are "given we're building this, which designs did we reject for each component?"

### Success Criteria

Written at the breakdown level. Per-ticket acceptance criteria live on the ticket and don't duplicate these.

## Clarifications Log

A persistent record of clarifying questions raised about this breakdown and how each was answered.

**Run an AI clarify pass against the draft before requesting cross-team review.** Spec Kit's `/speckit.clarify`, Claude, or equivalent. The output of that pass folds back into Specification or Plan as decisions, not into the log. What lands in the log is the residue: questions that needed a human stakeholder (PM, legal, security, a peer team) and the answers they gave.

The log is a table with five columns: Status (Open / Resolved), Question, Raised by, Owner, Resolution.

- **Open** entries carry an owner and a target resolution date. A breakdown can ship to `Proposed` with Open clarifications so long as owners and targets are clear.
- **Resolved** entries stay in the log as short stubs pointing into Specification or Plan, so future readers can see why a decision was made.
- A breakdown shouldn't reach `Accepted` with material Open questions. Blocking questions are blockers; don't move to Proposed until they're either resolved or owner-assigned with a clear target.

## Plan

The HOW. Plan breaks into four kinds of subsections: Current State, Architecture (with Out of Scope and Known Limitations), Prototypes, and per-technical-layer specs. Apply architectural judgment as you fill these in. **Use `Skill(architecting-solutions)` (in the `bitwarden-tech-lead` plugin) as the lens** — blast-radius assessment, dual-data-access parity, V±2 client compatibility, multi-client reality.

### Current State

What exists today, before the change. File paths, existing types, current behavior, current data shapes. This anchors the proposed change in concrete code so the reader can see what's actually being modified.

### Architecture

The proposed architecture. Headings and structure depend on the work. **Prefer Mermaid source over image-only diagrams** — it's AI-readable, diffs cleanly, and reviewers can suggest edits in text.

Two recommended subsections:

- **Out of Scope** — what this work explicitly does not deliver. Use to short-circuit drift; if a question comes up later, the answer is "out of scope, tracked under X" or "out of scope, not pursued."
- **Known Limitations** — in-scope-but-deferred decisions. Distinct from Out of Scope: these are constraints inside the work being shipped, not exclusions. For each, name the rationale and what follow-up (if any) addresses it.

### Prototypes

Throwaway code, PoCs, and technical investigation done to validate the spec. Sized for shaping, not implementation. Findings feed the per-layer subsections below; if a finding rewrites a layer's plan, the spec is updated and the finding stays here as the audit trail.

### Per-layer subsections

The template enumerates the layers below. Walk each one and either fill in the changes required or state explicitly that the layer isn't touched ("no DB changes"). Don't leave subsections silently empty.

- **Data model changes.** Tables, columns, indexes. Backwards compatibility under [EDD](https://contributing.bitwarden.com/contributing/database-migrations/edd) — self-hosted cannot roll back, so backwards-incompatible changes must phase explicitly. Data migration strategy. EF vs Dapper considered.
- **Server logic and controller changes.** Whether CQRS applies. Concrete handlers, commands, queries.
- **Server API surface changes.** Endpoints and contract changes. Backwards compatibility (V±2 client lens). **Unauthenticated endpoints require Architecture Review** — flag explicitly and treat the breakdown as not Proposed-ready until Architecture is in the loop.
- **`sdk-internal` changes.** Public FFI-exposed API changes. WASM + UNIFFI bindings. New crates (route to [Adding functionality to the SDK](https://contributing.bitwarden.com/architecture/sdk/adding-functionality)). **Opportunity to move existing logic to the SDK** — most commonly skipped question; surface it here.
- **Client services changes.** TypeScript services touched. If extending pre-existing TS services, ask whether the work should include migrating to a high-level SDK method instead.
- **Client / UI behavior changes.** Affected components, shared team-owned components, Component Library (base) components. If base components change, alert the Design System team and confirm timeline. New components: candidates for the Component Library? All new/modified components have Storybook stories covering default, loading, error, and edge cases.
- **Background jobs.** New or changed jobs with batch sizing, idempotency, observability notes.
- **Security & cryptography.** Cryptographic work routes through `Skill(bitwarden-security-context)` (in the `bitwarden-security-engineer` plugin); internal vs external review vs security proof. Existing security definitions touched or broken — `Skill(threat-modeling)` is the source for definition format.
- **Deployment & environments.** Self-hosted vs cloud support. Flagging strategy or rationale for not flagging. Where the flag is enforced (server, client, both). Developer-environment differences.
- **Observability & operations.** Logging, metrics, events, alerts. Event log entries this work writes; existing observability that needs to be extended.
- **Testing strategy.** Tests beyond table-stakes unit/integration coverage. Storybook stories are the unit-level test surface for UI; reference them rather than restating their content. Call out test cases for QA that aren't obvious from feature scope.
- **Technical debt.** Debt that could be paid off opportunistically. Be selective — pulling unrelated cleanup into scope is how breakdowns balloon.

## Tasks

Task decomposition is part of the breakdown itself. For each task, include:

- **Task:** title describing the task.
- **Owner:** the team doing the work.
- **Affected files / crates / modules:** concrete paths, not vague areas.
- **Blocked on:** prior tasks or external dependencies that must land first.
- **Depends on:** parallel work whose interface must exist (but not necessarily land first).

Tasks are at the implementation-unit level — what becomes Jira stories. Sequence them by blocking relationships so the team can see the critical path. Don't restate architectural decisions on tasks; the breakdown is the source for cross-cutting decisions and the task carries a pointer.

### Creating Jira stories from Tasks

Jira stories are created at the `Proposed → Accepted` transition, after signoff is captured and before the refinement-facilitator handoff. Each story mirrors one row of the Tasks section and carries the Ticket Shape described below.

Mechanics live in **`Skill(jira-manager)`** (read/write via MCP) or **`Skill(jira-cli)`** (CLI). This skill names _when_ and _what_ to create; those skills know _how_.

#### Field mapping

Putting Ticket Shape content into the right Jira fields matters — sprint teams, refinement, QA, and reporting all key off specific fields, and the wrong field placement (especially folding acceptance criteria into the description) makes the story invisible to those workflows.

| Ticket Shape content                  | Jira field                              | Notes                                                                                                                                                                                                                                                                                              |
| ------------------------------------- | --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Task title                            | **Summary**                             | The Tasks-section task title, trimmed for ticket length. When the task applies to only one part of the stack, prefix the Summary with a tag identifying that part (examples: `[Clients]`, `[Web]`, `[Server]`, `[SDK]`, `[iOS]`, `[Android]`). Omit the prefix when the task spans multiple parts. |
| Story-specific tech breakdown         | **Description** (top)                   | One or two paragraphs of context specific to this story. Don't re-state architectural decisions from the breakdown — link to them.                                                                                                                                                                 |
| Breakdown deep link                   | **Description** (top) + **Remote link** | Inline link in the Description (so it's visible to anyone reading), plus a Remote/Web link on the issue pointing to the breakdown file in the `bitwarden/tech-breakdowns` repo. The Remote link is what GitHub/Confluence Smartlinks pick up.                                                      |
| Implementation pointers               | **Description** (mid)                   | File paths, patterns to follow, and references to specific Plan subsections. From the breakdown's Tasks-section `Affected files / crates / modules`.                                                                                                                                               |
| Test scenarios                        | **Description** (lower)                 | Beyond the standard unit/integration baseline. From Plan's `Testing strategy` subsection where applicable.                                                                                                                                                                                         |
| Acceptance criteria (Given/When/Then) | **Acceptance Criteria** (custom field)  | Use the dedicated Acceptance Criteria custom field, not the Description. Refinement and QA filter on this field; burying criteria in Description breaks those workflows. If a project doesn't have the custom field, raise the gap rather than collapsing criteria into Description.               |
| Issue Type                            | **Issue Type**                          | `Story` for most Tasks-section rows; `Task` for non-user-facing implementation work; `Sub-task` only when the story is decomposed below the breakdown's granularity.                                                                                                                               |
| Parent epic                           | **Epic Link** (or **Parent**)           | The Jira epic the breakdown is shaping. If under a BW Initiative, the initiative epic is typically the grandparent — link to the team's epic, not the initiative.                                                                                                                                  |
| Owner team                            | **Team** (custom field)                 | The Tasks-section `Owner` value. Use the project's Team custom field for team attribution.                                                                                                                                                                                                         |

When the stories exist, **update the Tasks section to carry each story's Jira key inline** (for example, `Task 1: Introduce PinProtectedKeyEnvelope type [PM-12345]`). The breakdown points forward to the tickets; each ticket points back at the breakdown's Tasks section via the Description link and Remote link. The bidirectional linkage is what keeps the two artifacts findable from each other later.

#### Linkages between tickets

The Tasks section's `Blocked on` and `Depends on` rows are Jira issue links, not Description text. Create them explicitly when the stories are created:

- **Blocked on:** Tasks-section `Blocked on` row → **`is blocked by`** issue link on the target story, pointing back to the prior story. Jira's blocked-by reporting and dependency graphs key off this link type.
- **Depends on:** Tasks-section `Depends on` row → **`depends on`** issue link (or **`relates to`** if the project doesn't have the `depends on` type) to the parallel story whose interface must exist. Use the more specific link type when available — refinement uses it to identify interface-coupled work.
- **Sibling team breakdowns:** if the work has cross-team interfaces with sibling-team tickets (from the Cross-team engagement signoff table's `Associated breakdown` column), add **`relates to`** links between the corresponding stories. This is how cross-team dependency tracking surfaces in initiative-level reporting.
- **Parent / containing work:** the **Epic Link** field (above) is the structural parent; don't duplicate it as an issue link.
- **Breakdown file:** the **Remote link** to the markdown file in `bitwarden/tech-breakdowns` (above) is the canonical pointer back to the design artifact. Don't put the breakdown into an issue link — Remote/Web link is the right surface.

When `Skill(jira-manager)` or `Skill(jira-cli)` doesn't expose the exact link type for a given relationship, default to `relates to` and capture the intended semantics in the Description ("Blocks PM-12346 — interface must land before consumer can build"). The downstream refinement pass can refine the link type.

### Keeping Tasks and Jira stories in sync

Once stories exist, the breakdown's Tasks section and the corresponding Jira stories become a synchronized pair. **Any edit to a Task's scope, owner, affected files, or dependencies must be mirrored on the matching Jira story in the same change.** The breakdown remains the architectural source of truth; the Jira story is the sprint-level source of truth (status, assignee, sprint allocation, refinement notes). They diverge silently if not maintained together.

Some practical rules:

- **Trivial edits** (prose tightening, formatting, clarifying wording without changing scope) — update the breakdown only. No Jira sync needed.
- **Substantive edits** (scope change, new acceptance criterion, file-path changes, added/removed dependency, owner change) — update both the Tasks section in the breakdown PR **and** the matching Jira story. Use `Skill(jira-manager)` or `Skill(jira-cli)` for the Jira update.
- **Significant edits** (anything a sprint team picking up the story would need to re-evaluate against, especially scope or acceptance-criteria changes) — also post a **summary comment on the Jira story** linking back to the breakdown PR / section and naming what changed and why. This is the traceability trail; without it, the story's history loses the "why."
- **Edits affecting cross-team interfaces** — also trigger the lifecycle rule for material changes to an `Accepted` breakdown. Move the breakdown back to `Proposed` and re-run affected signoffs before merging. The Jira-side sync still happens, but it's downstream of the lifecycle reset.

Sync flows in both directions. If a story is materially re-scoped during refinement or implementation, the breakdown's Tasks section gets a corresponding update in a follow-up PR, with the change noted under "Last substantive update" in the Status block.

## Agent Context

This section exists for AI assistants working on tickets carved from the breakdown. The breakdown itself is self-contained; Agent Context is pointers to existing code and external references that supplement the inline spec. A populated Agent Context is what makes the breakdown useful in future Claude conversations.

Four required subsections:

- **Repos affected.** List each repo touched with a pointer to its `CLAUDE.md` file (`repo-name/CLAUDE.md`). **Per the repo `CLAUDE.md` convention, each affected repo's `CLAUDE.md` should point agents back to this breakdown** — the linkage is bidirectional.
- **Existing patterns to follow.** Concrete file paths plus what to mirror. Avoid vague references; an agent should be able to navigate from this list directly to the relevant file.
- **External references.** Standards, RFCs, third-party docs, prior ADRs. Each item must be load-bearing for some decision above; if it isn't, leave it out.
- **Things an agent should not assume.** Counter-intuitive constraints, defaults that look obvious but aren't, invariants that an agent might violate by following standard patterns. **This is the highest-leverage section for preventing wrong-shaped AI-generated code.** Treat empty as a smell — at minimum, list "no surprising assumptions identified" rather than leaving the section blank.

## Ticket Shape (reference, not fill-in)

The template's Ticket Shape appendix is a reference, not a section to fill in. Tickets carved from the breakdown carry:

- A deep link to the relevant breakdown section.
- One or two paragraphs of story-specific tech context not duplicated from the breakdown.
- Acceptance criteria (story-specific, observable outcomes) in Given/When/Then.
- Test scenarios that aren't obvious from the standard unit/integration baseline.
- Implementation pointers — file paths, patterns, dependencies on other tickets.
- Issue links to blockers, dependencies, and sibling-team tickets.

Field mapping (which Jira field receives which piece) and link-type guidance live in the **"Creating Jira stories from Tasks → Field mapping"** subsection above. Treat that as the operating reference when creating or updating tickets.

Tickets **don't** restate the breakdown's architectural decisions. If an architectural decision affects a story, the ticket points at the breakdown section that contains it. This keeps cross-cutting decisions in one place and prevents drift.

## When You Move to Proposed

Once Specification, Clarifications Log (any Open items have owners + targets), Plan, Tasks, and Agent Context are complete and the team has reviewed internally, set status to `Proposed` (in the same PR that finalizes the content). Then **invoke `Skill(coordinating-cross-team-breakdown)`** — the work shifts from authoring (this skill) to cross-team coordination (the companion skill). The companion skill owns:

- Building or populating the Cross-team engagement signoff table.
- Walking the cross-team checklist (mobile changes, components outside the team's domain, dependencies on other teams' services, APIs built for other teams).
- Chasing signoffs to move from `Proposed` to `Accepted`.
- Running the stakeholder-communication checklist at the `Accepted` transition (verify signoff, post to `#team-eng-tech-breakdowns`, contact QA, create Jira stories from the Tasks section, hand off Task decomposition to the team's refinement facilitator for scheduling).
- Moving the file to `<team>/complete/` on the PR that flips status to `Complete` after implementation ships.

Engage the team's refinement facilitator yourself while the breakdown is in `Proposed` — get the Task decomposition into a refinement pass alongside the cross-team signoff work.

**Re-run the collision scan** from "Before You Start: Check for Collisions in the Same Codebase" at this point. New breakdowns and PRs can appear in the gap between starting the draft and circulating for review; surfacing them at `Proposed` is materially cheaper than discovering them during signoff or implementation.

For Jira ticket mechanics (creation, updates, sync, summary comments on significant edits), route through `Skill(jira-manager)` or `Skill(jira-cli)`. This skill names the timing and shape; those skills do the writes. See "Keeping Tasks and Jira stories in sync" above for the bidirectional-sync rules once stories exist.

The state machine lives in this skill; the cross-team workflow lives in the companion. They compose by cross-reference, not auto-invocation.

## Common Mistakes

- **Drafting a "Part 4 child page" out of habit.** The new format is a single self-contained file. Per-layer specs are subsections inside Plan, not separate pages. Drafting child pages re-fragments the artifact the format is designed to prevent.
- **Drafting in a vacuum.** Initiative context (shepherd, sibling teams' epics, architecture plan) is the input that makes Specification and Cross-team engagement correct. Skipping `Skill(navigating-the-initiative-funnel)` when an initiative exists is the most common upstream error.
- **Skipping the collision scan.** Other teams may be shaping changes in the same codebase right now. A breakdown drafted without checking in-flight breakdowns and open PRs in the affected repos discovers the conflict at signoff or merge time, when both designs are far harder to reshape. Run the scan before drafting and again at the `Proposed` transition.
- **Pasting Product spec into Specification.** The breakdown is a technical document. Link the spec; don't reproduce it.
- **Treating Plan's per-layer subsections as yes/no checklists.** The value is in the follow-ups. "Yes, DB changes" with no scope and no compatibility analysis is no better than skipping the question.
- **Skipping the AI clarify pass before circulating.** Running clarify after cross-team review surfaces questions the team should have answered first; running it before means cross-team review focuses on real interface concerns.
- **Leaving "Things an agent should not assume" empty.** This section is cheap to populate while drafting and very expensive to reconstruct later. Empty is a smell.
- **Moving to Accepted with only one gate closed.** `Accepted` requires both cross-team signoff and the team's own refinement pass on the Tasks section. Moving forward with just signoffs (and no team refinement) produces work that gets re-litigated in sprint planning; moving forward with just refinement (and no signoffs) produces a design the rest of the org hasn't agreed to. Treating either gate ceremonially produces breakdowns nobody trusts.
- **Editing a Complete breakdown.** Files under `**/complete/**` are historical. Material new work gets a new breakdown.
- **Editing the Tasks section without syncing Jira.** Once stories exist, the Tasks section and the Jira stories are a synchronized pair. Substantive edits to one must be mirrored on the other in the same change; significant edits also get a summary comment on the Jira story. Silent drift between the two leaves sprint teams working off stale acceptance criteria or wrong file paths.
- **Folding acceptance criteria into the Description field.** Acceptance criteria belong in the dedicated Acceptance Criteria custom field. Refinement and QA filter on that field; criteria buried in Description are invisible to those workflows. The Description carries the story-specific tech breakdown, implementation pointers, test scenarios, and the breakdown deep link — not the criteria.
- **Skipping issue links for Blocked on / Depends on rows.** Tasks-section dependencies become Jira issue links (`is blocked by`, `depends on`), not free-text in Description. Without the links, Jira's dependency graphs and refinement views can't see the work order; sprint teams pick up stories that aren't actually unblocked yet.

## Reference

- [`bitwarden/tech-breakdowns`](https://github.com/bitwarden/tech-breakdowns) — the breakdowns repo. Template at `templates/tech-breakdown.md`. Each team's in-flight work is under `<team>/`; completed work is under `<team>/complete/`.
- [EDD — Evolutionary Database Design](https://contributing.bitwarden.com/contributing/database-migrations/edd) — referenced in Plan for DB-change backwards compatibility.
- [Adding functionality to the SDK](https://contributing.bitwarden.com/architecture/sdk/adding-functionality) — referenced in Plan for new SDK crates.
- Related: `Skill(navigating-the-initiative-funnel)` — load-bearing when the breakdown sits under a BW Initiative; provides shepherd, sibling-team, and architecture-plan context that feeds Specification, Plan, and Cross-team engagement. `Skill(coordinating-cross-team-breakdown)` — the Cross-team engagement table, cross-team checklist, and completion-communication workflow that closes the breakdown. `Skill(architecting-solutions)` (in the `bitwarden-tech-lead` plugin) — the architectural-judgment lens to apply through Plan.
