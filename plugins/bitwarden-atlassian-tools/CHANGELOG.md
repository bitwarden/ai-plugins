# Changelog

All notable changes to the Bitwarden Atlassian Tools plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.7.1] - 2026-08-26

### Fixed

- `evaluating-qa-readiness` no longer reports "no PR or build is linked" as a settled fact. `get_issue_remote_links` cannot see Jira's native Development panel (the GitHub/Bitbucket integration that links most PRs via smart commits or branch naming), so an empty result is now reported as "not found in the sources this check can search" with a pointer to check the Development panel manually, instead of a confident negative.
- `evaluating-qa-readiness`'s feature-flag criterion and developer-ask draft no longer demand an explicit on/off state when only one flag is named — "enable to test" is now the assumed default unless the ticket gives a real reason the state is ambiguous.
- `evaluating-qa-readiness`'s drafted developer ask now names the gap without dictating exhaustive step-by-step detail (exact queries, seed data, timing) that a competent tester doesn't need.

## [2.7.0] - 2026-08-06

### Added

- Added the `evaluating-qa-readiness` skill, which checks a Jira ticket for the information QA needs before testing (testing instructions, implementation notes, feature-flag state, acceptance criteria, affected clients, and a linked PR/build) via the read-only Atlassian MCP and drafts a ready-to-paste developer comment for any gaps

## [2.6.0] - 2026-08-04

### Added

- **`filing-jira-tickets` skill** — files work items that stand on their own: reads the target project's create screen first, translates work into real ticket titles and criteria placed in whatever field the project provides, previews each payload and takes approval before writing it, then wires and verifies dependency links. Approval is the default and only an explicit instruction skips it.

## [2.5.0] - 2026-08-03

### Added

- **`get_create_fields` MCP tool** (read-only) — reports a project's creatable issue types, and for a given type every field on the create screen with its field id, required flag, and allowed values. Lets callers discover a project's shape instead of hardcoding it, which matters because Bitwarden's projects differ: PM and SM expose an Acceptance criteria field, QA and VULN do not; VULN has no Story type; PLT's only creatable type is `Platform Initiative`.
- **`create_issue` MCP tool** (write, opt-in) — creates a single work item in any project. Defaults to a dry run that returns the exact payload without sending it; a live create requires an explicit `dryRun: false`. Carries no project-specific field knowledge: the issue type is a name Jira resolves, and anything beyond project/type/summary/description/parent/labels is passed through a `fields` object keyed by Jira field id.
- **`link_issues` MCP tool** (write, opt-in) — links two work items. For a dependency it takes `blockerKey` and `blockedKey` and applies Jira's inward/outward mapping internally, so the direction cannot be inverted by argument order. Also defaults to a dry run.
- **Optional `ATLASSIAN_JIRA_WRITE_TOKEN`** — write capability is opt-in per install. The write tools are always listed and their dry-run paths always work; without this variable, a live write refuses to execute.

## [2.4.0] - 2026-07-24

### Added

- `assessing-jira-issue-relevance` skill for determining whether a single Jira issue still applies to the current codebase. Fetches the ticket along with its comments, linked issues, and parent epic; confirms which repositories are in scope before searching; greps for the code path the ticket describes; checks git history since the filed date; and returns a verdict (still relevant / partially addressed / no longer relevant / technically relevant but worth questioning / cannot determine) with `file:line` evidence. Intended for backlog cleanup — one ticket per invocation.
  - Works against any Bitwarden repository. Where the ticket does not name one outright, the skill infers the likely repo from the available signals and presents that inference for confirmation before searching anything, then orients itself by reading the confirmed repo's own `CLAUDE.md`/`README`.
  - Halts without a verdict if a repository in scope is not cloned locally and the user declines to clone it. Searching an absent repo returns no matches, which is indistinguishable from the code having been removed, and would otherwise produce a confident "no longer relevant" on a live ticket.
  - Ships scoped `allowed-tools` covering the four read-only Atlassian MCP tools the workflow calls, so routine use does not prompt for permission on every fetch.

## [2.3.0] - 2026-07-15

### Added

- Three read-only Jira Agile MCP tools that expose the MCP server's existing (previously unexposed) Agile API client methods:
  - `list_boards` — list Jira Agile boards, optionally filtered by project
  - `get_sprints` — list sprints for a board, optionally filtered by state (active/future/closed)
  - `get_sprint_issues` — list all issues in a sprint
- Documented the granular Jira Software OAuth scopes (`read:board-scope:jira-software`, `read:project:jira`, `read:sprint:jira-software`, `read:issue-details:jira`, `read:jql:jira`) required by the board/sprint tools — the Agile `/rest/agile/1.0` API is not covered by the classic `read:jira-work` scope

### Changed

- Extracted the shared issue formatter into `src/utils/format-issue.ts`, reused by `search_issues` and `get_sprint_issues` instead of duplicating it per tool

## [2.2.8] - 2026-07-01

### Security

- Updated the bundled MCP server's pinned pnpm toolchain from 11.5.2 to 11.8.0 to address CVE-2026-55180 (GHSA-3qhv-2rgh-x77r), where pnpm repository config could expand environment secrets into registry requests before scripts run

## [2.2.7] - 2026-06-08

### Changed

- Migrated the bundled MCP server's tooling from npm to pnpm (pinned `pnpm@11.5.2`, installed via Corepack) as part of the repo-wide migration. **Consumers now need Corepack** (bundled with Node.js) and Node.js 22+; npm is no longer used to install or build the server

## [2.2.6] - 2026-06-05

### Changed

- Updated bundled MCP server dependencies to new major versions, with minor source and test adjustments for compatibility

## [2.2.5] - 2026-06-02

### Added

- Commit `package-lock.json` for the bundled MCP server so every consumer install (which runs `npm install` at MCP startup) resolves the same pinned transitive dependency tree

### Changed

- CI now installs the MCP server with `npm ci` against the committed lockfile, with npm caching enabled

## [2.2.4] - 2026-06-02

### Added

- CI workflows (`atlassian-mcp-server-build.yml`, `atlassian-mcp-server-test.yml`) that build and test the bundled Atlassian MCP server, path-scoped so they only run when the MCP server changes
- `.nvmrc` at the repository root pinning Node 24 for all workflows

### Changed

- Raised the bundled MCP server's `engines.node` requirement from `>=18.0.0` to `>=24.0.0`

## [2.2.3] - 2026-04-15

### Changed

- Apply prettier formatting to markdown and JSON files

## [2.2.2] - 2026-04-15

### Fixed

- Removed invalid `view` option from `bodyFormat` parameter in `get_confluence_page_comments` — the Confluence REST API v2 only supports `storage` format for comment bodies

## [2.2.1] - 2026-04-14

### Security

- Update a dependency vulnerability

## [2.2.0] - 2026-04-03

### Added

- `get_issue_remote_links` MCP tool for fetching remote links attached to a Jira issue
- `researching-jira-issues` skill for deep Jira issue reads with linked issue traversal and Confluence follow-through
- Reference documents for custom field mappings and link type taxonomy

### Removed

- `atlassian-reader` plugin — superseded by this plugin's MCP tools and the new skill

## [2.1.0] - 2026-03-20

### Added

- `get_issue` now includes populated custom fields (e.g., "Replication Steps", "Recommended Solution") in an "Additional Fields" section with human-readable field names

## [2.0.0] - 2026-03-09

### Changed

- Migrated from direct site URLs to Atlassian API gateway (`api.atlassian.com`) for all API requests
- Replaced `ATLASSIAN_JIRA_URL` and `ATLASSIAN_CONFLUENCE_URL` env vars with single `ATLASSIAN_CLOUD_ID`
- Attachment URL validation now accepts any `*.atlassian.net` origin instead of exact origin match
- Attachment downloads now route through the API gateway for scoped token compatibility

### Added

- Support for Atlassian scoped API tokens (requires gateway routing)

### Migration

- Remove `ATLASSIAN_JIRA_URL` and `ATLASSIAN_CONFLUENCE_URL` environment variables
- Add `ATLASSIAN_CLOUD_ID` (find yours at `https://your-domain.atlassian.net/_edge/tenant_info`)

## [1.1.1] - 2026-03-09

### Fixed

- Fix `extractPlainText` silently dropping smart links (Figma, Confluence URLs), lists, mentions, and other rich ADF content from Jira descriptions
- Add handlers for 15 ADF node types: inlineCard, blockCard, embedCard, mention, emoji, status, date, media, bulletList, orderedList, blockquote, expand, nestedExpand, rule, and table
- Preserve link URLs from text node marks and inlineCard nodes in `extractPlainTextTruncated`
- Grow test coverage from 27 to 118 cases

## [1.1.0] - 2026-03-07

### Added

- Confluence client layer with Basic Auth using `ATLASSIAN_CONFLUENCE_URL` and `ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN` env vars (falls back to Jira credentials)
- 6 Confluence tools:
  - `get_confluence_page` — retrieve page content, metadata, and title by ID
  - `get_confluence_page_comments` — get footer and inline comments with optional replies
  - `get_child_pages` — list child pages of a given parent for hierarchy navigation
  - `search_confluence` — search pages by space key and/or title
  - `search_confluence_cql` — search content using Confluence Query Language (CQL)
  - `list_spaces` — list accessible Confluence spaces with type filtering
- `download_attachment` tool for downloading Jira attachments as Base64 with configurable size limits
- Optimized Confluence HTML-to-markdown transformation for reduced token consumption
- Confluence environment variable passthrough in `.mcp.json`
- Unit tests for Confluence auth, client, content formatting, and input validation

## [1.0.1] - 2026-03-06

### Fixed

- Fix MCP server startup command to install dependencies and build before execution

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
