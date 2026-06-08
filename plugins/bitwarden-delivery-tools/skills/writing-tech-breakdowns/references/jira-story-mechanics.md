# Creating and Syncing Jira Stories from a Tech Breakdown's Tasks Section

Load this reference when actually creating or updating the Jira stories that mirror a breakdown's Tasks section. This file covers when stories get created, what each carries (the Ticket Shape), the field-by-field mechanics, the inter-ticket linkages, and the bidirectional-sync rules once the stories exist.

Mechanics-level Jira write operations live in whatever Jira authoring tool the engineer has available — for example, a `jira-manager` skill, a `jira-cli` skill, direct MCP calls against the Atlassian server, or the Jira UI. This skill is intentionally read-only at the MCP layer; write capability is delegated.

## Two valid timings for story creation

The parent SKILL.md offers two valid timings; the team picks based on how it refines. Either way, by `Accepted` the stories must exist and the bidirectional link between breakdown and Jira must be in place.

- **Create stories at Proposed entry** (default for ticket-refinement teams). Stories carry the rough Ticket Shape; refinement runs on the Jira tickets themselves, with AC, scope tightening, and dependencies folded into the stories. The breakdown's Tasks section and the stories are a synchronized pair from this point on; refinement edits land on both. This is the right choice for teams whose refinement ritual is ticket-shaped (story-pointing, AC discussion on the ticket, etc.).
- **Defer story creation to the Accepted gate** (for teams who prefer to refine on the breakdown). Refinement runs on the Tasks section in the breakdown PR (Owner, Affected files, Blocked on, Depends on, plus AC folded into the Tasks subsection as refinement progresses). At the `Proposed → Accepted` transition, the refined Tasks are mechanically converted to Jira stories. This keeps the backlog clean of provisional work and the breakdown PR as the atomic record of refinement decisions.

If the team deferred to the Accepted gate, the conversion is mostly copy-paste from the refined Tasks section into the right Jira fields below — refinement has folded AC, scope adjustments, and dependencies back into the breakdown by then. Update the Tasks section with story IDs and confirm the bidirectional link as the last step before flipping status.

## Ticket Shape

Each story carved from a Tasks row carries:

- A deep link to the relevant breakdown section.
- One or two paragraphs of story-specific tech context not duplicated from the breakdown.
- Acceptance criteria (story-specific, observable outcomes) in Given/When/Then.
- Test scenarios that aren't obvious from the standard unit/integration baseline.
- Implementation pointers — file paths, patterns, dependencies on other tickets.
- Issue links to blockers, dependencies, and sibling-team tickets.

Tickets **don't** restate the breakdown's architectural decisions. If an architectural decision affects a story, the ticket points at the breakdown section that contains it. This keeps cross-cutting decisions in one place and prevents drift.

## Field mapping

Putting Ticket Shape content into the right Jira fields matters — sprint teams, refinement, QA, and reporting all key off specific fields, and the wrong field placement (especially folding acceptance criteria into the description) makes the story invisible to those workflows.

| Ticket Shape content                  | Jira field                                                  | Notes                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| ------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Task title                            | **Summary**                                                 | The Tasks-section task title, trimmed for ticket length. When the task applies to only one part of the stack, prefix the Summary with a tag identifying that part (examples: `[Clients]`, `[Web]`, `[Server]`, `[SDK]`, `[iOS]`, `[Android]`). Omit the prefix when the task spans multiple parts.                                                                                                                                                                                                                                                |
| Story-specific tech breakdown         | **Technical breakdown** (custom field, `customfield_10313`) | **Use the dedicated Technical breakdown custom field, not the Description.** Bitwarden's Jira has a purpose-built rich-text field for this content; it supports paragraphs, code blocks, lists, links, and inline cards (same expressivity as Description). One or two paragraphs of context specific to this story, plus inline implementation pointers (file paths, patterns, references to specific Plan subsections), code snippets, and any inline test scenarios. Don't re-state architectural decisions from the breakdown — link to them. |
| Breakdown deep link                   | **Description** (top) + **Remote link**                     | Inline link in the Description (so it's visible to anyone reading), plus a Remote/Web link on the issue pointing to the breakdown file in the `bitwarden/tech-breakdowns` repo. The Remote link is what GitHub/Confluence Smartlinks pick up. The Description top is the one place Description still earns its keep on a breakdown-derived ticket — everything else lives in dedicated custom fields.                                                                                                                                             |
| Acceptance criteria (Given/When/Then) | **Acceptance Criteria** (custom field, `customfield_10192`) | Use the dedicated Acceptance Criteria custom field, not the Description. Refinement and QA filter on this field; burying criteria in Description breaks those workflows. If a project doesn't have the custom field, raise the gap rather than collapsing criteria into Description.                                                                                                                                                                                                                                                              |
| Issue Type                            | **Issue Type**                                              | `Story` for most Tasks-section rows; `Task` for non-user-facing implementation work; `Sub-task` only when the story is decomposed below the breakdown's granularity.                                                                                                                                                                                                                                                                                                                                                                              |
| Parent epic                           | **Epic Link** (or **Parent**)                               | The Jira epic the breakdown is shaping. If under a BW Initiative, the initiative epic is typically the grandparent — link to the team's epic, not the initiative.                                                                                                                                                                                                                                                                                                                                                                                 |
| Owner team                            | **Team** (custom field, `customfield_10001`)                | The Tasks-section `Owner` value. Use the project's Team custom field for team attribution.                                                                                                                                                                                                                                                                                                                                                                                                                                                        |

**Why this matters: Description is the wrong place for tech-breakdown content.** The Bitwarden Jira instance has dedicated custom fields for the structured content (Technical breakdown, Acceptance Criteria, Team). Refinement, QA, sprint planning, and reporting key off those fields. Folding story-specific tech breakdown into Description (a common mistake) makes the content invisible to the workflows that depend on it, and creates a second source of truth diverging from the breakdown.

When the stories exist, **update the Tasks section to carry a link to each story or task**. The breakdown points forward to the tickets; each ticket points back at the breakdown's Tasks section via the Description link and Remote link. The bidirectional linkage is what keeps the two artifacts findable from each other later.

## Linkages between tickets

The Tasks section's `Blocked on` and `Depends on` rows are Jira issue links, not Description text. Create them explicitly when the stories are created:

- **Blocked on:** Tasks-section `Blocked on` row → **`is blocked by`** issue link on the target story, pointing back to the prior story. Jira's blocked-by reporting and dependency graphs key off this link type.
- **Depends on:** Tasks-section `Depends on` row → **`depends on`** issue link (or **`relates to`** if the project doesn't have the `depends on` type) to the parallel story whose interface must exist. Use the more specific link type when available — refinement uses it to identify interface-coupled work.
- **Sibling team breakdowns:** if the work has cross-team interfaces with sibling-team tickets (from the Cross-team engagement signoff table's `Associated breakdown` column), add **`relates to`** links between the corresponding stories. This is how cross-team dependency tracking surfaces in initiative-level reporting.
- **Parent / containing work:** the **Epic Link** field (above) is the structural parent; don't duplicate it as an issue link.
- **Breakdown file:** the **Remote link** to the markdown file in `bitwarden/tech-breakdowns` (above) is the canonical pointer back to the design artifact. Don't put the breakdown into an issue link — Remote/Web link is the right surface.

When the Jira authoring tool doesn't expose the exact link type for a given relationship, default to `relates to` and capture the intended semantics in the Description ("Blocks PM-12346 — interface must land before consumer can build"). The downstream refinement pass can refine the link type.

## Keeping Tasks and Jira stories in sync

Once stories exist, the breakdown's Tasks section and the corresponding Jira stories become a synchronized pair. **Any edit to a Task's scope, owner, affected files, or dependencies must be mirrored on the matching Jira story in the same change.** The breakdown remains the architectural source of truth; the Jira story is the sprint-level source of truth (status, assignee, sprint allocation, refinement notes). They diverge silently if not maintained together.

Some practical rules:

- **Trivial edits** (prose tightening, formatting, clarifying wording without changing scope) — update the breakdown only. No Jira sync needed.
- **Substantive edits** (scope change, new acceptance criterion, file-path changes, added/removed dependency, owner change) — update both the Tasks section in the breakdown PR **and** the matching Jira story, using whichever Jira authoring tool is available.
- **Significant edits** (anything a sprint team picking up the story would need to re-evaluate against, especially scope or acceptance-criteria changes) — also post a **summary comment on the Jira story** linking back to the breakdown PR / section and naming what changed and why. This is the traceability trail; without it, the story's history loses the "why."
- **Edits affecting cross-team interfaces** — also trigger the lifecycle rule for material changes to an `Accepted` breakdown. Move the breakdown back to `Proposed` and re-run affected signoffs before merging. The Jira-side sync still happens, but it's downstream of the lifecycle reset.

Sync flows in both directions. If a story is materially re-scoped during refinement or implementation, the breakdown's Tasks section gets a corresponding update in a follow-up PR, with the change noted under "Last substantive update" in the Status block.

## Common mistakes (Jira-side)

- **Editing the Tasks section without syncing Jira.** Once stories exist, the Tasks section and the Jira stories are a synchronized pair. Substantive edits to one must be mirrored on the other in the same change; significant edits also get a summary comment on the Jira story.
- **Folding story-specific content into the Description field.** Use the dedicated custom fields — `Technical breakdown` (`customfield_10313`) for story-specific tech-breakdown content, `Acceptance Criteria` (`customfield_10192`) for Given/When/Then. On a breakdown-derived ticket, Description's only job is to carry the inline link back to the breakdown file.
- **Skipping issue links for Blocked on / Depends on rows.** Tasks-section dependencies become Jira issue links (`is blocked by`, `depends on`), not free-text in Description.
