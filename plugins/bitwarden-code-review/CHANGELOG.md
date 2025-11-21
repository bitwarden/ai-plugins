# Changelog

All notable changes to the Bitwarden Code Review Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

Individual skills have independent versioning in their SKILL.md frontmatter:
- Example: Plugin v1.2.0, android skill v1.5.0, iOS skill v2.1.0
