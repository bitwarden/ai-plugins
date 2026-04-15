# Changelog

All notable changes to the `bitwarden-software-engineer` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
