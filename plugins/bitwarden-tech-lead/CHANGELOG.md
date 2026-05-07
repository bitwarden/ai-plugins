# Changelog

All notable changes to the `bitwarden-tech-lead` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-05-07

### Added

- `contributing-to-technical-strategy` skill. Full vertical guidance from Technical Strategy Ideas through BW Initiatives down to team-level epic and story breakdown: recognizing when a team-level pattern belongs upstream, framing a TSI well enough for Architecture to evaluate it, the ARCH idea ↔ BW Initiative linkage, and defining epic- and story-level work downward.
- `architecting-solutions` gains two sections: _Working with the Architecture Group (Holistic Coherence)_ drawing on the Architecture / Engineering Operating Model, and _Working with the Initiative Shepherd_ drawing on the Software Initiative Funnel.

### Changed

- Reframed `AGENT.md` from "senior software architect" to a tech lead embedded in a product team who works alongside shepherds and the architecture group rather than replacing either. Added a three-rule decision tree for distinguishing "operate alongside the shepherd" from "propose taking on the shepherd role" based on scope rather than title.
- AGENT.md now dispatches to `Skill(navigating-the-initiative-funnel)` and `Skill(running-work-transitions)` cross-plugin (skills live in `bitwarden-delivery-tools`). The agent stays funnel-aware while the funnel mechanics are agent-neutral and reusable.
- Skill descriptions and content rewritten in third-person, process-focused voice (per team feedback). Persona framing lives in `AGENT.md`, not in the skills.
- Plugin description and keywords updated to reflect the holistic-architecture and technical-strategy framing.
- README updated to list the two skills retained in this plugin and the cross-plugin delivery-lifecycle skills.

### Removed

- `navigating-the-initiative-funnel` and `running-work-transitions` skills (moved to `bitwarden-delivery-tools` 1.1.0 in [#109](https://github.com/bitwarden/ai-plugins/pull/109) so multiple agents can compose them). The agent invokes them cross-plugin.

## [2.0.0] - 2026-04-24

### Changed

- **BREAKING:** Renamed plugin from `bitwarden-architect` to `bitwarden-tech-lead`. Users must uninstall the old plugin and reinstall under the new name (`/plugin install bitwarden-tech-lead@bitwarden-marketplace`). The agent's callable identifier (`name:` in AGENT.md frontmatter) also changed to `bitwarden-tech-lead`.

## [1.0.0] - 2026-04-16

### Added

- Architect agent for technical planning and implementation phasing across Bitwarden repositories
- `architecting-solutions` skill with Bitwarden-specific architectural principles, security mindset, and judgment heuristics
- Cross-plugin integration with security-engineer, product-analyst, software-engineer, and atlassian-tools plugins
