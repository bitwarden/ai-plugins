---
name: analyzing-requirements
description: |
  Use this skill when analyzing JIRA ticket requirements for clarity, completeness, and implementation readiness.
  Apply this rubric after retrieving ticket data via get_issue and get_issue_comments to produce a structured
  requirements_analysis object. This replaces automated keyword matching with Claude's natural language understanding.
---

# Analyzing Requirements

## Purpose

Evaluate a JIRA ticket's requirements quality to determine if it is ready for implementation. This skill provides the rubric for producing the `requirements_analysis` section of a ticket investigation report.

## When to Use

Apply this rubric whenever you have retrieved a ticket's full details (description, comments, linked issues) and need to assess requirement clarity. You do NOT need a separate tool call — analyze the data you already have.

## Analysis Rubric

Evaluate each ticket across these five dimensions. For each dimension, record whether it passes and note specific evidence.

### 1. Description Quality

**Passes if:** The ticket has a description longer than 50 characters that explains what needs to be done.

Evaluate:
- Is the description present and non-trivial (not just a copy of the summary)?
- Does it explain the problem or goal, not just the solution?
- Does it provide enough context for someone unfamiliar with the codebase?

### 2. Acceptance Criteria

**Passes if:** The ticket contains explicit acceptance criteria in any recognized format.

Look for:
- A section labeled "Acceptance Criteria", "AC", "Definition of Done", or "Success Criteria"
- BDD format: "Given... When... Then..." patterns
- Checkbox lists: `- [ ]` or `- [x]` items describing verifiable outcomes
- Numbered lists of expected behaviors or test scenarios

Also check comments — acceptance criteria are sometimes clarified in discussion rather than the description.

### 3. Technical Details

**Passes if:** The ticket includes implementation-relevant technical information.

Look for:
- References to specific components, classes, functions, APIs, or endpoints
- Architecture or design considerations
- Database schema changes or migration notes
- Keywords: technical, implementation, architecture, api, database, design, component, endpoint, schema, migration

**Exception:** Epic-type issues are not expected to have technical details — skip this dimension for Epics.

### 4. Comment Activity

Record:
- Total comment count
- Date of most recent comment
- Whether comments contain blocker mentions ("waiting on", "blocked by", "depends on")
- Whether comments contain completion signals ("done", "merged", "deployed", "resolved")
- Whether comments clarify requirements that were missing from the description

### 5. Linked Issues

Record:
- Count of blocking/blocked-by relationships
- Whether blocking issues are resolved
- Whether there are unresolved dependencies

## Scoring

Count the number of **missing elements** from dimensions 1-3:

| Missing Elements | Clarity Score | Meaning |
|---|---|---|
| 0 | `CLEAR` | Ready for implementation |
| 1 | `PARTIAL` | Needs clarification before implementation |
| 2+ | `UNCLEAR` | Blocked until requirements are clarified |

## Output Format

Produce a `requirements_analysis` object matching this structure:

```json
{
  "completeness_score": 75,
  "has_description": true,
  "has_acceptance_criteria": false,
  "has_technical_details": true,
  "comment_count": 8,
  "clarity": "PARTIAL",
  "missing_elements": ["Clear acceptance criteria"],
  "suggestions": [
    "Add Given-When-Then format acceptance criteria",
    "Clarify expected behavior for edge cases"
  ]
}
```

### Field Definitions

- **completeness_score** (0-100): Percentage based on passing dimensions. With 3 dimensions, each is worth ~33 points. Add up to 1 bonus point per active comment that clarifies requirements.
- **has_description**: Boolean — description exists and is >50 characters
- **has_acceptance_criteria**: Boolean — any recognized AC format found in description or comments
- **has_technical_details**: Boolean — technical implementation details present (always true for Epics)
- **comment_count**: Total number of comments on the ticket
- **clarity**: One of `CLEAR`, `PARTIAL`, `UNCLEAR` per scoring table above
- **missing_elements**: List of specific things that are absent
- **suggestions**: Actionable recommendations for improving the ticket, tailored to what's actually missing

### Generating Suggestions

Tailor suggestions to what is specifically missing:

- **Missing description**: "Expand description with problem context, user impact, and background"
- **Missing acceptance criteria**: "Add Given-When-Then format acceptance criteria" or "Add a checklist of verifiable outcomes"
- **Missing technical details**: "Include technical approach, affected components, and API changes"
- **Zero comments on unclear ticket**: "Ticket has no discussion — consider requesting clarification from the reporter"
- **Stale ticket (no updates >30 days)**: "Ticket has not been updated recently — verify requirements are still current"

## Integration with Ticket Investigation

This rubric is applied during Step 4 of the ticket-investigator protocol. The agent should:

1. Retrieve the ticket via `get_issue` (Step 1 — already done)
2. Retrieve comments via `get_issue_comments` (Step 2 — already done)
3. Apply this rubric to the retrieved data (no additional API calls needed)
4. Include the `requirements_analysis` object in the investigation output
