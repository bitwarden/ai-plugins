# Bitwarden Atlassian Tools

## Overview

Read-only Atlassian access via a custom MCP server providing Jira issue retrieval, JQL search, Confluence page reading, CQL search, and attachment downloads. All operations are read-only — the server never creates, updates, or deletes any Atlassian resource.

## Installation

Configure the following environment variables:

```bash
# Required — Atlassian Cloud ID (find yours at https://your-domain.atlassian.net/_edge/tenant_info)
export ATLASSIAN_CLOUD_ID="your-cloud-id"
export ATLASSIAN_EMAIL="your-email@company.com"
export ATLASSIAN_JIRA_READ_ONLY_TOKEN="your-jira-scoped-token"
export ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN="your-confluence-scoped-token"
```

API requests are routed through the Atlassian API gateway (`api.atlassian.com`), which supports both classic and scoped API tokens.

### Required Atlassian Permissions

Use **scoped (granular) API tokens** for least-privilege access. Create them at [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens). Scoped tokens require the API gateway (`api.atlassian.com`) and your Cloud ID.

#### Confluence token scopes

| Scope                                  | Required for                                       |
| -------------------------------------- | -------------------------------------------------- |
| `read:space:confluence`                | Space listing and metadata                         |
| `read:space.property:confluence`       | Space property access                              |
| `read:page:confluence`                 | Page retrieval by ID                               |
| `read:label:confluence`                | Label metadata on pages                            |
| `read:hierarchical-content:confluence` | Child page navigation                              |
| `read:folder:confluence`               | Folder content access                              |
| `read:embed:confluence`                | Embedded content rendering                         |
| `read:custom-content:confluence`       | Custom content types                               |
| `read:content.property:confluence`     | Content properties                                 |
| `read:content:confluence`              | Pages, blogposts, attachments, comments, templates |
| `read:content-details:confluence`      | Content details and associated properties          |
| `read:confluence-space.summary`        | Space summary information                          |
| `read:confluence-props`                | Confluence properties                              |
| `read:confluence-content.summary`      | Content summaries                                  |
| `read:confluence-content.all`          | Full content including body text                   |
| `read:comment:confluence`              | Page comments (footer and inline)                  |
| `read:blogpost:confluence`             | Blog post content                                  |
| `read:attachment:confluence`           | Attachment metadata and downloads                  |
| `read:account`                         | User display names on content                      |

#### Jira token scopes

| Scope            | Required for                              |
| ---------------- | ----------------------------------------- |
| `read:jira-work` | Issues, comments, projects, attachments   |
| `read:jira-user` | User display names on issues and comments |

## MCP Tools

### Jira

| Tool                     | Purpose                                                              |
| ------------------------ | -------------------------------------------------------------------- |
| `get_issue`              | Read a Jira issue by key or ID                                       |
| `search_issues`          | Search issues using JQL                                              |
| `get_issue_comments`     | Get comments for an issue                                            |
| `get_issue_remote_links` | Get remote links for an issue (Confluence pages, PRs, external URLs) |
| `list_projects`          | List accessible Jira projects                                        |
| `download_attachment`    | Download a Jira attachment as Base64                                 |

### Confluence

| Tool                           | Purpose                              |
| ------------------------------ | ------------------------------------ |
| `get_confluence_page`          | Read a Confluence page by ID         |
| `get_confluence_page_comments` | Get comments on a Confluence page    |
| `get_child_pages`              | Get child pages of a Confluence page |
| `search_confluence`            | Search Confluence by space/title     |
| `search_confluence_cql`        | Search Confluence using CQL          |
| `list_spaces`                  | List accessible Confluence spaces    |

## Usage

The MCP tools are available as `mcp__bitwarden-atlassian__<tool_name>`. Examples:

- Read an issue: `mcp__bitwarden-atlassian__get_issue` with `issueIdOrKey: "PROJ-123"`
- Search with JQL: `mcp__bitwarden-atlassian__search_issues` with `jql: "project = PROJ AND status = Open"`
- Read a Confluence page: `mcp__bitwarden-atlassian__get_confluence_page` with `pageId: "123456789"`
- Search Confluence: `mcp__bitwarden-atlassian__search_confluence_cql` with `cql: "space = EN AND text ~ \"search term\""`

## Skills

### `researching-jira-issues`

Orchestrates a deep read of a Jira issue by traversing linked issues, remote links, and supporting Confluence documentation, then synthesizing everything into a structured summary. Triggered by mentioning a Jira issue key with intent to understand it deeply (e.g., "Read PROJ-123", "What's blocking PROJ-123?").

Features:

- Graph traversal with depth control (2 hops) and cycle detection
- Custom field awareness for 16 Bitwarden-specific fields across 6 issue types
- Next-gen epic children discovery via JQL
- Automatic Confluence page follow-through from remote links
- Context budget guidance and graceful degradation

## Requirements

- Claude Code with MCP support
- Atlassian API credentials (see Installation)
