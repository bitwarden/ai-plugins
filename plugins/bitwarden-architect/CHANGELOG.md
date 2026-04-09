# Changelog

All notable changes to the `bitwarden-architect` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-04-08

### Added

- Generic `plan-implement-review` orchestration command — end-to-end pipeline for requirements, architecture, implementation, and multi-agent code review

## [0.1.0] - 2026-04-08

### Added

- Generic `architect` agent for planning features across any Bitwarden repository
- Dynamic context discovery via CLAUDE.md Skills & Commands table
- Standardized output format: Implementation Plan, Work Breakdown Document, Architecture Review
- Technical gap analysis checklist (security, multi-account, SDK, extensions, data migration, performance, offline)
- Behavioral guardrails preventing code writing, pattern invention, and requirement assumption
