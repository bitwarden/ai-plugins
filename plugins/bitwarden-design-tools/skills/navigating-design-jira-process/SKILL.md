---
name: navigating-design-jira-process
description: Move design work through Bitwarden's Product and Design Jira workflow — final designs attached to tickets, the 30/60/90 critique cadence tracked in Figma, status transitions on engineering epics and stories, and the one-off engineering story flow.
when_to_use: Use when a task is about the Jira choreography that surrounds design work — distinct from the design substance itself. Triggers — "set up Jira for this design project", "what's the design status", "move this to Ready for Dev", "Jira workflow for design", "how does design plug into the epic". Not for the full handoff workflow (use `preparing-design-handoff`).
allowed-tools: Skill, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_remote_links, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_issues, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence_cql
---

# Navigating the Product and Design Jira Process

This skill grounds Jira moves in the design team's current practice for plugging into
engineering's Jira workflow. The goal: keep design decisions visible alongside the
engineering work — without maintaining a parallel design tracker. Designs are attached
directly to the engineering tickets they belong to, and everything substantive (30/60/90
critique iterations, copy, annotations) lives in Figma.

> **A note on status names below.** Jira status labels appear here in the same casing Jira
> uses them — `IN DESIGN`, `IN PROGRESS`, `DONE`, `DESIGN NEEDED`, `Ready for Dev`. Copy them
> verbatim when transitioning tickets.

## The structural rule

**Designs are attached directly to tickets.** The Figma file lives in the engineering Epic's
"Design" field (or, for one-off engineering stories, in the story's "Design" field). There is
no parallel design project, no parallel design Kanban, and no per-stage design tasks.

That's the design-team-Jira insight in one sentence. Everything else is choreography around
this rule.

## Epic-driven flow

### Initial setup

- A PM creates at least one Epic to accompany every Product Initiative document they're
  working on.
- PM assigns the Epic to the designated designer.

### In Design

- Designer (or PM) moves the Epic to `IN DESIGN`.
- Designer runs the 30/60/90 critique cadence **in Figma** — no separate Jira tasks per stage.
  Stage iterations, attached materials (stakeholder presentations, research), and
  cross-iteration feedback all live in the Figma file alongside the work.

### Design Done

- In Figma, group final designs on a single page with named Sections for each story-level
  surface.
- Designer links the Figma file in the Epic's "Design" field.
- Designer marks Figma sections as **"Ready for Dev"**.
- EM moves the Epic to `Ready for Dev` to signal engineering can pick the work up. (Some
  teams have automation that handles this; treat it as the EM's responsibility for now.)

### Engineering technical breakdown

- When engineering creates stories during technical breakdown, designer + PM + the engineer
  doing the breakdown together review the stories.
- For each story, ensure the correct Figma section is linked and that the section's content
  is **only** about that story. One-to-one mapping.

### In Progress (and dev support)

- PM or EM moves the Epic to `IN PROGRESS` when development starts.
- PM/EM creates a dev-support task titled `[project name] - dev support`, assigns it to the
  project's designer, and links it as "relates to" all engineering stories needing design
  support. (This convention persists for now even as other separate-design-task work has
  retired.)
- The task lets the designer know when their project enters development and represents the
  misc support needed throughout.
- When the last engineering task is done, the dev-support task is also marked `DONE`.

## One-off engineering stories

Some stories aren't tied to an epic — common on the UI Foundation team. The flow is shorter:

- An engineering story is created outside an epic; PM or EM realizes design support is needed.
  (Or: a designer working on a component improvement for UIF creates the story themselves.)
- PM or EM moves the story to `DESIGN NEEDED` and assigns it to the feature team's designer.
- Designer does the design work in Figma. No separate design task is created.
- When the design is complete, the designer:
  1. Links the Figma file to the story's "Design" field.
  2. Unassigns themselves from the story.
  3. Adds a comment in the ticket noting the design is ready to be picked up.

The three closing steps — link, unassign, comment — are explicit. Skipping any of them
leaves the story stuck in someone's queue or visible-but-not-discoverable.

## Composing with other skills

- **`preparing-design-handoff`.** The transitions at the end of In Design (Figma linked, sections
  marked Ready for Dev, EM moves Epic) are the pre-handoff side of the handoff process. The
  handoff skill is the gate / checklist; this skill is the canonical lifecycle.
- **`evolving-design-system-components`.** Component Library work generates Jira issues on
  the Component Library board. Those follow the same rule (designs attached to tickets), but
  feature-team-owned recipes generate stories in the feature team's project rather than the
  Component Library project. Surface the difference explicitly to the designer.

## Common mistakes to catch

- **Forgetting to mark Figma sections "Ready for Dev."** Engineering can't find what's final.
  This is part of Design Done, not optional.
- **Sections not aligned to stories.** When engineering creates stories, each story should
  map to a Figma section whose content is _only_ that story. Mismatch creates ambiguity at
  review time.
- **One-off engineering story left unfinished at the design end.** All three closing steps
  must happen — link Figma to the story's "Design" field, unassign self, comment that the
  design is ready. Missing any one of them leaves the ticket in an ambiguous state.
- **PM creating the dev-support task too late or not at all.** When dev support isn't
  visible on the Epic, dev support requests come at the designer without warning. Surface
  this gap when reviewing a project's Jira state.

## Output format

When asked to set up or move work through the Jira process:

1. **Project shape** — is this an epic-driven project or a one-off engineering story?
2. **Current state** — what Jira entities exist (Epic, story, dev-support task) and their
   current statuses.
3. **Moves to make** — the specific status transitions and Figma links to apply, named by
   responsibility (designer, PM, EM).
4. **Figma links** — what to attach where (Epic "Design" field, story "Design" field).
5. **Watch-outs** — the common mistakes above that apply to this specific project.
