# Changelog

All notable changes to the Bitwarden Init plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
