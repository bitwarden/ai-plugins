# Bitwarden Atlassian Tools

## Overview

Read-only Jira access via a custom MCP server providing issue retrieval, JQL search, comment reading, and project discovery. All operations are read-only — the server never creates, updates, or deletes Jira resources.

## Installation

Configure the following environment variables:

```bash
export ATLASSIAN_JIRA_URL="https://your-domain.atlassian.net"
export ATLASSIAN_EMAIL="your-email@company.com"
export ATLASSIAN_JIRA_READ_ONLY_TOKEN="your-api-token"
```

## MCP Tools

| Tool | Purpose |
|------|---------|
| `get_issue` | Read a Jira issue by key or ID |
| `search_issues` | Search issues using JQL |
| `get_issue_comments` | Get comments for an issue |
| `list_projects` | List accessible Jira projects |

## Usage

The MCP tools are available as `mcp__bitwarden-atlassian__<tool_name>`. Examples:

- Read an issue: `mcp__bitwarden-atlassian__get_issue` with `issueIdOrKey: "PROJ-123"`
- Search with JQL: `mcp__bitwarden-atlassian__search_issues` with `jql: "project = PROJ AND status = Open"`
- List projects: `mcp__bitwarden-atlassian__list_projects`

## Requirements

- Claude Code with MCP support
- Jira API credentials (see Installation)

## License

MIT License - See repository root for details.
