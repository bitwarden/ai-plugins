# Changelog

All notable changes to the `bitwarden-engineering-building` plugin (previously published as `bitwarden-software-engineer`) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-06-07

### Changed (BREAKING)

- **Renamed plugin from `bitwarden-software-engineer` → `bitwarden-engineering-building`.** Reframed from a role-based identity ("the software engineer") into an activity-mode identity ("an engineer in building mode — implementing stories, reviewing PRs, preparing commits and pull requests, shipping code"). The split with `bitwarden-engineering-shaping` (formerly `bitwarden-tech-lead`) is by activity, not seniority — same engineer steps between modes as the work demands. Any agent or workflow invoking `Agent(bitwarden-software-engineer)` must switch to `Agent(bitwarden-engineering-building)`. The plugin directory, `plugin.json` name, `marketplace.json` entry, root README catalog row, and agent frontmatter `name:` are all renamed; the agent body rewrite (absorbing the mode reframe into the AGENT.md prose, examples, and orientation rubric) lands in subsequent commits on this PR before the draft moves out of draft.

## [1.0.0] - 2026-05-19

### Changed

- Agent realigned with the canonical "Software Engineer" role on the Engineering Career Ladder (Engineering Excellence, Delivery & Impact, Leadership & Communication) and the description now includes four `<example>` blocks for orchestrator routing.
- Renamed `agents/bitwarden-software-engineer.md` → `agents/AGENT.md` to match the convention used by sibling agent plugins.
- Plugin/marketplace descriptions and README catalog row rewritten to match; added `software-engineer` to keywords.
- Plugin `README.md` refreshed to match the new agent-only framing (the 0.4.0 skills migration left it describing skills the plugin no longer ships).

## [0.4.2] - 2026-05-13

### Fixed

- Added `dotnet format` to the server repo verification steps so the agent auto-corrects encoding and style violations (including BOM) after file edits.

## [0.4.1] - 2026-05-07

### Fixed

- Added `Skill` to the agent's `tools:` frontmatter. Without it, the agent could not invoke Claude Code skills, so slash-command and skill-based workflows silently failed to dispatch.

## [0.4.0] - 2026-04-21

### Changed

- Aligned description in the README.md with the plugin.json.

### Removed

- Removed the repo specific skills and migrated them to their respective repos. Claude Code uses progressive disclosure to use them when needed.

## [0.3.3] - 2026-04-15

### Changed

- Updated `writing-database-queries` skill: clarified dual-ORM architecture, rewrote EDD section to reflect no-rollback deployment model, documented stored procedure compatibility patterns, simplified key locations, and removed Cloud/Self-hosted labels from ORM descriptions

## [0.3.2] - 2026-04-15

### Changed

- Apply prettier formatting to markdown and JSON files

## [0.3.1] - 2026-04-13

### Changed

- `implementing-dapper-queries` skill now distinguishes SSDT source files (`src/Sql/dbo/`) from migration scripts (`util/Migrator/DbScripts/`), clarifying when to use `CREATE PROCEDURE` vs `CREATE OR ALTER PROCEDURE`

## [0.3.0] - 2026-02-23

### Added

- Cross-plugin skill awareness: agent now proactively invokes security engineer skills (`reviewing-security-architecture`, `analyzing-code-security`, `reviewing-dependencies`, `detecting-secrets`) when the `bitwarden-security-engineer` plugin is installed alongside

## [0.2.0] - 2026-02-09

### Added

- `implementing-dapper-queries` and `implementing-ef-core` skills
- Inlined critical rules and do/don't code examples in all skills
- Verification steps and skill routing in agent file
- Plugin registered in marketplace.json

### Changed

- Reframed all skills to focus on rationale; inlined top rules from contributing.bitwarden.com
- Consolidated `guides/` content into standalone skills to eliminate duplication

### Removed

- `guides/` directory (content merged into standalone skills)
- `tools` field from skill frontmatter
- `rust` keyword from plugin.json

## [0.1.0] - 2025-12-11

### Added

- Initial plugin with `bitwarden-software-engineer` agent
- `writing-client-code`, `writing-server-code`, `writing-database-queries` skills
