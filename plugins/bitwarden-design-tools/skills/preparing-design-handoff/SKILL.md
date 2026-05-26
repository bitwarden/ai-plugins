---
name: preparing-design-handoff
description: Prepare a Bitwarden design handoff — the Confluence handoff page, the Figma "Ready for Dev" state, and the Jira transitions that go with them.
when_to_use: Use at the end of the In Design phase before engineering picks the work up. Triggers — "prep handoff", "create a handoff page", "what goes in a handoff", "hand this off to engineering", "finish the design phase". Not for Jira-specific state transitions on their own (use `navigating-design-jira-process`); composes that one for the Jira moves and `using-figma` for verifying the Figma file is handoff-ready.
allowed-tools: Skill, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_remote_links, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_issues, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence_cql
---

# Preparing a Design Handoff

This skill grounds handoff prep in Bitwarden's actual handoff page template — the same
structure every recent project handoff page in the Product and Design Confluence space
follows. Engineering relies on that consistency. A handoff missing a section creates downstream
questions and slows the epic into development.

When prepping a real handoff, read at least one recent handoff page from the same engineering
area first via `get_confluence_page` (the Bulk Management handoff is a clean reference point,
ID `387350548`). The full template, with every field's purpose, lives in
`references/handoff-template.md`.

## The handoff is three things, not one

A handoff is finished when all three are in place:

1. **The handoff Confluence page.** Created in the Product and Design space, structured per
   the template. This is the document engineering reads first.
2. **The Figma file in Ready-for-Dev state.** Final designs grouped on a single page, with
   sections named to match the engineering stories that will consume them. Sections marked
   "Ready for Dev" in Figma. Annotated prototype available.
3. **The Jira state aligned.** Design tasks moved to DONE on the design board, the engineering
   epic moved to TODO / READY FOR DEV, and the Figma file linked in the epic's "Design"
   section. The full Jira choreography is in `navigating-design-jira-process`.

If any of the three is missing, the handoff isn't done — even if the page exists.

## Prep checklist (before writing the page)

- The product initiative or PRD page exists and is current.
- The engineering epic exists in Jira and the designer is or has been assigned to it.
- Designs have been through critique at 30%, 60%, and 90% and the 90% review has been
  addressed.
- Real-user testing has happened where applicable (this is what 90% is for).
- The Figma file's final-designs page is curated — no scratch pages, no unused frames in the
  Ready-for-Dev surface.

If any item is missing, surface that before drafting the page — handoff is not the moment to
discover the 90% review never happened.

## The template, at the section level

(See `references/handoff-template.md` for each field's purpose, expected content, and the
common gotchas.)

- **Product Initiative Confluence Page.** Link to the PRD-equivalent.
- **Design Confluence Page.** Self-link (current page).
- **Link to Development Epics.** Engineering epic(s) in Jira.
- **Designer.** The assigned designer (mention the user, don't just type the name).
- **Design Status.** `DESIGN DONE` once handoff is real.
- **Product Initiative.** Repeat the link to the initiative document at the section level.
- **Background.** Brief project purpose, goals, and the solution shape — enough for someone
  picking the epic up cold to understand the _why_.
- **Stakeholders & Team.** Primary and secondary stakeholders.
- **Jira/Asana Tickets.** Epic or story-level links.
- **Design Documents.** Research, source-of-truth design docs, prior design pages.
- **Userflows.** Happy path and edge cases.
- **Message Text File.** A table of every toast, notification, form verification, and email
  copy string, numbered to match the Figma frames. This is the single most-skipped field —
  flag it before publishing.
- **Figma Prototype.** Link to the high-fidelity prototype.
- **Annotated Prototype.** Link to the annotated version following Bitwarden's annotation
  process.

## Composing with other skills

- **`using-figma`.** Before publishing the handoff, use `get_metadata` to confirm the
  Ready-for-Dev sections exist with the expected names; use `get_variable_defs` to confirm
  tokens are library-bound rather than raw values; use `search_design_system` if a component
  in the design is suspiciously close to one that already exists.
- **`navigating-design-jira-process`.** The Jira moves that go with handoff are documented
  there — assigned epic to TODO, design tasks to DONE, dev-support task created, designs
  linked to engineering stories, "Ready for Dev" marks applied to Figma sections.
- **`content-style-guide`.** Walk the Message Text File table through the style guide before
  publishing. Toasts, errors, and form-verification text are the highest-leverage place to
  catch content-style issues before engineering localizes them.

## Common omissions to catch

- **Missing Message Text File.** Engineering will ask for it the moment they pick the epic up.
  Build the table before publishing.
- **Background that assumes context.** The handoff page is read cold by people who didn't sit
  through critique. Background must stand on its own.
- **Figma file with no Ready-for-Dev marks.** Engineering can't find what's final. The Figma
  side of the handoff is as important as the Confluence side.
- **Sections not aligned to stories.** When engineering creates stories, each story should
  map to a Figma section whose content is _only_ that story. Mismatch creates ambiguity at
  review time.
- **Stakeholder list missing engineering.** Primary stakeholders should include the EM and
  PM. If engineering isn't listed, the handoff hasn't been socialized.

## Output format

When asked to help prep a handoff:

1. **Prep checklist** — what's in place, what's missing.
2. **Page outline** — section-by-section, with what to fill in.
3. **Message Text File draft** — table form, every visible string, numbered to Figma frames.
4. **Figma readiness check** — what to confirm in the file before marking Ready for Dev.
5. **Jira moves** — the specific state transitions to apply, deferring to
   `navigating-design-jira-process` for the choreography.

Always end with the explicit go/no-go: _is this handoff actually ready?_
