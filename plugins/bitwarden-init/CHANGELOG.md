# Changelog

All notable changes to the Bitwarden Init plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-01-13

### Added
- Two-phase initialization: `/bitwarden-init:init` now chains Anthropic's `/init` with Bitwarden enhancement
- `run-init-chain.sh` script that orchestrates the two-phase process
- `/bitwarden-init:enhance` command for enhancing existing CLAUDE.md files independently

### Changed
- `/bitwarden-init:init` now runs a bash script that invokes Anthropic's `/init` first, then enhances with Bitwarden's template
- Improved CLAUDE.md generation with comprehensive codebase analysis from both sources

## [1.0.0] - 2026-01-13

### Added
- Initial release of bitwarden-init plugin
- `/bitwarden-init:init` slash command for generating CLAUDE.md files
- Standardized six-section template format:
  - Overview
  - Architecture & Patterns
  - Stack Best Practices
  - Anti-Patterns
  - Data Models
  - Configuration, Security, and Authentication
