# Changelog

All notable changes to the `bitwarden-retrospective-tools` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-14

### Added

- New plugin for skills that look back on an engineer's own work.
- **`daily-recap` skill**: builds an interactive HTML recap of one workday from the user's Claude Code session logs and GitHub activity, so standup, 1:1 prep, and sharing progress start from a complete record instead of memory. The workday boundary follows a configurable local cutoff hour so late-night work counts toward the day it continues.
