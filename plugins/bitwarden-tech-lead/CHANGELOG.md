# Changelog

All notable changes to the `bitwarden-tech-lead` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-05-07

### Added

- `contributing-to-technical-strategy` skill — guides the path from Technical Strategy Ideas through BW Initiatives down to team-level epic and story breakdown.
- `architecting-solutions` gains _Working with the Architecture Group (Holistic Coherence)_ and _Working with the Initiative Shepherd_ sections.

### Changed

- Reframed `AGENT.md` from "senior software architect" to a tech lead embedded in a product team. Adds a scope-based decision tree for when to operate alongside a shepherd vs. take on the shepherd role.
- Agent dispatches to `Skill(navigating-the-initiative-funnel)` and `Skill(running-work-transitions)` from `bitwarden-delivery-tools` (1.1.0+).
- Plugin description and keywords updated to reflect the holistic-architecture and technical-strategy framing.

## [2.0.0] - 2026-04-24

### Changed

- **BREAKING:** Renamed plugin from `bitwarden-architect` to `bitwarden-tech-lead`. Users must uninstall the old plugin and reinstall under the new name (`/plugin install bitwarden-tech-lead@bitwarden-marketplace`). The agent's callable identifier (`name:` in AGENT.md frontmatter) also changed to `bitwarden-tech-lead`.

## [1.0.0] - 2026-04-16

### Added

- Architect agent for technical planning and implementation phasing across Bitwarden repositories
- `architecting-solutions` skill with Bitwarden-specific architectural principles, security mindset, and judgment heuristics
- Cross-plugin integration with security-engineer, product-analyst, software-engineer, and atlassian-tools plugins
