# Changelog

All notable changes to the Bitwarden Product Analyst plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.4] - 2026-03-12

### Changed

- Remove redundant `skills` field from `plugin.json`; skills are auto-discovered from the `skills/` directory

## [0.1.3] - 2026-03-12

### Changed

- Remove duplicated section list from agent; agent now reads `references/requirements-template.md` directly at the Documentation Phase

## [0.1.2] - 2026-03-12

### Fixed

- Corrected agent path in `plugin.json` from `./agents/product-analyst/AGENT.md` to `./agents/product-analyst.md` so the plugin can discover its agent
- Fixed malformed code fence in `references/requirements-template.md` where the outer `````markdown` block closed prematurely after section 9, leaving sections 10–15 outside the template block

## [0.1.1] - 2026-03-10

### Changed

- Add local files and directories as a first-class spec source (Read, Glob, Grep)
- Add generic web URLs as a spec source (WebFetch)
- Save generated specs to the current working directory instead of the plugin's specs/ folder

## [0.1.0] - 2026-03-04

### Added

- Initial release of Bitwarden Product Analyst plugin
- Product analyst agent for creating comprehensive Bitwarden requirements documents
- `requirements-elicitation` skill for extracting and organizing requirements
- `work-breakdown` skill for decomposing features into implementable tasks
- Requirements document template following Bitwarden standards
- Integration with Bitwarden security vocabulary and principles (P01-P06)
- Support for analyzing multiple sources (GitHub issues, technical docs, user requests)
- Structured requirements output with security considerations
