# Changelog

All notable changes to the Claude Retrospective Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-03

### Added

- Initial release of `claude-retrospective` plugin
- `retrospecting` skill for comprehensive session analysis with three analysis depths (quick/standard/comprehensive)
- `extracting-session-data` skill with 4 bash scripts for accessing Claude Code native session logs:
  - `locate-logs.sh`, `list-sessions.sh`, `extract-data.sh` (8 extraction types), `filter-sessions.sh` (8 filter criteria)
- `analyzing-git-sessions` skill for git history analysis with three output formats (concise/detailed/code review)
- Multi-source data collection: git history, session logs, code quality metrics, user feedback, sub-agent feedback
- Automatic depth recommendation based on session size with user override capability
- Context budget management system with adaptive strategy (high/medium/low budget thresholds)
- Configuration improvement loop: suggest and apply updates to `.claude/CLAUDE.md`, skills, or agents based on findings
- Two report templates (quick and comprehensive) with evidence-based standards
- Report storage in `${CLAUDE_PROJECT_DIR}/.claude/skills/retrospecting/reports/` with ISO date format

---

## Version Format

Plugin version tracks retrospective system changes:

- **Major version**: Breaking changes to report templates, data collection methods, or skill interfaces
- **Minor version**: New analysis features, additional data sources, new report types, skill enhancements
- **Patch version**: Bug fixes, clarifications, documentation improvements, script refinements
