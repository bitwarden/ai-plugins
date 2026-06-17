# Changelog

All notable changes to the `bitwarden-design-tools` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-06-17

### Changed

- `applying-bitwarden-branding` now covers both **building** on-brand standalone deliverables (dashboards, recaps, reports, slide decks, one-pagers, mockups) and **reviewing** whether a deliverable is on-brand. Reviews are calibrated to separate canonical violations from brand-silent pragmatic choices, and brand-silent choices that visibly shape the deliverable (surface mode, voice and tone) are surfaced to the requester when working interactively rather than silently defaulted. The canon is now bundled (assets + tokens) for offline, verbatim use rather than referenced externally.

### Added

- Bundled brand assets for `applying-bitwarden-branding`: `bitwarden-tokens.css` (palette + 36px radius + Inter on `:root`), the official lockup (`bitwarden-lockup-official.svg`), and derived per-variant SVGs (horizontal and vertical lockups, shield, wordmark, in blue and white), each with path data verbatim from the official lockup.
- Reference docs `typography.md` and `logo-usage.md`, and `examples/on-brand-one-pager.html` demonstrating light and dark compositions.
- `scripts/verify-brand-canon.sh` to detect drift between the bundled palette and the brand repository's `palette.scss` and report the correct values to use (drift detector; runs on demand). It never modifies the bundle.
- `evals/` regression harness for `applying-bitwarden-branding`: mock-only off-brand and on-brand fixtures, a pre-registered objective rubric, and a deterministic grader (`grade.py`) that reads the canonical palette and the official-logo signatures from the live bundled assets so it tracks canon changes. The grader covers the context-free checks (Inter, primary palette, verbatim lockup, 36px radius, off-brand-font and off-palette detection); the calibration dimensions (review specificity, false-positive/over-flagging) are left to a blind LLM grader.

### Fixed

- `--bw-yellow` corrected to `#FDC700` to match the brand repository's `$tertiary-yellow` (was `#FFD700`).

### Removed

- `references/brand-assets.md` — its repo-path asset inventory and trademark note are folded into `references/logo-usage.md`.

## [0.1.0] - 2026-05-22

### Added

- Initial release. `bitwarden-design-tools` is the toolkit half of the design plugin pair — non-persona skills for the design lifecycle, composed by the `bitwarden-designer` agent and usable standalone.
- Six skills:
  - `content-style-guide` — Bitwarden's product content style guide for GUI copy. Ported from the `designer-agent-skills` branch in `bitwarden/clients`, with progressive disclosure into `references/grammar-mechanics.md` and `references/accessibility-rules.md`.
  - `using-figma` — read and inspect Figma designs via the Dev Mode MCP server. Read-only scope by `allowed-tools`; per-job-to-be-done tool selection across the read surface, with setup notes in `references/setup.md` and per-tool reference deferred to Figma's canonical docs.
  - `applying-bitwarden-branding` — apply Bitwarden brand standards (logo, color, typography, iconography, capitalization) grounded in [bitwarden.com/brand](https://bitwarden.com/brand/) and the [bitwarden/brand](https://github.com/bitwarden/brand) repository. Full palette and asset inventory in `references/color-palette.md` and `references/brand-assets.md`.
  - `preparing-design-handoff` — the end-of-In-Design gate / checklist. Confirm the Figma file is Ready-for-Dev (sections aligned to stories, tokens library-bound, strings annotated, edge states covered) and that the Jira state is aligned (Figma linked to the Epic's Design field, sections marked Ready for Dev, EM transitions the Epic).
  - `evolving-design-system-components` — propose new patterns or modify existing components per the published governance process. Figma conventions in `references/figma-conventions.md`.
  - `navigating-design-jira-process` — final designs attached to tickets, the 30/60/90 critique cadence tracked in Figma, status transitions on engineering epics and stories, and the one-off engineering story flow (link Figma to the story's Design field, unassign, comment that the design is ready).
- Required cross-plugin dependency on `bitwarden-atlassian-tools` for Confluence access to the canonical design-team process pages.
