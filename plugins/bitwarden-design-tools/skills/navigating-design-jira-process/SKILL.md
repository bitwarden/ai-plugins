---
name: navigating-design-jira-process
description: Move design work through Bitwarden's Product and Design Jira workflow — engineering epics with nested design tasks, the 30/60/90 iteration cadence, status transitions across the design and engineering boards, and one-off engineering stories that need design support.
when_to_use: Use when a task is about the Jira choreography that surrounds design work — distinct from the design substance itself. Triggers — "set up Jira for this design project", "what's the design Jira status", "move this to Ready for Dev", "create design tasks for an epic", "Jira workflow for design", "30/60/90 in Jira", "design board", "design task status". Not for the full handoff workflow (use `preparing-design-handoff`).
allowed-tools: Skill, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_remote_links, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_issues, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence_cql
---

# Navigating the Product and Design Jira Process

This skill grounds Jira moves in the
[Product and Design Jira Process](https://bitwarden.atlassian.net/wiki/spaces/PROD/pages/1828094078)
Confluence page. The goal of the process: keep design tasks visibly close to the engineering
workflows so executives, PMs, QA, and engineering can see what design decisions are happening
and where the work is. Read the canonical page via `get_confluence_page` when prepping a real
project — the page has a Figma process diagram that this skill summarizes but does not
duplicate.

> **A note on status names below.** Jira status labels appear here in the same casing Jira uses
> them — `IN DESIGN`, `TODO`, `IN PROGRESS`, `DONE`, `ON HOLD`, `DESIGN NEEDED`, `Ready for Dev`.
> Copy them verbatim when transitioning tickets; the mixed casing isn't a typo, it's the labels
> engineering and design configured.

## The structural rule

**Design tasks live under engineering epics**, not in a parallel design-only stream. Every
design task's `Parent` field points to an engineering epic. The design team maintains a
Kanban board, but the tasks on it are children of engineering epics — the same epics
engineering is delivering.

That's the design-team-Jira insight in one sentence. Everything else is choreography around
this rule.

## The five-act flow (initial setup → in design → design done → in progress → finishing)

### Act 1: Initial setup

- A PM creates at least one Epic to accompany every Product Initiative document they're
  working on.
- PM assigns the Epic to the designated designer.

### Act 2: In Design

- Designer moves the Epic to `IN DESIGN` (the Epic-level "Design and Scoping" state).
- Designer creates design tasks in the Product Design company-managed project, with `Parent`
  set to the relevant engineering Epic.
- **One design task per iteration of the 30/60/90 framework.** A typical project has at least
  three tasks: 30% review, 60% review, 90% review. If a stage needs multiple reviews, use
  `60% review 2`.
- When a design task is complete, attach a copy of the design at that stage. Link a Figma
  page named for the stage — `30% review`, `60% review`, `60% review 2` etc.
- Attach other materials used in that stage (stakeholder presentations, etc.).
- Feedback on the iteration becomes requirements for the next iteration's task.
- Designer moves design tasks through the Design Kanban: `TODO` → `IN PROGRESS` → `DONE` (and
  `ON HOLD` if needed).

### Act 3: Design Done

- All design tasks are `DONE`.
- Designer moves the Epic to `TODO` (the engineering board state that signals Ready for Dev).
- In Figma, group final designs on a single page with named Sections for each story-level
  surface.
- Designer links the Figma file in the Epic's "Design" field.
- Designer marks Figma sections as **"Ready for Dev"**.
- Design tasks remain on the Epic, assigned to the designer — that visibility helps QA and
  dev know who the designer is.

### Act 4: Engineering technical breakdown

- When engineering creates stories during technical breakdown, designer + PM + the engineer
  doing the breakdown together review the stories.
- For each story, ensure the correct Figma section is linked and that the section's content
  is **only** about that story. One-to-one mapping.

### Act 5: In Progress (and dev support)

- PM or EM moves the Epic to `IN PROGRESS` when development starts.
- PM/EM creates a Design project task titled `[project name] - dev support`, assigns it to
  the project's designer, and links it as "relates to" all engineering stories needing
  design support.
- Designer moves the dev-support task to `IN PROGRESS` on the design board. This represents
  the misc design support the project needs through dev.
- When the last engineering task is done, the dev-support task is also marked `DONE`.

## One-off engineering stories

Some stories aren't tied to an epic — common on the UI Foundation team. The flow for these is
shorter and uses different statuses:

- An engineering story is created outside an epic; PM or EM realizes design support is needed.
- (Or: a designer working on a component improvement for UIF creates the story.)
- PM or EM moves the story to `DESIGN NEEDED` (a story-level status, distinct from the Epic
  `IN DESIGN` status) and assigns it to the feature team's designer.
- The story is pulled into the Design board's `TO DO` column.
- When the designer starts, they move the design task to `IN PROGRESS` on the design board,
  which corresponds to `IN DESIGN` on the engineering board.
- When the design is complete, designer moves it to `DONE` on the design board, which
  corresponds to `TODO` on the engineering board (Ready for Dev).
- Designer links the Figma file to the story's "Design" field.
- Designer unassigns themselves from the story.

## The two boards are linked, not duplicated

The design Kanban and the engineering Kanban share state through the structural rule above —
design tasks are children of engineering epics, so they show up in both views. The status
_labels_ differ between boards (the engineering board has phases like `DESIGN AND SCOPING`,
`IN PROGRESS`, `DONE`; the design board has `TO DO`, `IN PROGRESS`, `DONE`, `ON HOLD`). When
moving work, name the board explicitly to avoid ambiguity.

## Composing with other skills

- **`preparing-design-handoff`.** The Jira transitions in Act 3 (Design Done) are the
  pre-handoff side of the handoff process. The handoff skill composes this one for those
  transitions; this skill provides the canonical choreography.
- **`evolving-design-system-components`.** Component Library work generates Jira issues on
  the Component Library board — those follow the same rule (children of engineering epics
  when feature-driven) but feature-team-owned recipes generate stories in the feature team's
  project rather than the Component Library board. Surface the difference explicitly to the
  designer.

## Common mistakes to catch

- **Design tasks without a parent epic.** Breaks the structural rule. Find the right
  engineering epic, set the parent. If no epic exists, the work is probably a one-off — apply
  the one-off engineering story flow instead.
- **One task for all three review stages.** Loses the 30/60/90 visibility. Each stage gets
  its own task.
- **Forgetting to mark Figma sections Ready for Dev.** Engineering can't find what's final.
  This is part of Design Done, not optional.
- **Designer unassigning themselves from the design tasks after handoff.** Don't. The tasks
  remain assigned to the designer so QA and dev know who to talk to. The exception is the
  one-off engineering story flow, where the designer _does_ unassign themselves at the end.
- **PM creating the dev-support task too late or not at all.** When dev support is invisible
  on the design board, dev support requests come at the designer without warning. Surface
  this gap when reviewing a project's Jira state.

## Output format

When asked to set up or move work through the Jira process:

1. **Project shape** — is this an epic-driven project or a one-off engineering story?
2. **Current state** — what Jira entities exist (epic, design tasks, story), and what their
   current statuses are on each board.
3. **Moves to make** — the specific status transitions and entity creations, named by board.
4. **Figma links** — what to attach where (design task attachments, epic "Design" field,
   story "Design" field).
5. **Watch-outs** — the common mistakes above that apply to this specific project.
