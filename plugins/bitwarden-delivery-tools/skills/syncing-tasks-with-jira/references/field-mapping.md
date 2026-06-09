# Field Mapping

Load this reference when building a CREATE or UPDATE operation spec in Phase 3 (Execute) — it carries the field-by-field mapping from Tasks-row content to Jira fields, and the issue-link types for Tasks-row dependencies.

The parent SKILL.md keeps the workflow (Triage, Confirm, Execute, Sync back); this file carries the concrete field-name and link-type tables Phase 3 needs.

## Ticket Shape → Jira fields

| Ticket Shape content                              | Jira field                                    | Notes                                                                                                                                                                                                                                               |
| ------------------------------------------------- | --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Task title (with stack-area prefix if applicable) | **Summary**                                   | Prefix with `[Clients]`, `[Web]`, `[Server]`, `[SDK]`, `[iOS]`, `[Android]` when single-stack. Omit when spanning.                                                                                                                                  |
| Task description + inline breakdown link          | **Description**                               | One or two sentences describing what the task does, followed by the inline link back to the breakdown file. Description carries general task framing — it's **not** the place for story-specific tech context (that's `Technical breakdown` below). |
| Story-specific tech context                       | **Technical breakdown** (`customfield_10313`) | Dedicated rich-text Jira field. **Not** Description. One or two paragraphs of architectural / implementation context not duplicated from the breakdown; inline implementation pointers. Don't re-state architectural decisions — link to them.      |
| Acceptance Criteria (Given/When/Then)             | **Acceptance Criteria** (`customfield_10192`) | Dedicated Jira field. **Not** Description. Refinement and QA filter on this. If the project lacks the field, raise the gap rather than collapsing into Description.                                                                                 |
| Owner team                                        | **Team** (`customfield_10001`)                | Tasks-row Owner. Drives sprint allocation and reporting.                                                                                                                                                                                            |
| Breakdown deep link (also)                        | **Remote / Web link**                         | A Remote / Web link on the issue pointing to the breakdown file in `bitwarden/tech-breakdowns`. Picked up by GitHub/Confluence Smartlinks. Complements (does not replace) the inline link inside the Description body.                              |
| Issue Type                                        | **Issue Type**                                | `Story` for user-facing tasks. `Task` for non-user-facing implementation.                                                                                                                                                                           |
| Parent epic                                       | **Epic Link** (or **Parent**)                 | The epic key from the breakdown filename.                                                                                                                                                                                                           |

## Issue link types

| Tasks-row relationship                             | Jira link type                               |
| -------------------------------------------------- | -------------------------------------------- |
| `Blocked on` row → prior Task within the breakdown | `is blocked by`                              |
| `Blocked on` row → external Jira key               | `is blocked by`                              |
| `Depends on` (parallel interface coupling)         | `depends on` if available, else `relates to` |
| Sibling-team breakdown interface                   | `relates to`                                 |

Dependencies live in the link graph, never in Description prose.
