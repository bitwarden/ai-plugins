# Changelog

All notable changes to the `bitwarden-beads-tools` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-21

### Added

- New plugin of tools that complement the beads (`bd`) issue tracker in Claude Code.
- **Beads pane** tool, which keeps the project's beads in view during a session:
  - **Pane**: lists open, in-progress, and blocked beads from `bd list --json`, grouped by status and sorted by priority, so the state of the work is visible without running `bd` by hand.
  - **Status line**: a one-line count of beads by status, left empty when the project has nothing open.
  - **`/beads-pane` command**: refreshes the list and opens the pane on demand.
  - Refreshes at the start of an interactive session, every 30 seconds after that, after any Bash tool call that runs `bd`, and when the working directory changes; stays hidden outside a beads project.
