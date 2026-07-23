---
name: creating-jira-tickets
description: Create Jira tickets from a tech breakdown's tasks.md — an epic plus one child story/task per task entry, with real ticket titles, a Gherkin Acceptance criteria section, and wired Blocked-by/Depends-on links.
when_to_use: Use when the user is ready to file a breakdown's tasks in Jira — phrasings like "create the tickets from tasks.md", "make Jira tickets for these tasks", "file the epic and stories", "turn this breakdown into Jira tickets". Also use when decomposing-into-tasks or developing-breakdown-plan hands off a finished tasks.md. Do not use for reading or researching existing issues (that is researching-jira-issues), or for editing tickets that already exist.
allowed-tools: Read, Write, Glob, AskUserQuestion, Bash(acli jira auth status:*), Bash(acli jira workitem view:*), Bash(acli jira workitem create:*), Bash(acli jira workitem edit:*), Bash(acli jira workitem link:*)
---

# Creating Jira Tickets from tasks.md

Tickets are read outside the breakdown's context, so translate each task entry into a ticket that stands on its own. Create them **one at a time** — a wording or field mistake surfaces on the first ticket, not across the whole set.

Two facts shape every step:

- **acli for everything.** Reads and writes go through the `acli` CLI.
- **One at a time.** Live tickets are awkward to unwind. The user reviews the first before the rest.

## Step 1 — Preflight the write path

Confirm `acli` can write before drafting anything:

- Run `acli jira auth status`.
- Missing binary → prompt to install (`brew install atlassian/homebrew-acli/acli`, or the Atlassian CLI docs) and **stop**.
- Installed but not authenticated → prompt `acli jira auth login --web` and **stop**.

**Completion criterion:** `acli jira auth status` prints `Authenticated` against `bitwarden.atlassian.net`, or you have stopped with an install/auth prompt.

## Step 2 — Build the ticket tree

Read `tasks.md` and its sibling `breakdown.md`. Establish the hierarchy before writing any fields:

- The breakdown's **epic is the parent**. Take its PM key from `breakdown.md`. If no epic exists, ask whether to create one or attach children to an existing key — do not guess a key. Confirm the key is `issuetype: Epic` (`workitem view <KEY> --fields issuetype`) before parenting under it.
- Each task entry becomes **one child** — Story by default; Task or Bug only if the entry says so.
- For each child, capture its **Owner** (team → label), **Blocked by**, and **Depends on** for Step 5.

**Completion criterion:** an echoed tree — epic key, then the ordered children with type and parent — where the child count matches the task count in `tasks.md`.

## Step 3 — Turn each task into real ticket fields

Translate the entry, don't copy it:

- **Title** — imperative verb + outcome + context (client/area), matching sibling-ticket house style, e.g. `Add CSV export to the item list (web)`. NOT the decomposition label (`ExportService + column mapping (libs/exporter)`).
- **Description** — one short paragraph of the actual work plus genuinely per-ticket caveats. No lineage boilerplate (`Part of PM-####`), no breakdown path — the epic-child link already conveys that. Spell out shorthand; no `§` or `→` symbols.
- **Acceptance criteria** — its own ADF heading, written in Gherkin (`Scenario` / `Given` / `When` / `Then` / `And`).
- **Labels** — Team, Capability Driver, and Initiative Owner auto-default from the PM project — do not set them. If the only owner-derived label would be Team, apply no label. Otherwise verify the expected label against a sibling child ticket of the same epic before applying.

Build the description as ADF and assemble the create command from **[references/acli-and-adf.md](references/acli-and-adf.md)**.

**Completion criterion:** for every child, a drafted `{title, ADF description containing an "Acceptance criteria" heading, type, parent, labels}`.

## Step 4 — Create one at a time

Never batch-create:

1. Preview the exact fields and the full `acli ... create` command for the **first** ticket.
2. Create only that one. Record its returned key.
3. Pause — wait for the user to review it in Jira and give the go-ahead.
4. Proceed to the next, one ticket at a time, recording each key.

**Completion criterion:** every child created, each returned key recorded, and the user reviewed the first before the rest were created.

## Step 5 — Wire dependency links

From each task's **Blocked by** / **Depends on**, create links with `acli`. Linking is reversible (`link delete`), so this step may run as a batch once all tickets exist.

- Map to a link type: hard dependency (must land first) → **Blocks**; soft / ordering-only → **Relates**. Run `acli jira workitem link type` once to confirm the available types.
- The acli link **direction is inverted** from its own success message — see the reference for the exact `--out`/`--in` mapping and how to read a link back.
- Verify every link with `acli jira workitem link list --key <KEY> --json` (check it against the Jira UI panel headings when unsure).

**Completion criterion:** every relationship whose target ticket exists is created and verified via `link list`; relationships pointing at not-yet-created work are reported back to the user, not dropped.
