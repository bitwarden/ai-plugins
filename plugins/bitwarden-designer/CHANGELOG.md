# Changelog

All notable changes to the `bitwarden-designer` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-05-22

### Added

- Initial release. `bitwarden-designer` is the persona half of the design plugin pair — a Bitwarden product designer agent that holds the design team's Code of Conduct and the 30/60/90 critique framework, and dispatches into the `bitwarden-design-tools` toolkit for everything else.
- `bitwarden-designer` agent with stage-aware critique dispatch, explicit boundaries against engineering-side counterparts (tech lead, shepherd), and cross-plugin composition into `bitwarden-design-tools`.
- Two in-plugin skills:
  - `design-review` — Code of Conduct combined with the 30/60/90 critique framework. Ported verbatim from the `designer-agent-skills` branch in `bitwarden/clients`.
  - `facilitating-design-critique` — run or participate in a Bitwarden design critique (weekly team critique or Product Design Review). Grounded in the Weekly Design Critique & Etiquette quick guide and the Product Design Review Guidelines.
- Required cross-plugin dependencies on `bitwarden-design-tools` (six toolkit skills) and `bitwarden-atlassian-tools` (Confluence access).
