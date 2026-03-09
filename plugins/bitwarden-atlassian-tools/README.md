# Bitwarden Atlassian Tools

## Overview

Read-only Atlassian access via a custom MCP server providing Jira issue retrieval, JQL search, Confluence page reading, CQL search, and attachment downloads. All operations are read-only — the server never creates, updates, or deletes any Atlassian resource.

## Installation

Configure the following environment variables:

```bash
# Required — Atlassian Cloud ID (find yours at https://your-domain.atlassian.net/_edge/tenant_info)
export ATLASSIAN_CLOUD_ID="your-cloud-id"
export ATLASSIAN_EMAIL="your-email@company.com"
export ATLASSIAN_JIRA_READ_ONLY_TOKEN="your-api-token"

# Optional — Confluence token (falls back to Jira token if not set)
export ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN="your-api-token"
```

API requests are routed through the Atlassian API gateway (`api.atlassian.com`), which supports both classic and scoped API tokens.

### Required Atlassian Permissions

Use **scoped (granular) API tokens** for least-privilege access. Create them at [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens) and grant the following scopes:

| Scope | Required for |
|-------|-------------|
| `read:jira-work` | Issues, comments, projects, attachments, boards, sprints |
| `read:jira-user` | User display names on issues and comments |
| `read:confluence-content.all` | Pages, comments, child pages |
| `read:confluence-space.summary` | Space listing |
| `search:confluence` | CQL and title/space search |

Classic (non-scoped) API tokens also work but inherit full account permissions, which is broader than necessary.

## MCP Tools

### Jira

| Tool | Purpose |
|------|---------|
| `get_issue` | Read a Jira issue by key or ID |
| `search_issues` | Search issues using JQL |
| `get_issue_comments` | Get comments for an issue |
| `list_projects` | List accessible Jira projects |
| `download_attachment` | Download a Jira attachment as Base64 |

### Confluence

| Tool | Purpose |
|------|---------|
| `get_confluence_page` | Read a Confluence page by ID |
| `get_confluence_page_comments` | Get comments on a Confluence page |
| `get_child_pages` | Get child pages of a Confluence page |
| `search_confluence` | Search Confluence by space/title |
| `search_confluence_cql` | Search Confluence using CQL |
| `list_spaces` | List accessible Confluence spaces |

## Usage

The MCP tools are available as `mcp__bitwarden-atlassian__<tool_name>`. Examples:

- Read an issue: `mcp__bitwarden-atlassian__get_issue` with `issueIdOrKey: "PROJ-123"`
- Search with JQL: `mcp__bitwarden-atlassian__search_issues` with `jql: "project = PROJ AND status = Open"`
- Read a Confluence page: `mcp__bitwarden-atlassian__get_confluence_page` with `pageId: "123456789"`
- Search Confluence: `mcp__bitwarden-atlassian__search_confluence_cql` with `cql: "space = EN AND text ~ \"search term\""`

## Requirements

- Claude Code with MCP support
- Atlassian API credentials (see Installation)

## License

MIT License - See repository root for details.
