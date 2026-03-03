# Changelog

All notable changes to the Bitwarden Atlassian Tools plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-23

### Added

- Custom MCP server with 4 read-only Jira tools
  - `get_issue`, `search_issues`, `get_issue_comments`, `list_projects`
- Jira client layer with Basic Auth using `ATLASSIAN_*` environment variables
- Optimized ADF-to-plaintext transformation for reduced token consumption
- Unit test suite using vitest covering validation, auth, ADF extraction, and formatting

### Fixed

- Add domain-specific terms to `.cspell.json` for spell-check compatibility
- Extract shared `extractPlainText` ADF utility to eliminate duplication
