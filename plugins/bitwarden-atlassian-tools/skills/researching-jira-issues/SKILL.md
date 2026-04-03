---
name: researching-jira-issues
description: Use whenever the user mentions a Jira issue key and wants more than a surface-level lookup — "Read PROJ-123", "What's PROJ-123 about?", "Give me context on PROJ-123", "Deep dive PROJ-123", "What's blocking PROJ-123?", "Summarize PROJ-123 and its dependencies", "I need to work on PROJ-123, what should I know?", or any request to understand an issue's purpose, scope, or requirements. Thoroughly researches and synthesizes a Jira issue including all linked issues, sub-tasks, blocked dependencies, and supporting Confluence documentation.
---

# Researching Jira Issues

Synthesize information, don't concatenate tool outputs. Each step below gathers raw data — the value of this skill is in connecting the dots across issues, docs, and comments into a coherent understanding that a human can act on.

## Workflow

### Step 1: Fetch the Main Issue

Use the `get_issue` MCP tool with the issue key. The tool defaults to expanding `renderedFields` and `names`, which provides HTML-rendered fields and human-readable custom field display names.

Extract and note:
- Issue type (Epic, Story, Task, Bug, Sub-task, etc.)
- Summary and description
- Current status and priority
- Assignee and reporter
- Key fields relevant to understanding the work (labels, components, sprint, etc.)
- Comments that provide important context (clarifications from stakeholders, technical decisions, implementation guidance)
- **Custom fields**: Consult `references/jira_custom_fields.md` to look up the custom field IDs for this issue's type. Extract and surface all non-null custom fields listed for that type (e.g., Acceptance criteria, QA testing notes, Technical breakdown, Goals/Deliverables, Outcome, etc.). The `names` expansion maps field IDs to human-readable names automatically.

### Step 2: Identify All Linked Issues

Examine the main issue response to identify linked issues through:

1. **Issue Links**: Look for the `issuelinks` field in the API response (an untyped array field returned by Jira) containing:
   - Blocks/Blocked by relationships
   - Depends on/Dependency relationships
   - Relates to links
   - Clones, Duplicates, Supersedes relationships
   - Any other link types

2. **Hierarchical Links**: Look for:
   - Parent issue (if this is a sub-task)
   - Epic link (if this is linked to an epic)
   - Sub-tasks (if this issue has sub-tasks)
   - **Next-gen projects**: If the issue type is Epic or Feature and `subtasks` is empty, use the `search_issues` MCP tool with JQL `parent = <ISSUE-KEY>` to discover child issues. Next-gen Jira projects use `parent` relationships instead of the `subtasks` field.

3. **Remote Links**: Use the `get_issue_remote_links` MCP tool with the issue key to find:
   - Linked Confluence pages (grouped under "Confluence Pages" in the output)
   - Pull requests and commits (grouped under "GitHub")
   - External documentation and other resources

### Step 3: Fetch Linked Issues with Depth Control

Fetch related issues to build context, but stop before the returns diminish. Each additional hop adds API calls and context window usage while providing less directly relevant information.

1. **Priority Order** (consult `references/jira_link_types.md` for details):
   - High Priority: Blocks, Depends on, Parent, Epic Link — these determine whether work can start and where the issue fits in the hierarchy
   - Medium Priority: Sub-tasks, Related issues — these define scope and provide background
   - Low Priority: Clones, Duplicates — only if they provide unique context not found elsewhere

2. **Depth Control**:
   - Traverse up to 2 levels beyond the main issue (main issue -> linked issue -> one more hop for high-priority links only). Beyond 2 levels, context relevance drops sharply and the risk of ballooning the response grows.
   - Track fetched issue keys to avoid circular references (A links to B, B links to A)
   - For each linked issue, use the `get_issue` MCP tool and extract key information

3. **Selective Fetching**:
   - For sub-tasks: Fetch all to understand full scope of work. If there are more than 10 children, fetch the first 10 and summarize the remainder as a compact list (key, status, summary) from the search results.
   - For blocking issues: Fetch to understand dependencies
   - For related issues: Fetch if they appear critical to understanding
   - Skip duplicate/cloned issues unless they contain unique information

4. **Rate Limiting**: Space out requests when making many API calls. After every 5 sequential calls, pause briefly (1 second) to avoid hitting Atlassian rate limits. If you encounter a 429 response, wait 10 seconds before retrying.

### Step 4: Fetch Linked Confluence Documentation

Confluence pages often contain requirements, design docs, or specifications:

1. Extract Confluence page links from:
   - Remote links output (Step 2 — links grouped under "Confluence Pages")
   - Issue description URLs matching `*/wiki/spaces/*/pages/*/`
   - Comment URLs pointing to Confluence

2. For each Confluence link:
   - Extract the `pageId` from the URL (e.g., `https://domain.atlassian.net/wiki/spaces/SPACE/pages/123456789/Title` -> `123456789`)
   - Use the `get_confluence_page` MCP tool with the page ID
   - Note the page title and key information from the content

3. **Context budget for pages**: For Confluence pages over 2000 words, summarize the sections relevant to the issue rather than reproducing the full page. Focus on requirements, acceptance criteria, technical constraints, and design decisions.

### Step 5: Handle Failures Gracefully

If any fetch fails, note the failure and continue with available data. Specific failure modes:
- **404 on a linked issue**: The issue was deleted or moved. Note the key and skip.
- **403 on a Confluence page**: No access. Note the page title from the remote link and skip.
- **404 on remote links**: The endpoint may not be available. Skip and rely on issue links from the main response.

Always report which items could not be retrieved at the end of the synthesis.

### Step 6: Synthesize and Present

Organize all gathered information into a comprehensive understanding:

#### Issue Overview
- What is the core purpose of this issue?
- What type of work is this (new feature, bug fix, tech debt, etc.)?
- Current status and who's working on it

#### Requirements and Context
- What are the key requirements or acceptance criteria?
- What problem is being solved?
- What documentation supports this work?
- Show any non-null custom fields for this issue type (per `references/jira_custom_fields.md`) under their field name as a heading, rendering the content as markdown

#### Dependencies and Relationships
- What issues must be completed first (blocking dependencies)?
- What issues does this block (downstream impact)?
- How does this fit into the larger epic or project?

#### Scope of Work
- What sub-tasks exist?
- What's the breakdown of the work?
- Are there related issues that provide additional context?

#### Key Insights
- Technical decisions or constraints from comments/documentation
- Risks or concerns mentioned
- Important historical context (why was this cloned, what was superseded, etc.)

### Context Budget

When the full synthesis exceeds approximately 4000 words (roughly the point where readers start skimming rather than absorbing), condense lower-priority linked issues (Related, Clones, Duplicates) to single-line summaries with key, status, and summary only. Limit displayed comments to the 3 most recent unless the user asks for more.

## Cross-Plugin Enrichment

After gathering all issue data, check for enrichment triggers from sibling plugins:

### Security Enrichment

Invoke `Skill(bitwarden-security-context)` when ANY of these signals are present in the `get_issue` output:
- The **Labels** section contains terms like `security`, `vulnerability`, `compliance`
- The **Components** section includes security-related components
- The description or linked docs mention security topics (encryption, auth, access control, etc.)
- The **Additional Fields** section shows a populated Security Approver (`customfield_10224`)

This overlays Bitwarden's security principles (P01-P06) and vocabulary onto the synthesis, adding a "Security Considerations" subsection.

### Development Enrichment

When linked Confluence pages contain technical specifications or the **Additional Fields** section shows a populated Technical breakdown (`customfield_10313`), invoke the relevant engineering skill based on content signals:
- Server/API/C#/.NET references -> `Skill(writing-server-code)`
- Client/Angular/TypeScript/UI references -> `Skill(writing-client-code)`
- Database/migration/SQL/stored procedure references -> `Skill(writing-database-queries)`

This validates whether the spec aligns with Bitwarden's coding conventions and surfaces any mismatches in a "Development Context" subsection.

### Skill Availability

These skills are from sibling plugins (`bitwarden-security-engineer`, `bitwarden-software-engineer`). If unavailable, present the raw Atlassian content without additional analysis.

## Composability

When invoked by another skill, produce a structured markdown document with clearly labeled sections matching the Step 6 headings. When invoked directly by a user, present a conversational summary that leads with the most important information (what is it, what's blocking it, what's the scope) and lets the user ask follow-up questions for deeper detail.

## Resources

### references/jira_custom_fields.md

Maps each Bitwarden Jira issue type (Epic, Spike, Story, Task, QA Bug, Subtask) to its known custom field IDs and human-readable names. Consult this in Step 1 after identifying the issue type to know exactly which custom fields to look for and surface.

### references/jira_link_types.md

Comprehensive documentation about Jira link types, their meanings, and priority for reading. Consult this when determining which linked issues to fetch and in what order.

## Example Usage

**User Request**: "Read PROJ-123"

**Workflow**:
1. Fetch PROJ-123 via `get_issue` -> It's a Story with 3 sub-tasks, blocked by PROJ-100, and has a remote link to a Confluence page
2. Fetch remote links via `get_issue_remote_links` -> Confirms Confluence page link and a GitHub PR
3. Fetch PROJ-100 (blocking issue) via `get_issue` -> It's a Bug that's currently in progress
4. Fetch the 3 sub-tasks via `get_issue` -> PROJ-124, PROJ-125, PROJ-126
5. Fetch the linked Confluence page via `get_confluence_page` -> Contains detailed requirements and mockups
6. Synthesize: "PROJ-123 is a Story for implementing user authentication. It's blocked by PROJ-100 (a bug in the login endpoint that's currently being fixed). The work is broken into 3 sub-tasks: frontend form (PROJ-124), API integration (PROJ-125), and testing (PROJ-126). The Confluence documentation specifies OAuth2 integration requirements and includes mockups of the login flow."
