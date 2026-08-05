# Changelog

All notable changes to the `bitwarden-planning-tools` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-30

### Added

- New plugin establishing the pre-implementation planning home, counterpart to `bitwarden-delivery-tools` (post-implementation).
- **`consulting-adrs` skill** — checks a design, change, plan, or threat model against Bitwarden's [Architecture Decision Records](https://contributing.bitwarden.com/architecture/adr/), or locates/summarizes the catalog, returning structured findings (conflict, gap, aligned) with cited ADRs. Workflow-agnostic and reusable cross-plugin. Ships with a triggering/structure/behavior eval set and recorded baselines on `claude-opus-4-8` (triggering 7/8 should-trigger, 6/6 should-not; behavior with-skill 1.00 vs baseline 0.78 over 9 cases). `WebFetch` scoped to `contributing.bitwarden.com`.
