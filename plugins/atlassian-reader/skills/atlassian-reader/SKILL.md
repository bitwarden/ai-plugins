---
name: atlassian-reader
description: Reads Jira issues, epics, stories, sprints, boards, and Confluence pages from Atlassian Cloud into context via READ-ONLY scoped API tokens and curl commands. Use when the user mentions a Jira ticket (e.g. PROJ-123), references a Confluence page or URL, asks about sprint status, needs epic child stories, or wants to review linked documents for a Jira issue.
---

# Atlassian Reader

Read-only access to Jira and Confluence via Atlassian Cloud REST APIs using **scoped read-only API tokens**. All operations use curl with Basic Auth through the Atlassian API gateway (`api.atlassian.com`). **Never create, update, or delete any Atlassian resource.**

## 1. Environment Variables

This skill requires four environment variables. **Do not run any verification commands** — go straight to the API call. If it fails, consult the error handling section (Section 11) to diagnose the cause and guide the user.

| Variable                               | Purpose                                                                                                                                     |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `ATLASSIAN_CLOUD_ID`                   | Bitwarden Atlassian Cloud ID (find it at `https://bitwarden.atlassian.net/_edge/tenant_info`)                                               |
| `ATLASSIAN_EMAIL`                      | Email address associated with the Atlassian account                                                                                         |
| `ATLASSIAN_JIRA_READ_ONLY_TOKEN`       | Scoped Jira API token with **read** permissions only ([create one here](https://id.atlassian.com/manage-profile/security/api-tokens))       |
| `ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN` | Scoped Confluence API token with **read** permissions only ([create one here](https://id.atlassian.com/manage-profile/security/api-tokens)) |

**Why two tokens?** Atlassian scoped tokens are per-product. A Jira-scoped token cannot access Confluence and vice versa. This enforces least-privilege: each token only has read access to its respective product.

## 2. Discovery

Use when the user doesn't specify a project key or space key, or asks what they have access to.

### List Jira Projects

```bash
curl -s --connect-timeout 10 --max-time 30 \
  -H "Authorization: Basic $(printf '%s:%s' "$ATLASSIAN_EMAIL" "$ATLASSIAN_JIRA_READ_ONLY_TOKEN" | base64)" \
  -H "Accept: application/json" \
  "https://api.atlassian.com/ex/jira/${ATLASSIAN_CLOUD_ID}/rest/api/3/project" | jq .
```

Present as a table: Key, Name, Type. Use the project key to resolve `{{PROJECT}}` in subsequent JQL or board queries.

### List Confluence Spaces

```bash
curl -s --connect-timeout 10 --max-time 30 \
  -H "Authorization: Basic $(printf '%s:%s' "$ATLASSIAN_EMAIL" "$ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN" | base64)" \
  -H "Accept: application/json" \
  "https://api.atlassian.com/ex/confluence/${ATLASSIAN_CLOUD_ID}/rest/api/space?limit=25&type=global" | jq .
```

Present as a table: Key, Name, Type. Use the space key to resolve `{{SPACE_KEY}}` in subsequent CQL queries.

## 3. Read Jira Issue

Use when the user references a ticket ID like `PROJ-123`, asks about a story, or wants issue details.

```bash
curl -s --connect-timeout 10 --max-time 30 \
  -H "Authorization: Basic $(printf '%s:%s' "$ATLASSIAN_EMAIL" "$ATLASSIAN_JIRA_READ_ONLY_TOKEN" | base64)" \
  -H "Accept: application/json" \
  "https://api.atlassian.com/ex/jira/${ATLASSIAN_CLOUD_ID}/rest/api/3/issue/{{TICKET_ID}}?fields=summary,description,status,issuetype,priority,assignee,reporter,comment,subtasks,issuelinks,parent,labels,components,sprint,customfield_10192&expand=renderedFields" | jq .
```

Replace `{{TICKET_ID}}` with the actual issue key (e.g. `PROJ-123`).

**Presentation instructions**:

- **Summary**: Show the issue title, type, status, priority, and assignee prominently
- **Description**: Read `renderedFields.description` (HTML) and present as clean markdown
- **Acceptance Criteria**: Check `renderedFields.customfield_10192` for acceptance criteria content (this is the dedicated A/C field in Bitwarden's Jira instance). If that field is empty or absent, fall back to looking for A/C headings, checklists, or "Acceptance Criteria" sections within the description
- **Children (Epics/Features)**: If the issue type is Epic or Feature, `fields.subtasks` may be empty — next-gen Jira projects use `parent` relationships instead of subtask links. When reading an epic, **always** perform a follow-up JQL search using `parent = {{TICKET_ID}}` (Section 5) to discover child issues
- **Subtasks**: If `fields.subtasks` is non-empty, list each with key, summary, and status
- **Links**: If `fields.issuelinks` is non-empty, list linked issues grouped by link type (e.g. "blocks", "is blocked by", "relates to")
- **Parent**: If `fields.parent` exists, mention the parent epic/story
- **Comments**: Show the last 3 comments from `fields.comment.comments` (sorted newest first). For each, show author display name, date, and body
- **Never dump raw JSON** unless the user explicitly asks for it

## 4. Read Jira Issue Comments

Use when more comments are needed beyond what the issue endpoint returned, or when the user asks specifically for comment history.

```bash
curl -s --connect-timeout 10 --max-time 30 \
  -H "Authorization: Basic $(printf '%s:%s' "$ATLASSIAN_EMAIL" "$ATLASSIAN_JIRA_READ_ONLY_TOKEN" | base64)" \
  -H "Accept: application/json" \
  "https://api.atlassian.com/ex/jira/${ATLASSIAN_CLOUD_ID}/rest/api/3/issue/{{TICKET_ID}}/comment?orderBy=-created&maxResults=10" | jq .
```

Replace `{{TICKET_ID}}` with the issue key.

**Presentation instructions**:

- Show each comment with: author display name, created date, and body text
- The body is in Atlassian Document Format (ADF) — read the `content` nodes and render as markdown
- If there are more comments than returned, mention the total count from the response

## 5. Search Jira (JQL)

Use when the user asks about sprint contents, epic children, text search across issues, or any bulk issue query.

> **API Note**: Atlassian removed the legacy `/rest/api/3/search` endpoint (see [CHANGE-2046](https://developer.atlassian.com/changelog/#CHANGE-2046)). Always use `/rest/api/3/search/jql` instead.

```bash
curl -s --connect-timeout 10 --max-time 30 -G \
  -H "Authorization: Basic $(printf '%s:%s' "$ATLASSIAN_EMAIL" "$ATLASSIAN_JIRA_READ_ONLY_TOKEN" | base64)" \
  -H "Accept: application/json" \
  --data-urlencode "jql={{JQL}}" \
  "https://api.atlassian.com/ex/jira/${ATLASSIAN_CLOUD_ID}/rest/api/3/search/jql?maxResults=20&fields=summary,status,issuetype,priority,assignee,parent" | jq .
```

Replace `{{JQL}}` with the user's query. URL-encode special characters.

**Common JQL patterns** (suggest these to the user when relevant):

| Use case                 | JQL                                                              |
| ------------------------ | ---------------------------------------------------------------- |
| Active sprint issues     | `project = {{PROJECT}} AND sprint in openSprints()`              |
| Epic children (next-gen) | `parent = {{EPIC_KEY}}`                                          |
| Epic children (classic)  | `"Epic Link" = {{EPIC_KEY}}`                                     |
| Full text search         | `text ~ "{{SEARCH_TERM}}"`                                       |
| Linked issues            | `issuekey in linkedIssues({{TICKET_ID}})`                        |
| My open issues           | `assignee = currentUser() AND resolution = Unresolved`           |
| Recently updated         | `project = {{PROJECT}} AND updated >= -7d ORDER BY updated DESC` |

**Presentation instructions**:

- Present results as a table with columns: Key, Type, Summary, Status, Priority, Assignee
- Include the parent epic key if present
- The new `/search/jql` endpoint uses cursor-based pagination: check `isLast` (boolean) to determine if more pages exist, rather than the legacy `total` field. If `isLast` is `false`, note that results were truncated

## 6. Read Confluence Page

Use when the user shares a Confluence URL or page ID, or when a Jira issue links to Confluence content.

```bash
curl -s --connect-timeout 10 --max-time 30 \
  -H "Authorization: Basic $(printf '%s:%s' "$ATLASSIAN_EMAIL" "$ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN" | base64)" \
  -H "Accept: application/json" \
  "https://api.atlassian.com/ex/confluence/${ATLASSIAN_CLOUD_ID}/rest/api/content/{{PAGE_ID}}?expand=body.storage,version,space,ancestors" | jq .
```

Replace `{{PAGE_ID}}` with the numeric page ID.

**Extracting the page ID from a Confluence URL**:

- URL format: `https://domain.atlassian.net/wiki/spaces/SPACE/pages/123456789/Page+Title` → page ID is `123456789`
- URL format: `https://domain.atlassian.net/wiki/x/AbCdEf` → this is a tiny URL; fetch it and extract the page ID from the redirect or resolved content

**Presentation instructions**:

- Show: page title, space name, version number, last modified info
- Show breadcrumb path from `ancestors` array (top-level → parent → current page)
- The `body.storage.value` field contains HTML — read it and convert to clean markdown in your response
- For large pages, summarize the key sections relevant to the user's current task rather than reproducing the entire page
- If the page contains tables, preserve table formatting

## 7. Search Confluence (CQL)

Use when the user wants to find Confluence pages by keyword, label, or space.

```bash
curl -s --connect-timeout 10 --max-time 30 -G \
  -H "Authorization: Basic $(printf '%s:%s' "$ATLASSIAN_EMAIL" "$ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN" | base64)" \
  -H "Accept: application/json" \
  --data-urlencode "cql={{CQL}}" \
  "https://api.atlassian.com/ex/confluence/${ATLASSIAN_CLOUD_ID}/rest/api/content/search?limit=10" | jq .
```

Replace `{{CQL}}` with the query. URL-encode special characters.

**Common CQL patterns**:

| Use case             | CQL                                                        |
| -------------------- | ---------------------------------------------------------- |
| Text search          | `text ~ "{{SEARCH_TERM}}"`                                 |
| Space + text         | `space = "{{SPACE_KEY}}" AND text ~ "{{SEARCH_TERM}}"`     |
| Label filter         | `label = "{{LABEL}}"`                                      |
| Space + label        | `space = "{{SPACE_KEY}}" AND label = "{{LABEL}}"`          |
| Pages under ancestor | `ancestor = {{PAGE_ID}}`                                   |
| Recently modified    | `lastModified >= "2024-01-01" AND space = "{{SPACE_KEY}}"` |

**Presentation instructions**:

- List results with: title, space name, last modified date, and a brief excerpt if available
- Show total result count and note if truncated

## 8. Confluence Child Pages

Use when the user wants to see subpages under a Confluence page, or when exploring a documentation tree.

```bash
curl -s --connect-timeout 10 --max-time 30 \
  -H "Authorization: Basic $(printf '%s:%s' "$ATLASSIAN_EMAIL" "$ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN" | base64)" \
  -H "Accept: application/json" \
  "https://api.atlassian.com/ex/confluence/${ATLASSIAN_CLOUD_ID}/rest/api/content/{{PAGE_ID}}/child/page?limit=25&expand=version" | jq .
```

Replace `{{PAGE_ID}}` with the parent page ID.

**Presentation instructions**:

- List child pages with: title, page ID, version number, and last modified date
- If there are many children, present as a numbered list

## 9. Boards and Sprints

Use when the user asks about sprint status, board configuration, or wants to see what's in the current sprint.

### List Boards

```bash
curl -s --connect-timeout 10 --max-time 30 \
  -H "Authorization: Basic $(printf '%s:%s' "$ATLASSIAN_EMAIL" "$ATLASSIAN_JIRA_READ_ONLY_TOKEN" | base64)" \
  -H "Accept: application/json" \
  "https://api.atlassian.com/ex/jira/${ATLASSIAN_CLOUD_ID}/rest/agile/1.0/board?projectKeyOrId={{PROJECT_KEY}}" | jq .
```

Replace `{{PROJECT_KEY}}` with the project key (e.g. `PROJ`).

### Get Active Sprint

```bash
curl -s --connect-timeout 10 --max-time 30 \
  -H "Authorization: Basic $(printf '%s:%s' "$ATLASSIAN_EMAIL" "$ATLASSIAN_JIRA_READ_ONLY_TOKEN" | base64)" \
  -H "Accept: application/json" \
  "https://api.atlassian.com/ex/jira/${ATLASSIAN_CLOUD_ID}/rest/agile/1.0/board/{{BOARD_ID}}/sprint?state=active" | jq .
```

Replace `{{BOARD_ID}}` with the board ID from the previous call.

### Get Sprint Issues

```bash
curl -s --connect-timeout 10 --max-time 30 \
  -H "Authorization: Basic $(printf '%s:%s' "$ATLASSIAN_EMAIL" "$ATLASSIAN_JIRA_READ_ONLY_TOKEN" | base64)" \
  -H "Accept: application/json" \
  "https://api.atlassian.com/ex/jira/${ATLASSIAN_CLOUD_ID}/rest/agile/1.0/sprint/{{SPRINT_ID}}/issue?fields=summary,status,issuetype,priority,assignee" | jq .
```

Replace `{{SPRINT_ID}}` with the sprint ID from the previous call.

**Workflow**: To answer "what's in the current sprint?", chain the three calls: list boards → get active sprint → get sprint issues.

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

## 11. Hook Testing

A read-only safety hook (`hooks/block-mutating-atlassian.sh`) blocks all mutating curl operations targeting Atlassian APIs. After modifying the hook or its gates, validate it by reading `references/hook-testing.md` for the full test harness and category list. Generate test payloads dynamically at runtime — do not store them as committed scripts.

## 12. Error Handling

| HTTP Status              | Meaning                                               | Fix                                                                                                                                                                                                                                                             |
| ------------------------ | ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 401 Unauthorized         | Invalid or expired API token                          | Ask user to verify the relevant token (`ATLASSIAN_JIRA_READ_ONLY_TOKEN` or `ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN`). Tokens can be regenerated at [Atlassian API tokens](https://id.atlassian.com/manage-profile/security/api-tokens).                           |
| 403 Forbidden            | Token is valid but lacks permission for this resource | Check that the scoped token has the correct **read** scope for the product. The Jira token needs `read:jira-work` scope; the Confluence token needs `read:confluence-content.all` scope. Also verify the user has access to the project/space.                  |
| 404 Not Found            | Issue, page, or resource does not exist               | Verify the ticket ID, page ID, or URL. Check for typos. The resource may have been deleted or moved.                                                                                                                                                            |
| 200 with `errorMessages` | API endpoint has been removed or deprecated           | Atlassian periodically retires old API versions. If the response contains `"The requested API has been removed"`, check the [Atlassian changelog](https://developer.atlassian.com/changelog/) for migration guidance and update the endpoint URL in this skill. |

**Never expose tokens**: Do not echo, log, or include token values in output when debugging authentication failures. Refer to tokens by variable name only.

**Wrong token for wrong product**: If a Jira call returns 401 but the token is valid, check that you're using `ATLASSIAN_JIRA_READ_ONLY_TOKEN` (not the Confluence token) and vice versa.

**Missing environment variable detection**: If a curl command returns a connection error or malformed URL, check whether `ATLASSIAN_CLOUD_ID`, `ATLASSIAN_EMAIL`, `ATLASSIAN_JIRA_READ_ONLY_TOKEN`, or `ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN` is unset and ask the user to set them (see Section 1).

**Rate limiting**: Atlassian Cloud APIs have rate limits. If you receive a 429 response, wait a moment before retrying. For batch operations, add a small delay between requests.
