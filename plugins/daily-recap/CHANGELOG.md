# Changelog

All notable changes to the Daily Recap Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-01

### Added

- Initial release with `engineering-recap` skill — generates an interactive HTML recap of the user's engineering work for a given day
- Output written to `${CLAUDE_PLUGIN_DATA}/recaps/engineering-recap-{YYYY-MM-DD}.html` (persistent per-plugin storage; survives plugin updates). Filename pattern uses a `{recap-type}-recap-` prefix to leave room for sibling recap skills
- Local-timezone day-boundary handling (late-night work folds into the prior workday); cutoff hour and timezone are configurable via the `DAILY_RECAP_CUTOFF_HOUR` and `TZ` env vars
- Bundled HTML template tuned to the Bitwarden brand palette (Bitwarden Blue, Teal, Inter font, brand shield)
- Bundled `gather-gh-events.sh` script that pulls GitHub events scoped to the user's workday window
- Bundled `render-guide.md` reference covering placeholder map and HTML injection recipes
- Cross-plugin integration with `claude-retrospective:extracting-session-data` for session extraction
