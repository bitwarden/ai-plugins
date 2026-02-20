---
name: atlassian-reader
description: Reads Jira issues, epics, stories, sprints, boards, and Confluence pages from Atlassian Cloud via MCP tools. Use when the user mentions a Jira ticket (e.g. PROJ-123), references a Confluence page or URL, asks about sprint status, needs epic child stories, or wants to review linked documents for a Jira issue.
---

# Atlassian Reader

Read-only access to Jira and Confluence via the bundled MCP server (`mcp__bitwarden-atlassian__*` tools). All operations are read-only. **Never create, update, or delete any Atlassian resource.**

## 1. Authentication

Auth is handled by the MCP server. The following environment variables must be configured:

| Variable | Purpose |
|---|---|
| `JIRA_URL` | Atlassian instance URL (e.g. `https://bitwarden.atlassian.net`) |
| `JIRA_EMAIL` | Email address associated with the Atlassian account |
| `JIRA_API_TOKEN` | Jira API token with read permissions |
| `CONFLUENCE_URL` | Confluence instance URL (defaults to `JIRA_URL` if not set) |
| `CONFLUENCE_EMAIL` | Confluence email (defaults to `JIRA_EMAIL` if not set) |
| `CONFLUENCE_API_TOKEN` | Confluence API token with read permissions |

**Do not run any verification commands** — go straight to the MCP tool call. If it fails, consult the error handling section (Section 11) to diagnose the cause and guide the user.

**Never expose tokens**: Do not echo, log, or include token values in output when debugging authentication failures. Refer to tokens by variable name only.

## 2. Discovery

Use when the user doesn't specify a project key or space key, or asks what they have access to.

### List Jira Projects

Use `mcp__bitwarden-atlassian__list_projects` with optional `maxResults` parameter.

Present as a table: Key, Name, Type. Use the project key to resolve `{{PROJECT}}` in subsequent JQL queries.

### List Confluence Spaces

Use `mcp__bitwarden-atlassian__list_spaces` with optional `limit` and `type` parameters.

Present as a table: Key, Name, Type. Use the space key to resolve `{{SPACE_KEY}}` in subsequent CQL queries.

## 3. Read Jira Issue

Use when the user references a ticket ID like `PROJ-123`, asks about a story, or wants issue details.

Use `mcp__bitwarden-atlassian__get_issue` with:
- `issueIdOrKey`: the ticket key (e.g. `PROJ-123`)
- `expand`: `["changelog", "renderedFields"]`

**Presentation instructions**:

- **Summary**: Show the issue title, type, status, priority, and assignee prominently
- **Description**: Read `renderedFields.description` (HTML) and present as clean markdown
- **Acceptance Criteria**: Check `renderedFields.customfield_10192` for acceptance criteria content (this is the dedicated A/C field in Bitwarden's Jira instance). If that field is empty or absent, fall back to looking for A/C headings, checklists, or "Acceptance Criteria" sections within the description
- **Children (Epics/Features)**: If the issue type is Epic or Feature, `fields.subtasks` may be empty — next-gen Jira projects use `parent` relationships instead of subtask links. When reading an epic, **always** perform a follow-up JQL search using `parent = {{TICKET_ID}}` (Section 5) to discover child issues
- **Subtasks**: If `fields.subtasks` is non-empty, list each with key, summary, and status
- **Links**: If `fields.issuelinks` is non-empty, list linked issues grouped by link type (e.g. "blocks", "is blocked by", "relates to")
- **Parent**: If `fields.parent` exists, mention the parent epic/story
- **Comments**: Show the last 3 comments (sorted newest first). For each, show author display name, date, and body
- **Never dump raw JSON** unless the user explicitly asks for it

## 4. Read Jira Issue Comments

Use when more comments are needed beyond what the issue endpoint returned, or when the user asks specifically for comment history.

Use `mcp__bitwarden-atlassian__get_issue_comments` with:
- `issueIdOrKey`: the ticket key
- `maxResults`: 10 (default)

**Presentation instructions**:

- Show each comment with: author display name, created date, and body text
- The body is in Atlassian Document Format (ADF) — read the `content` nodes and render as markdown
- If there are more comments than returned, mention the total count from the response

## 5. Search Jira (JQL)

Use when the user asks about sprint contents, epic children, text search across issues, or any bulk issue query.

Use `mcp__bitwarden-atlassian__search_issues` with:
- `jql`: the JQL query string
- `maxResults`: 20 (default)
- `fields`: `["summary", "status", "issuetype", "priority", "assignee", "parent"]` (for search results)

**Common JQL patterns** (suggest these to the user when relevant):

| Use case | JQL |
|---|---|
| Active sprint issues | `project = {{PROJECT}} AND sprint in openSprints()` |
| Epic children (next-gen) | `parent = {{EPIC_KEY}}` |
| Epic children (classic) | `"Epic Link" = {{EPIC_KEY}}` |
| Full text search | `text ~ "{{SEARCH_TERM}}"` |
| Linked issues | `issuekey in linkedIssues({{TICKET_ID}})` |
| My open issues | `assignee = currentUser() AND resolution = Unresolved` |
| Recently updated | `project = {{PROJECT}} AND updated >= -7d ORDER BY updated DESC` |

**Presentation instructions**:

- Present results as a table with columns: Key, Type, Summary, Status, Priority, Assignee
- Include the parent epic key if present
- Note if results were truncated (more results available)

## 6. Read Confluence Page

Use when the user shares a Confluence URL or page ID, or when a Jira issue links to Confluence content.

Use `mcp__bitwarden-atlassian__get_confluence_page` with:
- `pageId`: the numeric page ID
- `includeBody`: true
- `bodyFormat`: `"storage"` (default) or `"view"` for rendered HTML

**Extracting the page ID from a Confluence URL**:

- URL format: `https://domain.atlassian.net/wiki/spaces/SPACE/pages/123456789/Page+Title` → page ID is `123456789`
- URL format: `https://domain.atlassian.net/wiki/x/AbCdEf` → this is a tiny URL; fetch it and extract the page ID from the redirect or resolved content

**Presentation instructions**:

- Show: page title, space name, version number, last modified info
- The body content is HTML — read it and convert to clean markdown in your response
- For large pages, summarize the key sections relevant to the user's current task rather than reproducing the entire page
- If the page contains tables, preserve table formatting

## 7. Search Confluence (CQL)

Use when the user wants to find Confluence pages by keyword, label, or space.

Use `mcp__bitwarden-atlassian__search_confluence_cql` with:
- `cql`: the CQL query string
- `limit`: 10 (default, max 100)
- `start`: pagination offset (default 0)

**Common CQL patterns**:

| Use case | CQL |
|---|---|
| Text search | `text ~ "{{SEARCH_TERM}}"` |
| Space + text | `space = "{{SPACE_KEY}}" AND text ~ "{{SEARCH_TERM}}"` |
| Label filter | `label = "{{LABEL}}"` |
| Space + label | `space = "{{SPACE_KEY}}" AND label = "{{LABEL}}"` |
| Pages under ancestor | `ancestor = {{PAGE_ID}}` |
| Recently modified | `lastModified >= "2024-01-01" AND space = "{{SPACE_KEY}}"` |

**Presentation instructions**:

- List results with: title, space name, type, and URL
- Show total result count and note if truncated

## 8. Confluence Child Pages

Use when the user wants to see subpages under a Confluence page, or when exploring a documentation tree.

Use `mcp__bitwarden-atlassian__get_child_pages` with:
- `pageId`: the parent page ID
- `limit`: 25 (default)

**Presentation instructions**:

- List child pages with: title, page ID, and status
- If there are many children, present as a numbered list

## 9. Boards and Sprints

Use when the user asks about sprint status, board configuration, or wants to see what's in the current sprint.

**Workflow**: To answer "what's in the current sprint?", chain three calls:

### Step 1: List Boards

Use `mcp__bitwarden-atlassian__list_boards` with optional `projectKeyOrId` parameter.

### Step 2: Get Sprints

Use `mcp__bitwarden-atlassian__get_sprints` with:
- `boardId`: from Step 1
- `state`: `"active"` (for current sprint)

### Step 3: Get Sprint Issues

Use `mcp__bitwarden-atlassian__get_sprint_issues` with:
- `sprintId`: from Step 2
- `fields`: `["summary", "status", "issuetype", "priority", "assignee"]`

**Presentation instructions**:

- Show sprint name, goal (if set), start/end dates, and state
- Present sprint issues as a table: Key, Type, Summary, Status, Priority, Assignee
- Group by status if helpful (To Do, In Progress, Done)

## 10. Context Budget Guidance

**Always summarize — never dump raw JSON** unless explicitly asked.

- **Jira issues**: Lead with status, summary, and assignee. Show description as markdown. Append subtasks and links only if present.
- **Confluence pages**: Convert HTML body to markdown. For large pages (>2000 words), summarize sections relevant to the user's current task and offer to read specific sections in detail.
- **Sprint boards**: Present as a status-grouped table. Include completion counts (e.g. "12 of 20 issues done").
- **Search results**: Present as a compact table. Never expand every result — list summaries and let the user pick which to read in full.
- **Comments**: Show the 3 most recent unless the user asks for more.

## 11. Error Handling

MCP tool errors are returned as error responses. Common causes:

| Error Pattern | Meaning | Fix |
|---|---|---|
| Authentication failed | Invalid or expired API token | Ask user to verify the relevant token (`JIRA_API_TOKEN` or `CONFLUENCE_API_TOKEN`). Tokens can be regenerated at [Atlassian API tokens](https://id.atlassian.com/manage-profile/security/api-tokens). |
| Access forbidden | Token is valid but lacks permission | Check that the token has the correct read scope. Verify the user has access to the project/space. |
| Resource not found | Issue, page, or resource does not exist | Verify the ticket ID, page ID, or URL. Check for typos. The resource may have been deleted or moved. |
| Rate limit exceeded | Too many API requests | Wait a moment before retrying. For batch operations, add a small delay between requests. |
| Request failed / connection error | MCP server cannot reach Atlassian | Check that `JIRA_URL` and `CONFLUENCE_URL` are set correctly and the instance is accessible. |

**Never expose tokens**: Do not echo, log, or include token values in output when debugging authentication failures. Refer to tokens by variable name only.

**Wrong token for wrong product**: Jira and Confluence may use separate tokens. If a Jira call fails but the token is valid, verify you're using `JIRA_API_TOKEN` (not the Confluence token) and vice versa.
