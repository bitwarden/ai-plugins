# Output Document Format

## Document Structure

Every output `.md` file has the same outer structure:

1. **Title line** — `# [Ticket Title]` at the top
2. **Metadata block** — type and links, immediately below the title
3. **Field blocks** — each Jira field or Description section separated by `---`

Field labels use `**BOLD ALL-CAPS**`. This makes them easy to find when copy-pasting into Jira. Content inside a field may use `#` for Jira H1 headings freely — the field label itself is not a markdown heading.

---

## Filename Derivation

Derive from the ticket title:

1. Lowercase
2. Replace spaces and non-alphanumeric characters with hyphens
3. Collapse consecutive hyphens to one
4. Truncate to 50 characters at a word boundary
5. Prefix with type: `story-`, `task-`, `epic-`, `spike-`, `bug-`

Examples:

| Title                                    | Filename                                     |
| ---------------------------------------- | -------------------------------------------- |
| Add CSV export to the item list (web)    | `story-add-csv-export-to-the-item-list.md`   |
| Investigate offline sync conflict model  | `spike-investigate-offline-sync-conflict.md` |
| Vault item thumbnail renders blank image | `bug-vault-item-thumbnail-renders-blank.md`  |

---

## Jira Placeholder Conventions

Use these consistently so the user can find and replace them when pasting into Jira:

| What it represents           | Placeholder format           | Example                                             |
| ---------------------------- | ---------------------------- | --------------------------------------------------- |
| Jira status/label element    | `[STATUS: value]`            | `[STATUS: Open]`, `[STATUS: Resolved: Yes]`         |
| Jira callout (panel) element | `[CALLOUT: type \| message]` | `[CALLOUT: info \| Only affects web vault]`         |
| Link not yet available       | `(LINK TO BE PROVIDED)`      | `**Design:** [Export Designs](LINK TO BE PROVIDED)` |

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

**User Story:** As a [role], I want to [action] so that [outcome].

[Purpose paragraph — what this ticket covers and the context a reader needs to complete the work]

**Feature Flag:** `[launchdarkly-flag-value]`
**Design:** [Figma title](url)
**Tech Breakdown:** [Document or PR title](url)

---

**ACCEPTANCE CRITERIA**

- [Observable change]
- [Observable change]

**Out of Scope:**

- [Item a reader could assume is included but isn't]

---

**SCENARIOS**

```gherkin
Scenario: [Primary path name]
  Given [starting context]
  When [user action]
  Then [observable outcome]

Scenario: [Error / edge case name]
  Given [starting context]
  When [action that triggers the edge]
  Then [observable outcome]
` `` `

---

**QA TESTING NOTES**

- [Note that helps QA beyond what the scenarios cover]

---

**TECHNICAL BREAKDOWN**

[Intent and constraints paragraph. Captures trade-offs, non-obvious decisions, and constraints. Points to where the behavior lives using real links — never a step-by-step implementation guide.]

---

**SCOPE**

- [Observable change this ticket makes]

**Stretch Goals:**
- [Related work deferred to its own ticket]

**Out of Scope:**
- [Item a reader could assume is included but isn't]

---

**RISKS / CONSIDERATIONS**

- [Risk: description]

---

**QUESTIONS AND ANSWERS**

[STATUS: Open] **[Question directed at product or design]**
> [Answer or current best understanding]

---

**EXTERNAL REFERENCES**

- [Link text](url)
```
````

---

### Task

Same as Story except:

- No `**User Story:**` line in Description
- No `**SCENARIOS**` field — Tasks never get Gherkin Scenarios

```markdown
# [Ticket Title]

**Type:** Task
**Links:** [PM-123](url) — Blocks

---

**DESCRIPTION**

[Purpose paragraph]

**Feature Flag:** `[launchdarkly-flag-value]`
**Design:** [Figma title](url)
**Tech Breakdown:** [Document or PR title](url)

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

---

**SCOPE**

- [Observable change]

---

**RISKS / CONSIDERATIONS**

- [Risk]

---

**QUESTIONS AND ANSWERS**

[STATUS: Open] **[Question]**

> [Answer]

---

**EXTERNAL REFERENCES**

- [Link text](url)
```

---

### Epic

```markdown
# [Epic Title]

**Type:** Epic

---

**DESCRIPTION**

[Purpose paragraph — what this epic accomplishes and why]

# Goals

- [Outcome-oriented goal — what is true when this epic is complete]
- [Outcome-oriented goal]

---

**SCOPE**

- [Observable change this epic delivers]

**Out of Scope:**

- [Item]

---

**RISKS / CONSIDERATIONS**

- [Risk]

---

**QUESTIONS AND ANSWERS**

[STATUS: Open] **[Question]**

> [Answer]

---

**EXTERNAL REFERENCES**

- [Link text](url)
```

---

### Spike

```markdown
# [Spike Title]

**Type:** Spike

---

**DESCRIPTION**

[Purpose paragraph — what question or problem prompted this spike and what will be possible once it is complete]

---

**GOALS / DELIVERABLES**

- [Artifact or confirmed answer the spike must produce]
- [Artifact or confirmed answer]

---

**RISKS / CONSIDERATIONS**

- [Risk]

---

**QUESTIONS AND ANSWERS**

[STATUS: Open] **[Question]**

> [Answer]

---

**EXTERNAL REFERENCES**

- [Link text](url)
```

---

### Bug

```markdown
# [Bug Title]

**Type:** Bug
**Links:** [PM-123](url) — Relates to

---

**DESCRIPTION**

[Purpose paragraph — what is broken and where, without restating the replication steps]

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

---

**RISKS / CONSIDERATIONS**

- [Risk]

---

**QUESTIONS AND ANSWERS**

[STATUS: Open] **[Question]**

> [Answer]

---

**EXTERNAL REFERENCES**

- [Link text](url)
```

---

## Section Presence Reference

Quick reference for which sections to include per type. "Always" = include regardless of content (use a placeholder if needed). "When justified" = include only when you have real content for it. "Never" = omit entirely.

| Section                   | Epic           | Story          | Task           | Spike          | Bug            |
| ------------------------- | -------------- | -------------- | -------------- | -------------- | -------------- |
| Title                     | always         | always         | always         | always         | always         |
| Type metadata             | always         | always         | always         | always         | always         |
| Links metadata            | when justified | when justified | when justified | when justified | when justified |
| DESCRIPTION               | always         | always         | always         | always         | always         |
| — User Story line         | never          | when justified | never          | never          | never          |
| — Purpose paragraph       | always         | always         | always         | always         | always         |
| — Feature Flag line       | never          | when justified | when justified | never          | never          |
| — Design line             | never          | when justified | when justified | never          | never          |
| — Tech Breakdown line     | never          | when justified | when justified | never          | never          |
| — Goals (epic only)       | always         | never          | never          | never          | never          |
| ACCEPTANCE CRITERIA       | never          | always         | always         | never          | never          |
| — Out of Scope subsection | never          | when justified | when justified | never          | never          |
| SCENARIOS                 | never          | always*        | never          | never          | never          |
| QA TESTING NOTES          | never          | when justified | when justified | never          | when justified |
| TECHNICAL BREAKDOWN       | never          | when justified | when justified | never          | never          |
| GOALS / DELIVERABLES      | never          | never          | never          | always         | never          |
| REPLICATION STEPS         | never          | never          | never          | never          | always         |
| SCOPE                     | when justified | when justified | when justified | never          | never          |
| — Stretch Goals           | when justified | when justified | when justified | never          | never          |
| — Out of Scope            | when justified | when justified | when justified | never          | never          |
| RISKS / CONSIDERATIONS    | when justified | when justified | when justified | when justified | when justified |
| QUESTIONS AND ANSWERS     | when justified | when justified | when justified | when justified | when justified |
| EXTERNAL REFERENCES       | when justified | when justified | when justified | when justified | when justified |

*SCENARIOS for Story: omit when `--no-scenarios` is passed or preferences set `Never include: Scenarios`.

---

## Preferences File Format

The skill reads `~/.claude/jira-drafting-preferences.md` at the start of each invocation. The file is plain markdown with a simple heading structure. All keys are optional.

```markdown
# Jira Drafting Preferences

## Defaults

- Default ticket type: Story
- Always include: Technical Breakdown
- Never include: Scope

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

**Team Conventions** is free text. The skill reads each bullet and applies it as an override to its default behavior.

Invocation arguments (`--type`, `--no-scenarios`) win over any preference in this file.
