---
name: filing-breakdown-tasks
description: Turn a tech breakdown's tasks.md into Jira ticket drafts — an epic parent plus one child story/task per task entry, each a real ticket with acceptance criteria and mapped Blocked-by/Depends-on links — then hand off to filing-jira-tickets to file them.
when_to_use: Use only when starting from a finished tasks.md (a tech breakdown's task decomposition) to create a set of new Jira tickets — phrasings like "create the tickets from tasks.md", "make Jira tickets for these tasks", "file the epic and stories", "turn this breakdown into Jira tickets". Also use when a tech breakdown in bitwarden/tech-breakdowns hands off a finished tasks.md. Do not use to edit or update an existing ticket's fields such as description, acceptance criteria, status, or labels (there's no tasks.md involved); to read or research existing issues (that is researching-jira-issues); or to move, organize, or otherwise manage breakdown files and folders.
allowed-tools: Read, Glob, Skill, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue
---

# Filing Breakdown Tasks into Jira

This skill owns the tech-breakdown half of ticketing: turning a `tasks.md` decomposition into a parented set of ticket drafts. It does not file them. Once the drafts are ready it hands off to **filing-jira-tickets**, which reads the target project's create screen, previews each ticket, takes approval, and creates and links them through the Atlassian MCP write tools.

Tickets are read outside the breakdown's context, so translate each task entry into a ticket that stands on its own — never paste the decomposition label.

## Step 1 — Build the ticket tree

Read `tasks.md` and its sibling `breakdown.md`. Establish the hierarchy before drafting any fields:

- The breakdown's **epic is the parent**. Take its key from `breakdown.md`. If no epic exists, ask whether to create one or attach children to an existing key — do not guess a key. Confirm the key is an Epic (`get_issue`, check `issuetype`) before parenting under it.
- Each task entry becomes **one child** — Story by default; Task or Bug only if the entry says so.
- For each child, capture its **Owner**, **Blocked by**, and **Depends on**.

**Completion criterion:** an echoed tree — epic key, then the ordered children with type and parent — where the child count matches the task count in `tasks.md`.

## Step 2 — Draft each child ticket

Translate each entry into ticket fields; don't copy it:

- **Title** — imperative verb + outcome + context (client/area), matching sibling-ticket house style, e.g. `Add CSV export to the item list (web)`. NOT the decomposition label (`ExportService + column mapping (libs/exporter)`).
- **Description** — one short paragraph of the actual work plus genuinely per-ticket caveats. No lineage boilerplate (`Part of PM-XXXX`), no breakdown path — the epic-child link already conveys that.
- **Acceptance criteria** — written in Gherkin (`Scenario` / `Given` / `When` / `Then` / `And`). Supply the content only; filing-jira-tickets decides the field — the project's criteria field, or the description if it has none.
- **Parent** — the epic key from Step 1.

Leave labels unset unless the user asked for a specific one.

**Completion criterion:** for every child, a draft of `{title, description, acceptance criteria, type, parent}`.

## Step 3 — Map the dependency links

From each task's **Blocked by** / **Depends on**, build the link map filing-jira-tickets will wire:

- Hard dependency (must land first) → **Blocks**, with the must-land-first ticket as the blocker.
- Soft / ordering-only → **Relates**.
- A dependency whose target has no ticket in this set (e.g. a sibling slice not yet filed) → report it to the user, don't drop it.

**Completion criterion:** a link map of `{blocker, blocked, type}` for every dependency whose both ends are tickets in this set.

## Step 4 — Hand off to filing-jira-tickets

Hand the drafted tickets (Step 2) and the link map (Step 3) to **`Skill(filing-jira-tickets)`**. It owns the rest: reading the project's create screen, dry-run previews, per-ticket approval, live creation, and link verification.

If an epic is being created rather than reused, file it first so the children have a parent key to reference.

**Completion criterion:** filing-jira-tickets has the full draft set and link map and has taken over creation.
