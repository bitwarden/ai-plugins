# Changelog

All notable changes to the `bitwarden-software-engineer` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

## [0.1.0] - 2024-12-11

### Added

- Initial plugin with `bitwarden-software-engineer` agent
- `writing-client-code`, `writing-server-code`, `writing-database-queries` skills
