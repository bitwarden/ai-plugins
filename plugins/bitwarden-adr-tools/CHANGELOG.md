# Changelog

All notable changes to the `bitwarden-adr-tools` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-09-23

### Added

- New plugin for skills that act on Bitwarden's Architecture Decision Records.
- **`consulting-adrs` skill** — checks a design, change, plan, or threat model against Bitwarden's [Architecture Decision Records](https://contributing.bitwarden.com/architecture/adr/), or locates/summarizes the catalog, returning structured findings (conflict, gap, stale-reference, aligned) with cited ADRs.
