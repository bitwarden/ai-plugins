# Bitwarden Atlassian Tools

Read-only Atlassian access (Jira issues, sprints, boards, Confluence pages) plus sprint workability analysis with parallel investigation and categorized reporting.

## Features

### Atlassian Reader

General-purpose read-only access to Jira and Confluence via MCP tools:

- **Jira Issues**: Read issues, comments, attachments, and linked items
- **JQL Search**: Search issues using Jira Query Language
- **Confluence Pages**: Read pages, child pages, and page comments
- **CQL Search**: Search Confluence content using Confluence Query Language
- **Boards & Sprints**: List boards, sprints, and sprint issues
- **Discovery**: List accessible projects and Confluence spaces

### Sprint Workability Analysis

- **Multi-Source Data Retrieval**: Fetches sprint data from Confluence pages and JIRA tickets
- **Intelligent Filtering**: Filters tickets by platform, component, status, and custom criteria
- **Parallel Investigation**: Deploys dedicated subagents for each ticket to maximize throughput
- **Workability Categorization**: Classifies tickets into four actionable categories
- **Flexible Output**: Supports Markdown reports, inline summaries, and structured JSON/YAML

## Installation

Configure the following environment variables:

```bash
export JIRA_URL="https://your-domain.atlassian.net"
export JIRA_EMAIL="your-email@company.com"
export JIRA_API_TOKEN="your-api-token"
export CONFLUENCE_URL="https://your-domain.atlassian.net"  # defaults to JIRA_URL
export CONFLUENCE_EMAIL="your-email@company.com"            # defaults to JIRA_EMAIL
export CONFLUENCE_API_TOKEN="your-api-token"
```

## Usage

### Atlassian Reader (Skill)

The `atlassian-reader` skill activates automatically when you:
- Mention a Jira ticket (e.g. `PROJ-123`)
- Reference a Confluence page or URL
- Ask about sprint status or board contents
- Request epic child stories or linked issues

### Sprint Review (Command)

```bash
/sprint-review --source <confluence-page-id|jira|ticket-list> [options]
```

**Arguments:**
- `--source` (required): Confluence page ID, "jira", or comma-separated ticket keys
- `--sprint`: Sprint identifier (date range or name)
- `--platform`: Filter by component (android, ios, server, web, all)
- `--status`: Filter by status (incomplete, all, or specific status)
- `--output`: Format (markdown, inline, json, yaml)
- `--file`: Output file path

### Natural Language

The plugin responds to natural language queries:
- "Analyze sprint workability"
- "What's blocking the sprint?"
- "Show me PROJ-123"
- "Find Confluence pages about architecture"

## Workability Categories

| Category | Description | Recommended Action |
|----------|-------------|-------------------|
| **BLOCKED** | Cannot proceed without external resolution | Escalate or defer |
| **STALLED** | Work complete but ticket still open | Update status, close |
| **NEEDS_CLARIFICATION** | Missing info or ambiguous requirements | PM/Owner outreach |
| **IN_PROGRESS** | Active work with clear path | Monitor |

## Components

### Skills

| Skill | Purpose |
|-------|---------|
| `atlassian-reader` | General-purpose Atlassian read access via MCP tools |
| `sprint-workability` | Main orchestration skill for sprint analysis |
| `parsing-sprint-data` | Extract tickets from Confluence |
| `categorizing-workability` | Classify investigation results |
| `generating-report` | Format output in various formats |
| `analyzing-requirements` | Evaluate ticket requirement clarity and completeness |

### Agents

| Agent | Purpose |
|-------|---------|
| `ticket-investigator` | Deep investigation of individual tickets |

### Commands

| Command | Purpose |
|---------|---------|
| `/sprint-review` | CLI interface for sprint analysis |

### MCP Tools (14 total)

| Tool | Purpose |
|------|---------|
| `get_issue` | Read a Jira issue by key or ID |
| `search_issues` | Search issues using JQL |
| `get_issue_comments` | Get comments for an issue |
| `download_attachment` | Download a Jira attachment |
| `get_confluence_page` | Read a Confluence page by ID |
| `search_confluence` | Search Confluence by space/title (v2 API) |
| `search_confluence_cql` | Search Confluence using CQL (v1 API) |
| `get_confluence_page_comments` | Get comments on a Confluence page |
| `get_child_pages` | Get child pages of a Confluence page |
| `list_boards` | List Jira boards |
| `get_sprints` | Get sprints for a board |
| `get_sprint_issues` | Get issues in a sprint |
| `list_projects` | List accessible Jira projects |
| `list_spaces` | List accessible Confluence spaces |

## Performance

| Metric | Value |
|--------|-------|
| Parallel investigations | Up to 20+ simultaneous |
| 10-ticket analysis time | ~3-5 minutes |
| Context preservation | Via subagent delegation |

## Requirements

- Claude Code with Task tool support
- JIRA/Confluence API credentials (see Installation)

## License

MIT License - See repository root for details.
