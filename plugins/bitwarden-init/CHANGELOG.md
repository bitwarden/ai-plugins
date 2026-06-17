# Changelog

All notable changes to the Bitwarden Init plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-05-14

### Added

- `/bitwarden-init:init-user` — Q&A-driven initialization of user-level `~/.claude/CLAUDE.md` from opt-in behavioral modules (intellectual honesty, simplicity, surgical changes, code-review mutation lockdown, …)
- `/bitwarden-init:init-workspace` — Initializes `<workspace>/.claude/CLAUDE.md` for the directory containing all locally-cloned Bitwarden repos, with auto-detection of workspace root (walks up looking for sibling `.git` directories) and explicit confirmation before any write
- `/bitwarden-init:enhance-user` and `/bitwarden-init:enhance-workspace` — Refresh existing user-level or workspace-level CLAUDE.md files by adding missing modules
- Modular template library under `templates/user/` (10 modules) and `templates/workspace/` (8 modules) — each module is opt-in and editable; defaults are derived from one Bitwarden engineer's published preferences, not imposed as a standard
- Safety guardrails for global-state writes: timestamped backups before overwriting and unified-diff preview with explicit `Apply` confirmation
- `allowed-tools` on the four new commands narrows `Bash` to the specific subcommands each command needs (`diff`, `cp`, `date`, `rm`, plus `find`/`wc`/`tr`/`dirname`/`mkdir` for the workspace flows) so the model can't invoke arbitrary shell tools

### Changed

- README documents the three-level CLAUDE.md hierarchy (user / workspace / repo), the new commands, and a Usage section showing the typical first-time setup order

## [1.1.0] - 2026-02-23

### Added

- Post-generation validation in `/enhance` command: invokes config validator `reviewing-claude-config` and security engineer `detecting-secrets` skills to validate generated CLAUDE.md files when sibling plugins are installed

## [1.0.0] - 2026-01-14

### Added

- Initial release of bitwarden-init plugin
- `/bitwarden-init:init` command that chains Anthropic's `/init` with Bitwarden enhancement
- `/bitwarden-init:enhance` command for enhancing existing CLAUDE.md files
- Two-phase initialization process:
  - Phase 1: Runs Anthropic's `/init` for codebase analysis
  - Phase 2: Enhances with Bitwarden's standardized template
- Comprehensive template with 11 standardized sections:
  - Overview
  - Architecture & Patterns
  - Development Guide
  - Data Models
  - Security & Configuration
  - Testing
  - Code Style & Standards
  - Anti-Patterns
  - Deployment
  - Troubleshooting
  - References
