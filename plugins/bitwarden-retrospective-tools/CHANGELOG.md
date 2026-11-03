# Changelog

All notable changes to the `bitwarden-retrospective-tools` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-10-26

### Added

- **Jira and Confluence activity collection**: new `gather-atlassian.sh` script collects each service's activity independently, skipping gracefully when its tokens are unset.
- **Search-based GitHub PR collection**: new `gather-gh-search.sh` script replaces the 300-event/30-day activity API cap with paginated GraphQL searches for authored, reviewed, and commented-on PRs.
- **Daily-recap report wiring**: Jira, Confluence, and search-based PR data now render as stat tiles in `template.html`, with rendering rules documented in `render-guide.md` and gather steps documented in `SKILL.md`.
- **README setup docs**: new "Atlassian Setup (optional)" section documents the four `ATLASSIAN_*` environment variables.

## [1.0.0] - 2026-10-14

### Added

- New plugin for skills that look back on an engineer's own work.
- **`daily-recap` skill**: builds an interactive HTML recap of one workday from the user's Claude Code session logs and GitHub activity, so standup, 1:1 prep, and sharing progress start from a complete record instead of memory. The workday boundary follows a configurable local cutoff hour so late-night work counts toward the day it continues.
