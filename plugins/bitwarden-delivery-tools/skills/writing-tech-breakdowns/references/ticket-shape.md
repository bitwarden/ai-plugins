# Ticket Shape (reference)

The template's Ticket Shape appendix describes what each Jira story carved from a breakdown's Tasks section carries. It is a reference, not a fill-in section of the breakdown itself.

Each ticket carries:

- A deep link to the relevant breakdown section.
- One or two paragraphs of story-specific tech context not duplicated from the breakdown.
- Acceptance criteria (story-specific, observable outcomes) in Given/When/Then.
- Test scenarios that aren't obvious from the standard unit/integration baseline.
- Implementation pointers — file paths, patterns, dependencies on other tickets.
- Issue links to blockers, dependencies, and sibling-team tickets.

Field mapping (which Jira field receives which piece) and link-type guidance live in `references/jira-story-mechanics.md`. Treat that as the operating reference when creating or updating tickets.

Tickets **don't** restate the breakdown's architectural decisions. If an architectural decision affects a story, the ticket points at the breakdown section that contains it. This keeps cross-cutting decisions in one place and prevents drift.
