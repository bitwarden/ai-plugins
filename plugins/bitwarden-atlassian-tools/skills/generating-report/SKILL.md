---
name: Generating Report
description: |
  This skill should be used when the user needs to "generate sprint report",
  "create workability report", "format analysis output", "write sprint summary",
  or requires transformation of categorized workability results into actionable
  reports (Markdown, JSON, YAML, or inline summary formats).
version: 1.0.0
---

# Generating Report

## Purpose

Transform categorized workability results into actionable reports, supporting
multiple output formats for different use cases.

## Output Formats

### Format 1: Markdown Report

Full detailed report suitable for documentation and sharing.

**Template**:

```markdown
# Sprint Workability Analysis Report

**Sprint**: {sprint_identifier}
**Analysis Date**: {timestamp}
**Platform Filter**: {platform}
**Tickets Analyzed**: {total_count}

## Executive Summary

| Category | Count | Percentage |
|----------|-------|------------|
| BLOCKED | {blocked_count} | {blocked_pct}% |
| STALLED | {stalled_count} | {stalled_pct}% |
| NEEDS CLARIFICATION | {clarify_count} | {clarify_pct}% |
| IN PROGRESS | {progress_count} | {progress_pct}% |

**Sprint Health Score**: {health_score}/100
**Immediate Actions Required**: {action_count}

## Category Details

### BLOCKED (External/Architectural)

{for each blocked ticket}
#### {ticket_key}: {summary}
- **Status**: {status}
- **Assignee**: {assignee}
- **Blocker**: {blocker_description}
- **Blocked Since**: {blocked_date}
- **Recommendation**: {recommendation}
{end for}

### STALLED (Awaiting Closure)
...

### NEEDS CLARIFICATION
...

### IN PROGRESS
...

## Prioritized Recommendations

### Immediate Actions (This Week)
1. {high_priority_action_1}
2. {high_priority_action_2}

### Short-term Actions (This Sprint)
1. {medium_priority_action_1}

### Process Improvements
1. {process_improvement_1}

## Appendix

### Analysis Methodology
- Data Source: {source_type} ({source_id})
- Filters Applied: {filters}
- Investigation Depth: Full (comments, linked issues, requirements)

### Ticket Details
{detailed ticket data table}
```

---

### Format 2: Inline Summary

Brief summary for chat/standup contexts.

**Template**:

```
Sprint Analysis: {sprint_identifier} ({platform})

{total_count} tickets analyzed:
- {blocked_count} BLOCKED: {blocked_keys}
- {stalled_count} STALLED: {stalled_keys}
- {clarify_count} NEEDS CLARIFICATION: {clarify_keys}
- {progress_count} IN PROGRESS: {progress_keys}

Top 3 Actions:
1. {action_1}
2. {action_2}
3. {action_3}
```

---

### Format 3: JSON Output

Structured data for programmatic consumption. See schema in references.

---

### Format 4: YAML Output

Human-readable structured format. See template in references.

## Report Generation Guidelines

### For Large Reports (10+ tickets)
- Delegate final report writing to a subagent
- This preserves main conversation context
- Use Task tool with detailed formatting instructions

### Content Guidelines
- Executive summary should fit in one screen
- Recommendations must be actionable (who, what, when)
- Include ticket links for easy navigation
- Metrics should highlight health/risk

### File Output
- When `--file` specified, write to path using Write tool
- Confirm file creation with path and size
- Offer to open in editor if requested
