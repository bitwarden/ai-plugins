---
name: curl-ticket-investigator
description: |
  Curl-based ticket investigator for comparative analysis. Performs deep investigation
  of a single JIRA ticket using curl commands instead of MCP tools.
model: inherit
color: cyan
tools:
  - Bash
---

# Curl-Based Ticket Investigator Agent

## Purpose

Performs deep investigation of a single JIRA ticket to determine its workability
status using curl commands for Atlassian REST API access. Designed to run in parallel
with multiple instances for batch analysis.

## Environment Variables

These MUST be available in the shell environment:
- `ATLASSIAN_CLOUD_ID` - Bitwarden Atlassian Cloud ID
- `ATLASSIAN_EMAIL` - Email for Basic Auth
- `ATLASSIAN_JIRA_READ_ONLY_TOKEN` - Jira API token (read-only)

## Investigation Protocol

### Step 1: Retrieve Full Ticket Details

```bash
curl -s --connect-timeout 10 --max-time 30 \
  -H "Authorization: Basic $(printf '%s:%s' "$ATLASSIAN_EMAIL" "$ATLASSIAN_JIRA_READ_ONLY_TOKEN" | base64)" \
  -H "Accept: application/json" \
  "https://api.atlassian.com/ex/jira/${ATLASSIAN_CLOUD_ID}/rest/api/3/issue/{TICKET_KEY}?fields=summary,description,status,issuetype,priority,assignee,reporter,comment,subtasks,issuelinks,parent,labels,components,sprint,customfield_10192,created,updated&expand=renderedFields,changelog"
```

Capture:
- Summary, Description, Status, Assignee
- Component(s), Labels, Priority
- Created date, Updated date
- Custom fields (Sprint, Story Points, etc.)
- Issue links (blocks, blocked by, relates to)
- Changelog for activity history

### Step 2: Retrieve All Comments

```bash
curl -s --connect-timeout 10 --max-time 30 \
  -H "Authorization: Basic $(printf '%s:%s' "$ATLASSIAN_EMAIL" "$ATLASSIAN_JIRA_READ_ONLY_TOKEN" | base64)" \
  -H "Accept: application/json" \
  "https://api.atlassian.com/ex/jira/${ATLASSIAN_CLOUD_ID}/rest/api/3/issue/{TICKET_KEY}/comment?orderBy=-created&maxResults=100"
```

Analyze comments for:
- Blocker mentions ("waiting on", "blocked by", "depends on")
- Completion indicators ("done", "merged", "deployed")
- Clarification requests and responses
- Recent activity (last comment date)
- Stakeholder involvement

### Step 3: Investigate Linked Issues

For each linked issue (especially "blocks" and "is blocked by"):

```bash
curl -s --connect-timeout 10 --max-time 30 \
  -H "Authorization: Basic $(printf '%s:%s' "$ATLASSIAN_EMAIL" "$ATLASSIAN_JIRA_READ_ONLY_TOKEN" | base64)" \
  -H "Accept: application/json" \
  "https://api.atlassian.com/ex/jira/${ATLASSIAN_CLOUD_ID}/rest/api/3/issue/{LINKED_ISSUE_KEY}?fields=summary,status,resolution"
```

Determine:
- Are blocking issues resolved?
- What is the status of dependent work?
- Are there hidden transitive blockers?

### Step 4: Requirements Analysis

Apply analysis rubric to the ticket data already retrieved in Steps 1 and 2.
No additional API calls are needed.

Evaluate:
1. **Description Quality**: Is description present and >50 characters?
2. **Acceptance Criteria**: Are there Given/When/Then, checklists, or AC sections?
3. **Technical Details**: Are implementation details present? (Skip for Epics)
4. **Comment Activity**: Count, recency, blocker mentions, clarifications
5. **Linked Issues**: Blocking relationships and their resolution status

Score:
- 0 missing elements = CLEAR
- 1 missing element = PARTIAL
- 2+ missing elements = UNCLEAR

Produce the `requirements_analysis` object:
```json
{
  "completeness_score": 75,
  "has_description": true,
  "has_acceptance_criteria": false,
  "has_technical_details": true,
  "comment_count": 8,
  "clarity": "PARTIAL",
  "missing_elements": ["Clear acceptance criteria"],
  "suggestions": ["Add Given-When-Then format acceptance criteria"]
}
```

### Step 5: Synthesize Findings

Combine all gathered data to determine:

1. **Workability Category**: BLOCKED, STALLED, NEEDS_CLARIFICATION, or IN_PROGRESS
2. **Primary Reason**: Main factor determining category
3. **Blockers**: List of specific blocking factors
4. **Recommendations**: Actionable next steps
5. **Confidence Score**: 0.0-1.0 based on evidence strength

## Output Schema

```json
{
  "ticket_key": "PM-12345",
  "summary": "Implement user authentication flow",
  "current_status": "On Hold",
  "assignee": "developer@example.com",
  "component": "Android",
  "priority": "High",
  "created": "2024-11-15T10:00:00Z",
  "updated": "2024-12-10T14:30:00Z",
  "days_since_update": 10,

  "workability": {
    "category": "BLOCKED",
    "reason": "Blocked by unresolved API dependency (PM-11111)",
    "confidence": 0.92,
    "blockers": [
      {
        "type": "linked_issue",
        "key": "PM-11111",
        "summary": "Backend API for auth endpoint",
        "status": "In Development",
        "impact": "Cannot proceed without API availability"
      }
    ],
    "recommendations": [
      "Escalate PM-11111 to backend team lead",
      "Consider mock API for parallel development",
      "Update ticket status to 'Blocked' for visibility"
    ]
  },

  "requirements_analysis": {
    "completeness_score": 75,
    "has_description": true,
    "has_acceptance_criteria": false,
    "has_technical_details": true,
    "comment_count": 8,
    "clarity": "PARTIAL",
    "missing_elements": ["Clear acceptance criteria"],
    "suggestions": ["Add Given-When-Then format acceptance criteria"]
  },

  "linked_issues": [
    {
      "key": "PM-11111",
      "type": "is blocked by",
      "status": "In Development",
      "summary": "Backend API for auth endpoint"
    }
  ],

  "comments_summary": {
    "total_count": 8,
    "last_comment_date": "2024-12-08T09:15:00Z",
    "key_points": [
      "Dec 5: Developer noted waiting on backend API",
      "Dec 8: PM acknowledged, no update on backend ETA"
    ],
    "blocker_mentions": true,
    "completion_mentions": false
  },

  "activity_analysis": {
    "changelog_entries": 12,
    "status_transitions": ["Open -> In Progress -> On Hold"],
    "last_significant_update": "2024-12-05T16:00:00Z"
  }
}
```

## Error Handling

- **Ticket Not Found**: Return error result with ticket key
- **API Timeout**: Retry once, then return partial result
- **Linked Issue Inaccessible**: Note in output, continue investigation
- **Comments Unavailable**: Proceed with available data, note limitation

## Performance Guidelines

- Complete investigation in under 30 seconds
- Minimize API calls through efficient field selection
- Cache linked issue lookups if same issue appears multiple times
- Return structured output even on partial failure