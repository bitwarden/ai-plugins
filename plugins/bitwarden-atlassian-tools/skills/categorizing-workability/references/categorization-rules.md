# Categorization Rules Reference

## Quick Reference Table

| Category | Key Signals | Priority Action |
|----------|-------------|-----------------|
| BLOCKED | Unresolved blockers, external deps | Escalate |
| STALLED | Work done, ticket open | Close/Update |
| NEEDS_CLARIFICATION | Missing reqs, no assignee | Clarify/Assign |
| IN_PROGRESS | Active work, no blockers | Monitor |

## Signal Keywords

### BLOCKED Signals
- "waiting on"
- "blocked by"
- "depends on"
- "need approval"
- "external team"

### STALLED Signals
- "PR merged"
- "deployed"
- "code complete"
- "ready for release"

### NEEDS_CLARIFICATION Signals
- "unclear"
- "need more info"
- "missing requirements"
- "TBD"
- "to be discussed"

## Threshold Values

| Metric | Threshold | Impact |
|--------|-----------|--------|
| Days since update | > 14 | Stalled indicator |
| Requirements completeness | < 60% | Needs clarification |
| Days on hold | > 30 | Outdated hold |
| Recent activity window | 7 days | Active indicator |
