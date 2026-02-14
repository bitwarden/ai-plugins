# Changelog

All notable changes to the Atlassian Reader Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-02-14

### Added

- Added a hook to protect against any possible malicious skill usage.
- Added a reference file and Claude.md to provide Claude Code with specific instructions on how to safely verify the hook and skill work correctly together.

## [1.1.0] - 2026-02-10

### Fixed

- **JQL Search endpoint migration**: Updated from removed `/rest/api/3/search` to `/rest/api/3/search/jql` per Atlassian [CHANGE-2046](https://developer.atlassian.com/changelog/#CHANGE-2046)
- **Pagination guidance**: Updated Section 5 to use cursor-based `isLast` field instead of legacy `total` for the new search endpoint

### Added

- **Acceptance Criteria field**: Issue reads now fetch `customfield_10192` (Bitwarden's A/C field) and presentation instructions prioritize it over description-embedded A/C
- **Epic children discovery**: Section 3 now instructs agents to perform a JQL `parent =` search when reading Epics/Features, since next-gen projects don't populate `subtasks`
- **API deprecation error handling**: Section 11 error table now covers `200 with errorMessages` responses for removed/deprecated endpoints

## [1.0.0] - 2026-02-09

### Added

- Initial release with read-only Jira and Confluence access via scoped API tokens
- Jira: issue reading, comments, JQL search, boards and sprints
- Confluence: page reading, CQL search, child page listing
- Error handling and context-aware summarization

---

## Version Format

Plugin version tracks base guidelines changes:

- **Major version**: Breaking changes to base guidelines or emoji system
- **Minor version**: New organizational patterns added to base guidelines, or new tool additions.
- **Patch version**: Bug fixes, clarifications, documentation improvements
