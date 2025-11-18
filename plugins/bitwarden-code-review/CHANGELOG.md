# Changelog

All notable changes to the Bitwarden Code Review Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-11-18

### Added

- **`/code-review-local` slash command**: Invokes bitwarden-code-reviewer agent to review GitHub PRs and write findings to local files (`review-summary.md` and `review-inline-comments.md`) instead of posting to GitHub. Enables offline review workflows and review preview before posting.

## [1.0.0] - 2025-11-17

### Added

- Initial release of `bitwarden-code-review` plugin
- Base organizational guidelines (69 lines) defining:
  - Process rules (structured thinking, check existing comments, avoid duplicates, respect resolved threads)
  - Finding terminology ("Finding" not "Issue", no # symbol for GitHub autolinking)
  - Emoji classification system (❌ ⚠️ ♻️ 🎨 💭)
  - Comment format requirements (brevity, inline vs summary, clean PR format)
  - Professional tone guidelines
- Plugin manifest with metadata and skill registration
- Comprehensive README documentation
- Token-optimized architecture using progressive disclosure

### Architecture Notes

- **Base guidelines**: 69 lines, ~100 tokens (organizational standards)
- **Skill structure**: Self-contained with inline priority framework and review psychology (no duplication with base)
- **Token usage**: Simple reviews ~1,045 tokens, complex reviews ~1,770 tokens
- **Progressive disclosure**: Only relevant checklists and reference materials loaded per review

---

## Version Format

Plugin version tracks base guidelines changes:
- **Major version**: Breaking changes to base guidelines or emoji system
- **Minor version**: New organizational patterns added to base guidelines, or new tool additions.
- **Patch version**: Bug fixes, clarifications, documentation improvements

Individual skills have independent versioning in their SKILL.md frontmatter:
- Example: Plugin v1.2.0, android skill v1.5.0, iOS skill v2.1.0
