# Changelog

All notable changes to the `bitwarden-implementer` plugin (previously `bitwarden-software-engineer`) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-06-30

### Changed

- **BREAKING: Renamed plugin from `bitwarden-software-engineer` to `bitwarden-implementer`.** The old persona-shaped name described a role; the new name describes the workflow the agent actually drives — one Jira task through implementation to an open PR.
- **BREAKING: Re-scoped from a career-ladder persona to a workflow-shaped loop that ends at PR open.** The agent now runs a defined six-phase loop: Orient → Plan → Implement → Preflight → Self-review → Ship. Each phase composes an existing skill by name rather than restating rules.
- Self-review before shipping via `bitwarden-code-review:performing-multi-agent-code-review` on the local diff. Critical and important findings block the ship.
- Plan phase delegates to the built-in `Plan` agent rather than being owned inline.
- README refactored to workflow framing with a per-phase composition table.
- Marketplace and plugin.json descriptions rewritten. Keywords updated from `typescript, csharp, sql, fullstack, software-engineer` to `implementation, breakdown, pull-request, loop, self-review`.

### Removed

- **Teammate PR review responsibility.** Reviewing a teammate's PR is `bitwarden-code-review`.
- **Post-PR feedback iteration.** Addressing reviewer feedback on the opened PR is a bare skill call to `bitwarden-code-review:addressing-code-review-comments` — not agent-shaped work. Trimmed per the AI Review Guidelines' skill-first / trigger-aware defaults: human-triggered, small-horizon, and adds no unique isolation value.
- **Ambiguity-navigation responsibility.** Surfacing an ambiguous requirement is a one-turn human interaction, not agent-shaped work. Now expressed only as a scope-boundary rule.
- **Standalone commit and PR authorship responsibility.** These are composed via `bitwarden-delivery-tools:committing-changes` and `creating-pull-request` rather than owned inline.
- **Career-ladder framing paragraph** (Engineering Excellence / Delivery & Impact / Leadership & Communication). Replaced with a workflow-shaped identity paragraph.

### Added

- `evals/` scaffold with README, baseline template, and case files covering positive triggers (story, bug, breakdown-doc reference), near-miss negatives (PR review, decompose breakdown, architectural choice, plan-only), and behavior cases (golden path, scope drift declined, ambiguity surfaced, self-review-finds-and-fixes, PR shape, orient-with-breakdown-and-epic-siblings, blocker-check). Cases are run via `/skill-creator:skill-creator`. Blocking per the [AI Review Guidelines](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/3101458451/AI+Review+Guidelines) for any future change to `AGENT.md`.
- **Blocker check in Orient.** Before proceeding to Plan, the agent inspects every `is blocked by` link on the target Jira task; if any blocker is not resolved, it surfaces and stops. Motivated by running the loop against a real ticket (PM-27060) that was blocked by an in-code-review dependency.
- **Phase-tracking tasks.** The agent creates one task per loop phase (Orient → Plan → Implement → Preflight → Self-review → Ship) before starting, and transitions each between `in_progress` and `completed` as it advances. Gives the user a visible progress surface during a run.
- **Shallow-gap investigation in Orient.** Before escalating a specification gap to the human, the agent attempts to close it from the codebase and adjacent Jira context. Only genuine design decisions that the code cannot answer are surfaced as stakeholder questions. Motivated by running the loop against a real thinly-scoped ticket (PM-35093) where the shape of the answer was already discoverable in the code.

### Migration

Users installing by the old name will break. See the README's "Upgrading from `bitwarden-software-engineer`" section for uninstall and install commands.

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
