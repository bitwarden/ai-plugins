---
name: Categorizing Workability
description: |
  This skill should be used when the user needs to "categorize tickets",
  "classify ticket workability", "determine ticket status categories",
  or requires classification of investigation results into workability
  categories (BLOCKED, STALLED, NEEDS_CLARIFICATION, IN_PROGRESS).
version: 1.0.0
---

# Categorizing Workability

## Purpose

Apply consistent categorization rules to classify tickets into actionable
workability categories, enabling prioritized response.

## Categories

### BLOCKED (External/Architectural)

**Definition**: Ticket cannot proceed without resolution of external factors.

**Criteria** (any of):
- Explicit blocker linked issue in "Blocks" relationship
- Comments mentioning waiting on external team
- Dependency on unreleased infrastructure/services
- Architectural constraint requiring design decision
- Third-party integration pending (API access, licenses, etc.)
- Security/Compliance review pending

**Indicators in Data**:
- `issuelinks` with type "is blocked by" and unresolved target
- Comments containing: "waiting on", "blocked by", "depends on", "need X team"
- Status = "Blocked" or custom "External Dependency" status
- Labels: "blocked", "external-dependency", "waiting"

**Recommended Actions**:
- Escalate to relevant stakeholders
- Add to impediment log
- Consider removing from sprint if unresolvable

---

### STALLED (Awaiting Closure)

**Definition**: Work is substantially complete but ticket remains open.

**Criteria** (any of):
- PR merged but ticket not moved to Done
- All acceptance criteria met per comments
- "Ready for QA" but no QA activity in 7+ days
- Code complete, awaiting deployment
- Completed work documented but status not updated

**Indicators in Data**:
- Changelog shows no updates in 14+ days
- Comments indicate "PR merged", "deployed", "done"
- Linked PRs in merged state
- Subtasks all complete but parent open
- Status = "In Review" with no recent activity

**Recommended Actions**:
- Quick wins: update status, close tickets
- Verify completion with assignee
- Check if QA bottleneck exists

---

### NEEDS_CLARIFICATION

**Definition**: Ticket cannot be worked effectively due to ambiguity or missing information.

**Criteria** (any of):
- Requirements analysis shows low completeness score
- Missing acceptance criteria
- Unassigned with no recent activity
- "On Hold" status with outdated hold reason
- Conflicting requirements in comments
- Scope ambiguity (unclear what "done" means)
- Missing technical specifications

**Indicators in Data**:
- `mcp__bitwarden-atlassian__analyze_requirements` completeness < 60%
- Description is empty or minimal
- No acceptance criteria field populated
- Assignee is null/empty
- Status = "On Hold" with last update > 30 days
- Comments asking clarifying questions without answers

**Recommended Actions**:
- PM/Owner outreach for clarification
- Refinement session scheduling
- Consider moving to backlog if not sprint-critical

---

### IN_PROGRESS

**Definition**: Active work underway with clear path to completion.

**Criteria** (all of):
- Assigned to active team member
- Recent activity (update within 7 days)
- Clear requirements and acceptance criteria
- No blocking dependencies identified
- Status indicates active work ("In Progress", "In Development")

**Indicators in Data**:
- Recent changelog entries
- Assignee is active team member
- No "is blocked by" links to unresolved issues
- Requirements analysis completeness >= 70%
- Comments show ongoing work discussion

**Recommended Actions**:
- No action needed
- Monitor for blockers emerging
- Track toward completion

## Categorization Algorithm

```
function categorize(investigationResult):
    # Check for blocking conditions first (highest priority)
    if hasUnresolvedBlockingIssues(investigationResult):
        return BLOCKED
    if hasExternalDependencyIndicators(investigationResult):
        return BLOCKED

    # Check for stalled conditions
    if isWorkComplete(investigationResult) and statusNotDone:
        return STALLED
    if daysSinceLastUpdate > 14 and statusIndicatesActive:
        return STALLED

    # Check for clarification needs
    if requirementsCompleteness < 60%:
        return NEEDS_CLARIFICATION
    if isUnassigned and daysSinceCreation > 7:
        return NEEDS_CLARIFICATION
    if statusOnHold and holdReasonOutdated:
        return NEEDS_CLARIFICATION

    # Default to in progress
    return IN_PROGRESS
```

## Output Format

```json
{
  "categorization": {
    "BLOCKED": {
      "count": 3,
      "percentage": 30,
      "tickets": [
        {
          "key": "PM-12345",
          "reason": "Blocked by PM-11111 (external API dependency)",
          "blocker_details": "...",
          "recommendation": "Escalate to Platform team"
        }
      ]
    },
    "STALLED": { ... },
    "NEEDS_CLARIFICATION": { ... },
    "IN_PROGRESS": { ... }
  },
  "metrics": {
    "total_analyzed": 10,
    "actionable_count": 9,
    "health_score": 0.10
  }
}
```

## Prioritization Within Categories

### BLOCKED Priority
1. Age of blocker (older = higher priority)
2. Business criticality of blocked ticket
3. Number of dependent tickets

### STALLED Priority
1. Effort to close (lower effort = higher priority)
2. Sprint commitment status
3. Age since completion

### NEEDS_CLARIFICATION Priority
1. Sprint commitment status
2. Business criticality
3. Estimated clarification effort
