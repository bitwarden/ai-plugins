# Output Document Format

## Document Structure

Every output `.md` file has the same outer structure:

1. **Title line** — `# [Ticket Title]` at the top
2. **Metadata block** — type and links, immediately below the title
3. **Field blocks** — each standalone Jira field separated by `---`

### Two kinds of sections

| Kind                        | Label style                            | How it maps to Jira                                                   |
| --------------------------- | -------------------------------------- | --------------------------------------------------------------------- |
| **Standalone Jira field**   | `**BOLD ALL-CAPS**`, preceded by `---` | Pasted into its own named field in Jira                               |
| **Description sub-section** | `# H1 heading`, no `---`               | Flows into the Description field; `# H1` renders as a heading in Jira |

`---` dividers mark Jira field boundaries only. All content between two `---` dividers is the value for one Jira field. Description sub-sections (Scenarios, Scope, Risks / Considerations, Questions and Answers, External References) flow together inside the DESCRIPTION block without `---` separators — the `# H1` headings render as headings in Jira's rich text editor.

**Standalone Jira fields by type:**

- Story, Task: ACCEPTANCE CRITERIA, QA TESTING NOTES (when justified), TECHNICAL BREAKDOWN (when justified)
- Spike: GOALS / DELIVERABLES
- Bug: REPLICATION STEPS, QA TESTING NOTES (when justified)
- All types: DESCRIPTION

**Description sub-sections** (all live inside the Description field, labeled with `# H1`):

- Purpose (all types — always)
- Goals (Epic only)
- Scenarios (Story only)
- Scope (Story, Task, Epic — when justified)
- Risks / Considerations (all types — when justified)
- Questions and Answers (all types — when justified)
- External References (all types — when justified)

---

## Filename Derivation

Derive from the ticket title:

1. Lowercase
2. Replace spaces and non-alphanumeric characters with hyphens
3. Collapse consecutive hyphens to one
4. If the result is 50 characters or fewer, use it as-is
5. If longer than 50 characters: derive a concise semantic slug of 3–5 key words (noun + action) rather than truncating mechanically; present the derived slug to the user for confirmation
6. Prefix with type: `story-`, `task-`, `epic-`, `spike-`, `bug-`

Examples:

| Title                                                                                      | Filename                                                                    |
| ------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------- |
| [Web] Add CSV export to the item list                                                      | `story-web-add-csv-export-to-the-item-list.md`                              |
| Investigate offline sync conflict model                                                    | `spike-investigate-offline-sync-conflict.md`                                |
| Vault item thumbnail renders blank image                                                   | `bug-vault-item-thumbnail-renders-blank.md`                                 |
| Add the Active members and Sponsored Families Plan usage cards to the Member Adoption page | `story-add-metric-cards-member-adoption.md` _(slug derived, not truncated)_ |

---

## Jira Placeholder Conventions

Use these consistently so the user can find and replace them when pasting into Jira:

| What it represents             | Placeholder format           | Example                                             |
| ------------------------------ | ---------------------------- | --------------------------------------------------- |
| Jira status/label element      | `[STATUS: value]`            | `[STATUS: Open]`, `[STATUS: Resolved: Yes]`         |
| Jira callout (panel) element   | `[CALLOUT: type \| message]` | `[CALLOUT: info \| Only affects web vault]`         |
| Link not yet available         | `(LINK TO BE PROVIDED)`      | `**Design:** [Export Designs](LINK TO BE PROVIDED)` |
| Scalar value not yet available | `(VALUE TO BE PROVIDED)`     | `**Feature Flag:** (VALUE TO BE PROVIDED)`          |

Callout types: `info`, `warning`, `success`, `error`.

---

## Templates

### Story

````markdown
# [Ticket Title]

**Type:** Story
**Links:** [PM-123](url) — Blocks · [PM-456](url) — Relates to

---

**DESCRIPTION**

# Purpose

**User Story:** As a [role], I want to [action] so that [outcome].

[Purpose paragraph — what this ticket covers and the context a reader needs to complete the work]

**Feature Flag:** `[launchdarkly-flag-value]`
**Design:** [Figma title](url)
**Tech Breakdown:** [Document or PR title](url)

# Scenarios

```gherkin
Scenario: [Primary path name]
  Given [starting context]
  When [user action]
  Then [observable outcome]

Scenario: [Error / edge case name]
  Given [starting context]
  When [action that triggers the edge]
  Then [observable outcome]
` ``

# Scope

- [Observable change this ticket makes]

**Stretch Goals:**
- [Related work deferred to its own ticket]

# Risks / Considerations

- [Risk: description]

# Questions and Answers

[STATUS: Open] **[Question directed at product or design]**
> [Answer or current best understanding]

# External References

- [Link text](url)

---

**ACCEPTANCE CRITERIA**

- [Observable change]

**Out of Scope:**

- [Item a reader could assume is included but isn't]

---

**QA TESTING NOTES**

- [Note that helps QA beyond what the scenarios cover]

---

**TECHNICAL BREAKDOWN**

[Intent and constraints paragraph. Captures trade-offs, non-obvious decisions, and constraints. Points to where the behavior lives using real links — never a step-by-step implementation guide.]

- **Pending:** [Decision question — see Questions and Answers for current options]
```
````

---

### Task

Same as Story except:

- No `**User Story:**` line in Description
- No Scenarios sub-section — Tasks never get Gherkin Scenarios

```markdown
# [Ticket Title]

**Type:** Task
**Links:** [PM-123](url) — Blocks

---

**DESCRIPTION**

# Purpose

[Purpose paragraph]

**Feature Flag:** `[launchdarkly-flag-value]`
**Design:** [Figma title](url)
**Tech Breakdown:** [Document or PR title](url)

# Scope

- [Observable change this ticket makes]

**Stretch Goals:**

- [Related work deferred to its own ticket]

# Risks / Considerations

- [Risk: description]

# Questions and Answers

[STATUS: Open] **[Question]**

> [Answer]

# External References

- [Link text](url)

---

**ACCEPTANCE CRITERIA**

- [Observable change]

**Out of Scope:**

- [Item]

---

**QA TESTING NOTES**

- [Note]

---

**TECHNICAL BREAKDOWN**

[Intent and constraints paragraph.]

- **Pending:** [Decision question — see Questions and Answers for current options]
```

---

### Epic

```markdown
# [Epic Title]

**Type:** Epic

---

**DESCRIPTION**

# Purpose

[Purpose paragraph — what this epic accomplishes and why]

# Goals

- [Outcome-oriented goal — what is true when this epic is complete]
- [Outcome-oriented goal]

# Scope

- [Observable change this epic delivers]

**Out of Scope:**

- [Item]

# Risks / Considerations

- [Risk]

# Questions and Answers

[STATUS: Open] **[Question]**

> [Answer]

# External References

- [Link text](url)
```

---

### Spike

```markdown
# [Spike Title]

**Type:** Spike

---

**DESCRIPTION**

# Purpose

[Purpose paragraph — what question or problem prompted this spike and what will be possible once it is complete]

# Risks / Considerations

- [Risk]

# Questions and Answers

[STATUS: Open] **[Question]**

> [Answer]

# External References

- [Link text](url)

---

**GOALS / DELIVERABLES**

- [Artifact or confirmed answer the spike must produce]
- [Artifact or confirmed answer]
```

---

### Bug

```markdown
# [Bug Title]

**Type:** Bug
**Links:** [PM-123](url) — Relates to

---

**DESCRIPTION**

# Purpose

[Purpose paragraph — what is broken and where, without restating the replication steps]

# Risks / Considerations

- [Risk]

# Questions and Answers

[STATUS: Open] **[Question]**

> [Answer]

# External References

- [Link text](url)

---

**REPLICATION STEPS**

1. [Account setup — describe the account state needed]
2. [Step]
3. [Step]

**Expected Result:** [What should happen]

**Actual Result:** [What happens instead]

**Build Version:** [Release where the defect was found]

---

**QA TESTING NOTES**

- [Note that helps QA beyond the replication steps]
```

---

## Section Presence Reference

Quick reference for which sections to include per type. "Always" = include regardless of content (use a placeholder if needed). "When justified" = include only when you have real content for it. "Never" = omit entirely.

The "Kind" column shows how the section maps to Jira: **Field** = standalone Jira field (preceded by `---`, `**BOLD ALL-CAPS**` label); **Desc** = sub-section inside the Description field (`# H1` heading, no `---`); **Meta** = file-level metadata, not a Jira field.

| Section                   | Kind           | Epic           | Story          | Task           | Spike          | Bug            |
| ------------------------- | -------------- | -------------- | -------------- | -------------- | -------------- | -------------- |
| Title                     | Meta           | always         | always         | always         | always         | always         |
| Type metadata             | Meta           | always         | always         | always         | always         | always         |
| Links metadata            | Meta           | when justified | when justified | when justified | when justified | when justified |
| **DESCRIPTION**           | Field          | always         | always         | always         | always         | always         |
| — Purpose sub-section     | Desc (H1)      | always         | always         | always         | always         | always         |
| — — User Story line       | Desc content   | never          | when justified | never          | never          | never          |
| — — Feature Flag line     | Desc content   | never          | when justified | when justified | never          | never          |
| — — Design line           | Desc content   | never          | when justified | when justified | never          | never          |
| — — Tech Breakdown line   | Desc content   | never          | when justified | when justified | never          | never          |
| — Goals sub-section       | Desc (H1)      | always         | never          | never          | never          | never          |
| — Scenarios sub-section   | Desc (H1)      | never          | always\*       | never          | never          | never          |
| — Scope sub-section       | Desc (H1)      | when justified | when justified | when justified | never          | never          |
| — — Stretch Goals         | Desc sub-item  | when justified | when justified | when justified | never          | never          |
| — Risks / Considerations  | Desc (H1)      | when justified | when justified | when justified | when justified | when justified |
| — Questions and Answers   | Desc (H1)      | when justified | when justified | when justified | when justified | when justified |
| — External References     | Desc (H1)      | when justified | when justified | when justified | when justified | when justified |
| **ACCEPTANCE CRITERIA**   | Field          | never          | always         | always         | never          | never          |
| — Out of Scope subsection | Field sub-item | never          | when justified | when justified | never          | never          |
| **QA TESTING NOTES**      | Field          | never          | when justified | when justified | never          | when justified |
| **TECHNICAL BREAKDOWN**   | Field          | never          | when justified | when justified | never          | never          |
| — Pending bullet          | Field sub-item | never          | when justified | when justified | never          | never          |
| **GOALS / DELIVERABLES**  | Field          | never          | never          | never          | always         | never          |
| **REPLICATION STEPS**     | Field          | never          | never          | never          | never          | always         |

\*Scenarios for Story: omit when `--no-scenarios` is passed or preferences set `Never include: Scenarios`.

---

## Preferences File Format

The skill reads `~/.claude/jira-drafting-preferences.md` at the start of each invocation. The file is plain markdown with a simple heading structure. All keys are optional.

```markdown
# Jira Drafting Preferences

## Defaults

- Default ticket type: Story
- Always include: Technical Breakdown
- Never include: Scope

## Field Overrides

- Risks / Considerations: standalone field
- Scope: Acceptance Criteria sub-section

## Team Conventions

- [Free-text conventions the skill should follow, one per line]
- Example: Out of Scope belongs in the Acceptance Criteria field, not the Scope section

## Formatting

- Callout format: [CALLOUT: type | message]
- Status format: [STATUS: value]
```

**Recognized keys under Defaults:**

- `Default ticket type:` — one of Epic, Story, Task, Spike, Bug
- `Always include:` — comma-separated section names (e.g., `Technical Breakdown, QA Testing Notes`)
- `Never include:` — comma-separated section names (e.g., `Scope, External References`)

**Recognized keys under Field Overrides:**

- `[Section name]: standalone field` — treat as a standalone Jira field (`**BOLD ALL-CAPS**`, preceded by `---`)
- `[Section name]: [field name] sub-section` — treat as a `# H1` sub-section inside the named field (e.g., `Acceptance Criteria sub-section`, `Technical Breakdown sub-section`)

Any section listed in the Section Presence Reference can be overridden. Use this when your Jira project exposes a section as a dedicated custom field, or when your team places a section inside a field other than Description.

**Team Conventions** is free text. The skill reads each bullet and applies it as an override to its default behavior.

Invocation arguments (`--type`, `--no-scenarios`) win over any preference in this file.
