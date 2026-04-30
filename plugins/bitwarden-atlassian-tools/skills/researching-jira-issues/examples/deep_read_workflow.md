# Example: Deep Read Workflow

**User Request**: "Read PROJ-123"

**Workflow**:

1. Fetch PROJ-123 via `get_issue` -> It's a Story with 3 sub-tasks, blocked by PROJ-100, and has a remote link to a Confluence page
2. Fetch remote links via `get_issue_remote_links` -> Confirms Confluence page link and a GitHub PR
3. Fetch PROJ-100 (blocking issue) via `get_issue` -> It's a Bug that's currently in progress
4. Fetch the 3 sub-tasks via `get_issue` -> PROJ-124, PROJ-125, PROJ-126
5. Fetch the linked Confluence page via `get_confluence_page` -> Contains detailed requirements and mockups
6. Synthesize: "PROJ-123 is a Story for implementing user authentication. It's blocked by PROJ-100 (a bug in the login endpoint that's currently being fixed). The work is broken into 3 sub-tasks: frontend form (PROJ-124), API integration (PROJ-125), and testing (PROJ-126). The Confluence documentation specifies OAuth2 integration requirements and includes mockups of the login flow."
