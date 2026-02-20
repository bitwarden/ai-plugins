# Changelog

All notable changes to the Bitwarden Atlassian Tools plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-19

### Added

- Custom MCP server with 14 read-only Atlassian tools (Jira + Confluence)
  - Jira: `get_issue`, `search_issues`, `get_issue_comments`, `download_attachment`, `list_boards`, `get_sprints`, `get_sprint_issues`, `list_projects`
  - Confluence: `get_confluence_page`, `search_confluence`, `search_confluence_cql`, `get_confluence_page_comments`, `get_child_pages`, `list_spaces`
- Optimized ADF-to-plaintext and HTML-to-markdown transformation for reduced token consumption
- `atlassian-reader` skill for reading Jira issues, epics, sprints, boards, and Confluence pages
- `sprint-workability` skill for orchestrating full sprint health analysis
- `parsing-sprint-data` skill to extract ticket identifiers from Confluence pages
- `categorizing-workability` skill to classify tickets as BLOCKED, STALLED, NEEDS_CLARIFICATION, or IN_PROGRESS
- `analyzing-requirements` skill with rubric for evaluating ticket clarity, completeness, and readiness
- `generating-report` skill for formatting output as Markdown, JSON, YAML, or inline summary
- `ticket-investigator` agent for parallel deep-dive ticket analysis via MCP tools
- `curl-ticket-investigator` agent for curl-based comparative investigation
- `/sprint-review` command for CLI-driven sprint ticket analysis
- Multi-source data retrieval (Confluence, Jira, direct ticket lists)
- Platform/component filtering (Android, iOS, Server, Web)
- Parallel subagent execution for 10+ simultaneous investigations
