# Changelog

All notable changes to the Bitwarden Design Tools Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-05-22

### Added

- New `applying-bitwarden-branding` skill that applies Bitwarden's canonical brand identity (palette, Inter, official logo lockup, 36px radius foundation) to standalone HTML deliverables — recaps, dashboards, mockups, one-pagers, slides. The skill is explicit about the boundary between **canonical** brand guidance (lifted from `bitwarden.com/brand`) and **pragmatic** deliverable choices the brand site is silent on (surface mode, heading scale, code font, component shapes, voice/tone, accessibility specifics).
- Reference docs: `color-palette.md`, `typography.md`, `logo-usage.md`.
- Assets:
  - `bitwarden-tokens.css` — palette + radius + Inter on `:root`. Intentionally lean: no component CSS, no dark-surface vars, no gradients.
  - `bitwarden-lockup-official.svg` — the full official lockup file, verbatim from `images.ctfassets.net/.../BitwardenLogo.svg`. Contains every variant and color on one canvas; serves as the canonical reference.
  - Derived per-variant assets, each with its path data extracted verbatim from the official lockup (only the `<svg>` wrapper and `viewBox` crop are local):
    - `bitwarden-lockup-horizontal-blue.svg`, `bitwarden-lockup-horizontal-white.svg`
    - `bitwarden-lockup-vertical-blue.svg`, `bitwarden-lockup-vertical-white.svg`
    - `bitwarden-shield-blue.svg`, `bitwarden-shield-white.svg`
    - `bitwarden-wordmark-blue.svg`, `bitwarden-wordmark-white.svg`
- Example: `on-brand-one-pager.html` demonstrating both a **light surface** and a **dark surface** composition. The dark surface is labeled pragmatic and derives the background from `--bw-deep-blue` rather than introducing a new neutral. Explicitly not a prescribed component vocabulary.
