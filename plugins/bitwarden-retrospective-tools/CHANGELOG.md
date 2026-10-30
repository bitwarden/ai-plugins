# Changelog

All notable changes to the `bitwarden-retrospective-tools` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-10-30

### Added

- **`weekly-recap` skill**: thin skill reusing `daily-recap`'s scripts, template, and references (via `CLAUDE_PLUGIN_ROOT` sibling paths, no copied code) to cover a Monday-to-Friday workweek instead of a single day; weekly trigger phrasing moved here from `daily-recap`.

### Changed

- **Standup card restructured to Platform RAG format**: the standup card now renders a red/amber/green status dot plus a BLUF line above the Last week/This week/Blockers (or Yesterday/Today/Blockers) sections, driven by in-window evidence only (returned items, Blocked transitions, PRs with changes requested, open/deferred streams) per the documented heuristic in `render-guide.md`.
- **Standup Copy output emits Platform RAG text with markdown links**: the Copy button now emits Slack-shortcode RAG status plus markdown links (`[text](href)`) instead of plain text, so links survive copy/paste.
- **Standup bullet rules documented and enforced**: outcome-first phrasing, link-on-the-noun placement, and no per-bullet status tokens, documented in `render-guide.md` and `SKILL.md`.

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
