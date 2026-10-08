---
name: authoring-jira-tickets
description: >-
  Draft a Jira ticket as a local .md file ready to copy into Jira fields.
  Trigger phrases: "draft a jira ticket", "write up this ticket", "author a story for X",
  "create a ticket for this", "draft a bug report", "write a spike ticket", "help me
  write a ticket", "author a jira ticket", "draft this as a ticket". Produces a
  structured .md file in the current directory. Does not create the ticket in Jira —
  use filing-jira-tickets for that.
when_to_use: >-
  Use when the user wants to draft a Jira ticket locally before filing, when they want
  to iterate on ticket content, or when Jira access is unavailable. Do not use when the
  user is ready to create the ticket directly in Jira (that is filing-jira-tickets).
allowed-tools: Read, Write, Glob, Grep, AskUserQuestion
---

# Authoring Jira Tickets

A well-written ticket is tight: every fact lives once, sections describe behavior not code, and each section covers only what this ticket delivers. Draft tight — do not write loose and edit down later.

References that inform this skill:

- Ticket type definitions and field map: [`references/ticket-type-guide.md`](references/ticket-type-guide.md)
- Exact output format and templates: [`references/output-doc-format.md`](references/output-doc-format.md)
- Writing rules: [`references/writing-rules.md`](references/writing-rules.md)

## Step 1 — Load preferences

Read `~/.claude/jira-drafting-preferences.md` if it exists. Extract:

- **Default type** — which ticket type to propose when none is specified
- **Always include** — sections to add even when no content is provided (leave them with a placeholder)
- **Never include** — sections to omit regardless of content
- **Field overrides** — which sections to treat as standalone Jira fields or as sub-sections inside a specific field, overriding the skill defaults
- **Team conventions** — formatting or structural preferences that override skill defaults

If the file is absent, use skill defaults: propose type based on context, include sections when content justifies them.

**Example `~/.claude/jira-drafting-preferences.md`:**

```markdown
default-type: Story

always-include:
  - Scenarios

never-include:
  - Technical Breakdown

team-conventions:
  - Write acceptance criteria as "Given / When / Then" bullet points.
  - Use "user" not "end user" in user story sentences.
```

Invocation arguments override anything in the preferences file:

- `--type [Epic|Story|Task|Spike|Bug]` — sets the ticket type directly, skips type proposal
- `--no-scenarios` — omits the Scenarios section from a Story even when content justifies it

**Completion criterion:** a resolved set of defaults for the session.

## Step 2 — Identify ticket type and gather context

### Identify the ticket type

If the type was set by `--type`, skip the proposal. Otherwise:

- Ask what the ticket covers if not already described.
- Propose a type with brief reasoning. See [`references/ticket-type-guide.md`](references/ticket-type-guide.md) for definitions and the team's conventions. When the work is genuinely ambiguous between Story and Task, ask.

The five types: **Epic**, **Story**, **Task**, **Spike**, **Bug**.

### Gather context

Collect what is needed to fill the sections for the proposed type. Ask concisely — one round of questions, not a series of individual prompts. The minimum to start drafting:

- **All types:** What is this ticket about? What problem does it solve or what does it deliver?
- **Story / Task:** Any acceptance criteria already in mind? Feature flag, Figma link, or tech breakdown link to include? If a Figma link is provided, note it cannot be opened and ask for a description of the relevant frames or screenshots.
- **All types (follow-up work):** Does the design include anything explicitly marked as a later phase or follow-up? Surface it in Out of Scope or Stretch Goals — do not drop it silently.
- **Story:** Should there be a user story sentence (`As a [role], I want to…`)?
- **Bug:** Steps to reproduce, expected result, actual result, build version where the defect was found?
- **Spike:** What must the spike produce — a decision, a document, a proof of concept?
- **All types (optional):** Any tickets to link (blocks / relates to)?

Do not ask for content for sections that are marked "never include" in the loaded preferences.

### Propose a title

Based on the context gathered, propose a ticket title following the title style rule: `[Area] imperative verb, outcome` (e.g., `[Web] Add CSV export to the item list`). Do not use the user's description verbatim — derive a proper title. If the user's description is verbose, trim to the essential action and subject. Present the proposed title for confirmation before proceeding to Step 3.

### Codebase exploration

If the user wants codebase context to inform the draft, ask explicitly before exploring. If they say yes, use Glob, Grep, and Read to orient in the relevant area. Cap exploration at what informs the ticket — do not turn this into a full codebase survey.

**Content surfaced by exploration belongs only in Technical Breakdown** (file paths, component names, constraints). It does not flow into Scope, Acceptance Criteria, or Scenarios.

**Completion criterion:** enough context to fill all required sections for the identified type.

## Step 3 — Draft the ticket

Load the template for the ticket type from [`references/output-doc-format.md`](references/output-doc-format.md). Fill every section that has content. Apply [`references/writing-rules.md`](references/writing-rules.md) throughout — especially:

- One fact, one place. If two sections would say the same thing, drop it from the second.
- Behavior not implementation. Code identifiers belong only in Technical Breakdown.
- Cover only this ticket's deliverables. Do not re-declare what another ticket delivers.

**Optional sections:** include when content genuinely justifies them. An empty optional section is worse than an absent one.

**Jira placeholders** — use these consistently so the user can find and replace them when pasting into Jira:

- Status/label element: `[STATUS: value]`
- Callout element: `[CALLOUT: type | message]` (types: `info`, `warning`, `success`, `error`)
- Links not yet available: `(LINK TO BE PROVIDED)`
- Scalar values not yet available (feature flag names, version numbers, etc.): `(VALUE TO BE PROVIDED)`

**Cross-ticket observations** — observations that apply across siblings (shared blockers, inconsistent terminology, missing definitions) do not belong in this ticket's Questions and Answers. Surface them after the draft under "Cross-ticket notes:".

**Completion criterion:** a complete draft with every required section filled and every optional section either filled or absent.

## Step 4 — Review with user

Show the draft inline. After the draft, briefly note:

- Any optional sections that were omitted and why (one line each)
- Any content the user mentioned but didn't have yet (placeholders used)
- Any cross-ticket observations under a "Cross-ticket notes:" heading — do not fold these into Questions and Answers

Ask the user to review. Accept changes to: content in any section, which sections appear, ticket type (requires re-draft), links. Iterate until the user approves.

Do not move to Step 5 without explicit approval.

**Completion criterion:** user has approved the draft.

## Step 5 — Write the file

Derive the filename from the ticket title:

1. Lowercase the title
2. Replace spaces and punctuation with hyphens
3. Collapse consecutive hyphens
4. If the result is 50 characters or fewer, use it as-is; if longer, derive a concise semantic slug of 3–5 key words (noun + action) rather than truncating mechanically — present the derived slug for confirmation before writing
5. Prefix with the ticket type: `story-`, `task-`, `bug-`, `epic-`, `spike-`

Example: `story-add-csv-export-item-list.md`

Write the file to the current directory. Confirm the path to the user.

**Preferences file:** If `~/.claude/jira-drafting-preferences.md` did not exist at the start of this session and team conventions were applied during drafting (ticket type defaults, section choices, phrasing patterns), offer to create the file now to capture those conventions. Skip this step if no conventions were applied beyond skill defaults.

If `filing-jira-tickets` is available (bitwarden-atlassian-tools plugin is installed), mention that the user can file it directly in Jira using that skill.

**Completion criterion:** file written, path confirmed to user.

---

## Known Limitations of Local Drafting

These limitations are inherent to local drafting — not bugs in the skill.

**No links between sibling drafts.** Cross-ticket links are placeholders (`(LINK TO BE PROVIDED)`) until the referenced tickets exist in Jira.

**Shared blockers repeat as placeholders.** A blocker that has not yet been filed appears as `(LINK TO BE PROVIDED)` on every dependent. The repetition is expected — each draft signals the dependency even though the link cannot resolve yet.

**Cross-ticket terminology is not checked automatically.** Shared terms drift silently when tickets are drafted independently. Before filing a set of siblings, review shared definitions and confirm they are consistent across all tickets.
