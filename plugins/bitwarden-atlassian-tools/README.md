# Bitwarden Atlassian Tools

## Overview

Atlassian access via a custom MCP server providing Jira issue retrieval, JQL search, Confluence page reading, CQL search, and attachment downloads.

Read access is the default and always available. Jira write access (creating work items and links) is **opt-in per install**: `create_issue` and `link_issues` are always listed and their dry-run preview always works, but without `ATLASSIAN_JIRA_WRITE_TOKEN` a live write refuses to execute. Confluence remains read-only with no write path.

## Installation

Configure the following environment variables:

```bash
# Required — Atlassian Cloud ID (find yours at https://bitwarden.atlassian.net/_edge/tenant_info)
export ATLASSIAN_CLOUD_ID="your-cloud-id"
export ATLASSIAN_EMAIL="your-email@company.com"
export ATLASSIAN_JIRA_READ_ONLY_TOKEN="your-jira-scoped-token"
export ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN="your-confluence-scoped-token"

# Optional — enables the Jira write tools (create_issue, link_issues).
# Omit to keep this install read-only.
export ATLASSIAN_JIRA_WRITE_TOKEN="your-jira-write-scoped-token"
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

The Jira Agile (Software) endpoints behind `list_boards`, `get_sprints`, and `get_sprint_issues` require **granular** scopes — the classic `read:jira-work` scope does **not** grant access to the `/rest/agile/1.0` API. Add these granular scopes to the Jira token if you use the board/sprint tools:

| Granular scope                   | Required for                              |
| -------------------------------- | ----------------------------------------- |
| `read:board-scope:jira-software` | `list_boards`                             |
| `read:project:jira`              | `list_boards` (board project details)     |
| `read:sprint:jira-software`      | `get_sprints`, `get_sprint_issues`        |
| `read:issue-details:jira`        | `get_sprint_issues` (issue fields)        |
| `read:jql:jira`                  | `get_sprint_issues` (sprint issue lookup) |

## MCP Tools

### Jira

| Tool                     | Purpose                                                                                                                  |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| `get_issue`              | Read a Jira issue by key or ID                                                                                           |
| `search_issues`          | Search issues using JQL                                                                                                  |
| `get_issue_comments`     | Get comments for an issue                                                                                                |
| `get_issue_remote_links` | Get remote links for an issue (Confluence pages, PRs, external URLs)                                                     |
| `list_projects`          | List accessible Jira projects                                                                                            |
| `list_boards`            | List Agile boards, optionally filtered by project                                                                        |
| `get_sprints`            | List sprints for a board (filter by active/future/closed)                                                                |
| `get_sprint_issues`      | List all issues in a sprint                                                                                              |
| `download_attachment`    | Download a Jira attachment as Base64                                                                                     |
| `get_create_fields`      | Report a project's creatable issue types, and a type's create-screen fields with ids, required flags, and allowed values |

### Jira (write, requires `ATLASSIAN_JIRA_WRITE_TOKEN`)

Both tools default to a dry run that returns the exact payload without sending it. A live write requires an explicit `dryRun: false`. Dry runs need no write token.

| Tool           | Purpose                                                                                                                                                                             |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `create_issue` | Create one work item in any project. Carries no project-specific field knowledge: pass anything beyond the common core through `fields`, keyed by field id from `get_create_fields` |
| `link_issues`  | Link two work items. For a dependency, takes `blockerKey` and `blockedKey` and maps them onto Jira's inward/outward sides internally so the direction cannot be inverted            |

Write tokens need write scopes in addition to the read scopes above:

| Scope                         | Required for                                                                      |
| ----------------------------- | --------------------------------------------------------------------------------- |
| `read:issue:jira`             | `create_issue`                                                                    |
| `read:issue:jira-software`    | `create_issue`                                                                    |
| `write:issue:jira`            | `create_issue`, `link_issues`                                                     |
| `write:issue:jira-software`   | `create_issue`, `link_issues`                                                     |
| `write:issue-link:jira`       | `link_issues`                                                                     |
| `write:comment:jira`          | `create_issue`, `link_issues` (required even though neither tool sends a comment) |
| `write:comment.property:jira` | `create_issue` (required even though it never sends a comment)                    |
| `write:attachment:jira`       | `create_issue` (required even though it never sends an attachment)                |

Grant the **whole** set, not a subset — a token holding only some of them fails every write with `401 Unauthorized; scope does not match`. For a scoped write token covering both write tools, that's:

```
read:issue:jira
read:issue:jira-software
write:attachment:jira
write:comment.property:jira
write:comment:jira
write:issue-link:jira
write:issue:jira-software
write:issue:jira
```

`get_create_fields` needs no additional scope. It calls the createmeta endpoints, which the existing read-only token already satisfies.

Token scope is separate from Jira project permission. Creating also requires the **Create Issues** permission in the target project, and linking requires **Link Issues**. In a project where the user lacks Create Issues, Jira answers `You cannot create issues in this project`, which `get_create_fields` reports as an ordinary result rather than an error.

A leaked write token permits more than these two tools use: `write:comment:jira`, `write:comment.property:jira`, and `write:attachment:jira` are granted only because Atlassian rejects a narrower scope set, so the token can also add comments and attachments across every project the user can reach. Treat this token as higher-blast-radius than the read-only token and rotate it accordingly.

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
- Preview a ticket before creating it: `mcp__bitwarden-atlassian__create_issue` with `project: "PM"`, `issueType: "Story"`, `summary: "Add CSV export to the item list"` — omit `dryRun` (defaults to `true`) to get the payload back without creating anything

## Skills

### `researching-jira-issues`

Orchestrates a deep read of a Jira issue by traversing linked issues, remote links, and supporting Confluence documentation, then synthesizing everything into a structured summary. Triggered by mentioning a Jira issue key with intent to understand it deeply (e.g., "Read PROJ-123", "What's blocking PROJ-123?").

Features:

- Graph traversal with depth control (2 hops) and cycle detection
- Custom field awareness for 16 Bitwarden-specific fields across 6 issue types
- Next-gen epic children discovery via JQL
- Automatic Confluence page follow-through from remote links
- Context budget guidance and graceful degradation

### `filing-jira-tickets`

Files Jira work items that stand on their own. Reads the target project's create screen before drafting, so no project's field layout is assumed, previews each payload before writing it, then wires and verifies dependency links. Triggered by intent to create or link tickets (e.g., "file a bug for this", "create a story for this work", "wire the blocked-by relationship").

Features:

- Discovers issue types, required fields, and allowed values per project rather than hardcoding them, which matters because Bitwarden's projects differ (PM and SM expose an Acceptance criteria field, QA and VULN do not; VULN has no Story type; PLT's only creatable type is `Platform Initiative`)
- Dry-run preview of the exact payload before every live write
- Approval required before each create, unless explicitly told to skip it
- Role-named link arguments (`blockerKey`, `blockedKey`) so dependency direction cannot be inverted

Live creation requires `ATLASSIAN_JIRA_WRITE_TOKEN`; without it the skill can still draft and preview.

## Requirements

- Claude Code with MCP support
- Atlassian API credentials (see Installation)
- Node.js 22+ with [Corepack](https://nodejs.org/api/corepack.html) enabled — on first run the bundled MCP server installs and builds itself with [pnpm](https://pnpm.io/installation) via Corepack
