---
name: sprint-review
description: Analyze sprint tickets for workability and generate actionable reports
---

# Sprint Review Command

Analyzes sprint tickets for workability status. Identifies blockers, stalled work,
and tickets requiring clarification.

## Usage

```
/sprint-review --source <confluence-page-id|jira|ticket-list> [options]
```

## Arguments

### --source (required)
The data source for sprint tickets:
- **Confluence Page ID**: Numeric ID of a Confluence page containing sprint data
- **"jira"**: Use JIRA sprint directly (requires --sprint)
- **Ticket List**: Comma-separated ticket keys (e.g., "PM-123,PM-456")

### --sprint
Sprint identifier for filtering:
- Date range: "Dec 15-26", "2024-01-01 to 2024-01-14"
- Sprint name: "Sprint 42", "PI 24.4"
- Required when source is "jira"

### --platform
Filter tickets by platform component:
- `android` - Android component only
- `ios` - iOS component only
- `server` - Server/Backend components
- `web` - Web/Frontend components
- `all` - No filtering (default)

### --status
Filter tickets by status:
- `incomplete` - Exclude "Done" tickets (default)
- `all` - Include all statuses
- Specific status: "In Progress", "On Hold", etc.

### --output
Output format:
- `markdown` - Full markdown report (default)
- `inline` - Brief inline summary
- `json` - Structured JSON output
- `yaml` - Structured YAML output

### --file
Output file path. If not specified, output is returned inline.

## Examples

### Analyze Android tickets from Confluence sprint page
```
/sprint-review --source 2270330935 --sprint "Dec 15-26" --platform android
```

### Analyze specific tickets with JSON output
```
/sprint-review PM-12345,PM-12346,PM-12347 --output json
```

### Full sprint analysis to file
```
/sprint-review --source jira --sprint "Sprint 42" --file ./sprint-42-analysis.md
```

## Workflow

When invoked, this command:
1. Retrieves sprint data from the specified source
2. Filters tickets based on platform and status criteria
3. Deploys parallel investigation agents for each ticket
4. Categorizes tickets into workability groups
5. Generates report in requested format
