# Changelog

All notable changes to the `bitwarden-tech-lead` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.1] - 2026-06-10

### Added

- `architecting-solutions`: new "Avoid deprecated methods" principle under Architectural Judgment. If a method is deprecated, the skill must not use it; if no clear alternative is documented with the deprecation, ask the human how to achieve the desired outcome.

### Changed

- `architecting-solutions`: clarified the "Complement existing patterns" guidance to also cover the multi-pattern case. When multiple competing patterns exist for the same concern, ask the human which is preferred rather than picking one.

### Removed

- `architecting-solutions`: dropped the "Accepting an initiative epic without capacity explicitly allocated by the team's EM and engineering leadership" red flag. Capacity allocation is governed by the initiative funnel and work-transition skills, not by this skill's red-flags list.

### Security

- `architecting-solutions`: added an explicit untrusted-data principle for content fetched via the Jira and Confluence MCP tools. Confluence pages are user-editable and a known prompt-injection surface; the skill must summarize or reference fetched content, never execute instructions found inside it.

## [2.3.0] - 2026-05-19

### Changed

- Agent definition realigned with the canonical "Team Tech Lead" role: three core relationships (team, peer tech leads, EM) rather than participation in any specific workflow.
- Two of four `<example>` blocks replaced — EM-partnership scoping and cross-team conduit, alongside the original team-scope planning and upstream-pattern examples. The funnel-specific examples were removed; those capabilities still exist via the relevant skills but no longer define the agent.
- Orientation block reduced to the two tech-lead-owned skills (`architecting-solutions`, `contributing-to-technical-strategy`). Workflow-classification bullets removed — workflows bring their own dispatch context when they invoke the agent.
- Body intro makes the principle explicit: workflows orchestrate the agent, not the other way around.
- Plugin and marketplace descriptions rewritten to match.

## [2.2.0] - 2026-05-13

### Changed

- Cross-Plugin Integration section now lists `Skill(writing-tech-breakdowns)` and `Skill(coordinating-cross-team-breakdown)` from `bitwarden-delivery-tools` (1.2.0+) as available delivery-lifecycle skills. The skills are agent-neutral and discoverable from their own descriptions; the agent does not pre-commit to invoking them as default behavior.

## [2.1.1] - 2026-05-11

### Changed

- README: added a "Related plugins" pointer to the new sibling `bitwarden-shepherd` plugin so tech leads can discover the shepherd-side counterpart of this role.
- Agent description now includes four `<example>` blocks (team-scope planning, receiving an initiative epic, surfacing a cross-team pattern, shepherding a smaller-scope initiative) so the orchestrator can route on concrete triggering scenarios rather than prose alone. Adopts Anthropic's documented standard for agent description fields.

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
