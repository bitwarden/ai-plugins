# Ticket Type Guide

## Type Definitions

### Epic

A large initiative that groups related stories, tasks, and spikes. Epics describe an outcome, not a deliverable. They are not QA-gated. The description and goals live in the epic; child tickets carry the scoped deliverables.

**When to choose:** The work spans multiple tickets and needs a common parent. The user says "initiative", "feature area", "program of work", "epic", or similar.

### Story

A unit of user-facing work that goes through QA at Bitwarden. Stories are written from the user's perspective and require Gherkin Scenarios so QA has concrete test cases. Each story is a single observable change or coherent set of changes a user can verify.

**When to choose:** The change is visible to a user and will be tested by QA. The user describes user-facing behavior, a UI change, or a feature a user interacts with.

### Task

An engineering deliverable that does not go through the Bitwarden QA gate. Tasks cover infrastructure work, refactors, scripts, or changes where the audience is engineers rather than end users. Tasks still carry QA Testing Notes because other teams may use tasks differently.

**When to choose:** The work has no user-facing behavior, or its correctness is verified by automated tests and engineer review rather than manual QA. The user says "refactor", "script", "migration", "internal change", or describes changes not visible to end users.

**Story vs. Task — when it's ambiguous:** Ask. The distinction matters because it determines whether the ticket goes through QA. A good test: "Would a user in production notice any change?" If yes, Story. If no, Task.

### Spike

A time-boxed investigation that produces an artifact — a decision, a document, a proof of concept, a confirmed answer. Spikes do not produce shippable code. Goals/Deliverables replace Acceptance Criteria because the output is knowledge, not behavior.

**When to choose:** The purpose is research, exploration, or answering an open question before implementation can start. The user says "investigate", "explore", "research", "figure out", or "proof of concept".

### Bug

A defect report. The primary artifact is the replication steps. Bugs do not have Acceptance Criteria — the fix is "it behaves as it should." QA Testing Notes carry any nuance that isn't captured by the replication steps.

**When to choose:** Something is broken, behaves incorrectly, or produces an error. The user says "bug", "defect", "broken", "not working", "regression", or describes a difference between expected and actual behavior.

---

## Field Map by Type

The table below shows which Jira fields are available for authoring by ticket type. Fields marked "always" must be filled. Fields marked "when content justifies" are optional. Fields marked "—" are not available or not used.

| Field / Section          | Epic      | Story                  | Task                   | Spike     | Bug                    |
| ------------------------ | --------- | ---------------------- | ---------------------- | --------- | ---------------------- |
| Title                    | always    | always                 | always                 | always    | always                 |
| Links (Jira metadata)    | when used | when used              | when used              | when used | when used              |
| Description (Jira field) | always    | always                 | always                 | always    | always                 |
| Acceptance Criteria      | —         | always                 | always                 | —         | —                      |
| QA Testing Notes         | —         | when content justifies | when content justifies | —         | when content justifies |
| Technical Breakdown      | —         | when content justifies | when content justifies | —         | —                      |
| Goals / Deliverables     | —         | —                      | —                      | always    | —                      |
| Replication Steps        | —         | —                      | —                      | —         | always                 |

**Description field contents** (sections below live inside the Description field in Jira):

| Section                | Epic                   | Story                      | Task                   | Spike                  | Bug                    |
| ---------------------- | ---------------------- | -------------------------- | ---------------------- | ---------------------- | ---------------------- |
| Purpose                | always                 | always                     | always                 | always                 | always                 |
| Goals                  | always                 | —                          | —                      | —                      | —                      |
| Scenarios              | —                      | always (unless suppressed) | —                      | —                      | —                      |
| Scope                  | —                      | when content justifies     | when content justifies | —                      | —                      |
| Risks / Considerations | when content justifies | when content justifies     | when content justifies | when content justifies | when content justifies |
| Questions and Answers  | when content justifies | when content justifies     | when content justifies | when content justifies | when content justifies |
| External References    | when content justifies | when content justifies     | when content justifies | when content justifies | when content justifies |

---

## Purpose Format by Type

The Purpose section appears in the Description field and is always present. Its content varies by type.

**Epic:** A `# Purpose` heading containing a paragraph describing what this epic accomplishes and why.

**Story:** A `# Purpose` heading followed by, in order:

1. (Optional) User Story sentence: `**User Story:** As a [role], I want to [action] so that [outcome].`
2. Purpose paragraph — what this ticket covers and the context a reader needs to complete the work
3. (Optional) `**Feature Flag:** [launchdarkly-flag-value]`
4. (Optional) `**Design:** [Figma title](url)`
5. (Optional) `**Tech Breakdown:** [Confluence document title or PR title](url)`

**Task:** Same as Story but without the User Story sentence.

**Spike:** A `# Purpose` heading containing a paragraph describing what question or problem prompted the spike and what will be possible once it is complete.

**Bug:** A `# Purpose` heading containing a paragraph describing what is broken and where, without restating the replication steps.

---

## Optional Section Decision Guide

Use this when deciding whether to include an optional section:

| Section                | Include when…                                                                               | Skip when…                                                           |
| ---------------------- | ------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Scope                  | The acceptance criteria leaves room for ambiguity about what exactly changes                | The acceptance criteria already makes the deliverable explicit       |
| Risks / Considerations | There is a real risk — performance regression, tech debt, dependency, security, compat      | The work is straightforward with no known risks                      |
| Questions and Answers  | There is an open question for product or design, or a resolved one worth recording          | No decisions were needed beyond the work itself                      |
| External References    | There are relevant Confluence pages, GitHub PRs, or external docs beyond the primary Figma  | Only the primary Figma and tech breakdown exist (already in Purpose) |
| Out of Scope           | A reader could reasonably assume this ticket covers something it does not                   | The scope is obvious from the acceptance criteria                    |
| Stretch Goals          | Work that is related but deliberately deferred due to scope or time                         | There are no deferred items                                          |
| QA Testing Notes       | QA needs context beyond the acceptance criteria to test effectively                         | The acceptance criteria and scenarios are self-sufficient            |
| Technical Breakdown    | The implementation has non-obvious constraints, trade-offs, or dependencies worth capturing | The acceptance criteria implies a straightforward change             |
