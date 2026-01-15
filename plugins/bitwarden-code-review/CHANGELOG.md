# Changelog

All notable changes to the Bitwarden Code Review Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.0] - 2026-01-15

### Changed

- Added code-review command to properly invoke the bitwarden-code-reviewer agent via Task tool
- Updated agent frontmatter listing all skills available
- Updated agent model to opus; aligns with our changes to the GitHub reusable action

## [1.5.2] - 2026-01-09

### Changed

- Refactored the fetching of resolved comments back into the SKILL.md because the script will not execute in the Claude Code Action because of security concerns.

## [1.5.1] - 2025-12-24

### Changed

- Added a brief ending instruction to avoid a follow-up update of the summary comment by the GitHub action.

## [1.5.0] - 2025-12-23

### Added

- Skill `posting-review-summary` for context-aware summary output (sticky comment vs local file)
- Skill `avoiding-false-positives` to reduce hallucinations
- Skill `detecting-existing-threads` for duplicate comment prevention
- Skill `reviewing-incremental-changes` for re-review scoping
- Collapsed `<details>` section in summaries listing findings by severity

### Changed

- Extracted PR metadata assessment from AGENT.md into `posting-review-summary` skill
- `posting-bitwarden-review-comments` delegates summary formatting to dedicated skill
- Summary comments include 1-2 neutral sentences describing what was reviewed
- Reduced AGENT.md complexity (~180 lines → ~120 lines)

### Fixed

- Tool permission patterns for `get-review-threads.sh`

## [1.4.0] - 2025-12-21

### Added

- Two new skills: `classifying-review-findings` and `posting-bitwarden-review-comments`
- Comprehensive test plan in `tests/TESTING.md`

### Changed

- Refactored AGENT.md to use skill-based architecture for classification and formatting
- Updated permission patterns in settings.json to use `:*` suffix format
- Simplified README.md by moving detailed procedures to skill documentation

### Fixed

- Permission deny patterns now correctly use `:*` format for Claude Code compatibility

## [1.3.3] - 2025-12-18

- Remove all repo specific guidance from our code review agent.

## [1.3.2] - 2025-12-17

### Security

- Implemented a custom bash script to retrieve the resolved comments on a pull request. The implementation was chosen to grant Claude Code the least privilege possible to complete the task.

## [1.3.1] - 2025-12-15

### Security

- Restrict agent tool declaration from `Bash(gh pr review:*)` to `Bash(gh pr review:--comment*)` to explicitly prevent PR approval and rejection operations
- Closes permission gap where `--approve` and `--request-changes` flags were technically allowed by wildcard pattern but not intended
- Agent retains ability to post inline review comments (`gh pr review --comment`) and summary comments (`gh pr comment`)

## [1.3.0] - 2025-12-09

### Security

- Restricted agent tools from wildcards (`gh pr:*`, `gh api:*`) to specific safe commands only
- Added `.claude/settings.json` with comprehensive deny list blocking:
  - PR modifications (merge, close, edit, lock, reopen, ready, checkout)
  - Issue modifications (create, close, edit, delete, lock, transfer, pin) - **allows read-only `gh issue view/list`**
  - Repository operations (edit, archive, delete, rename, sync, create, fork)
  - Release operations (all `gh release` commands)
  - Organization operations (all `gh org` commands)
  - Secrets access (all `gh secret` commands - **critical security boundary**)
  - Workflow operations (all `gh workflow` commands)
  - CI/CD operations (rerun, cancel, delete, watch - **allows read-only `gh run view/list`**)
  - API write operations (DELETE, PATCH, PUT methods)
- Agent now follows principle of least privilege with read + comment permissions only
- GraphQL access restricted to query operations.
  - Primary enforcement done through GitHub token permissions in the reusable review code workflow in the gh-actions repo.
  - Secondary defense is mutations blocked via pattern matching in the agent.md

## [1.2.0] - 2025-11-20

### Added

- **Thread Detection (REQUIRED)**: Universal duplicate comment prevention system
  - Detects existing comment threads (including resolved ones) before creating new ones
  - Matches by location (exact/nearby), content similarity (>70%), and issue type
  - Agent autonomously constructs `gh pr` and `gh api` GraphQL queries to fetch threads
  - Strict JSON output schema ensures consistent thread parsing across invocations
  - Supports multiple invocation contexts: GitHub Actions (environment variables), slash commands, manual invocation
  - Works universally across all repository installations
  - Prevents duplicate comments and maintains conversation continuity
- **Output Format Decision Tree**: Structured guidance for determining clean PR vs. issues format
  - Prevents verbose clean reviews (2-3 lines maximum for PRs with no issues)
  - Ensures consistent formatting across all reviews
  - Improves developer experience by reducing review noise

### Fixed

- **Severity-Based Respect Decisions**: Clarified when agents may respond to resolved threads
  - CRITICAL/IMPORTANT: May respond ONCE if issue genuinely persists after developer claims resolution
  - SUGGESTED/QUESTION: Never reopen after human provides answer/decision
- **Complete First Review Requirement**: Ensures comprehensive initial reviews find all critical issues
  - Agent performs full analysis across all changed code before posting
  - Prevents incremental feedback cycles that frustrate developers
- **Praise Prohibition Consolidation**: Eliminated duplication across sections
  - Single authoritative definition with references elsewhere
  - Reduced maintenance burden and improved clarity

### Changed

- **Agent Version Tracking**: Added `version: 1.2.0` to AGENT.md frontmatter for improved change management
- **Improved Section Organization**: Relocated "Determining Output Format" section for better logical flow (analysis → format decision → finding creation → posting)

## [1.1.0] - 2025-11-18

### Added

- **`/code-review-local` slash command**: Invokes bitwarden-code-reviewer agent to review GitHub PRs and write findings to local files (`review-summary.md` and `review-inline-comments.md`) instead of posting to GitHub. Enables offline review workflows and review preview before posting.

## [1.0.0] - 2025-11-17

### Added

- Initial release of `bitwarden-code-review` plugin
- Base organizational guidelines defining:
  - Process rules (structured thinking, check existing comments, avoid duplicates, respect resolved threads)
  - Finding terminology ("Finding" not "Issue", no # symbol for GitHub autolinking)
  - Emoji classification system (❌ ⚠️ ♻️ 🎨 💭)
  - Comment format requirements (brevity, inline vs summary, clean PR format)
  - Professional tone guidelines
- Plugin manifest with metadata and skill registration
- Comprehensive README documentation

---

## Version Format

Plugin version tracks base guidelines changes:

- **Major version**: Breaking changes to base guidelines or emoji system
- **Minor version**: New organizational patterns added to base guidelines, or new tool additions.
- **Patch version**: Bug fixes, clarifications, documentation improvements
