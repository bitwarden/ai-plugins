# Bitwarden Architect

Generic software architect agent for planning features across any Bitwarden repository.

## Overview

The architect agent transforms requirements, tickets, or feature ideas into precise, actionable, phased implementation plans before any code is written. It works across all Bitwarden repositories (Android, iOS, Server, SDK, Clients) by dynamically discovering platform-specific context from each repo's CLAUDE.md and local planning skills.

## Agent

| Agent | Model | Description |
|-------|-------|-------------|
| `architect` | opus | Plans and designs implementations for any Bitwarden repo |

## How It Works

1. **Context Discovery**: Reads the repo's CLAUDE.md to learn architecture constraints, security rules, and available skills
2. **Skill Invocation**: Finds and invokes the repo's planning skill (e.g., `planning-android-implementation`, `planning-ios-implementation`) for platform-specific guidance
3. **Gap Analysis**: Evaluates technical gaps (security, SDK, extensions, data migration, performance)
4. **Codebase Exploration**: Deploys sub-agents to find existing patterns and similar implementations
5. **Plan Production**: Outputs a standardized Implementation Plan with phased tasks, file manifest, and risk assessment

## Deliverables

- **Implementation Plan** (`{slug}-IMPLEMENTATION-PLAN.md`) — Architecture design, phased task breakdown, file manifest, risk assessment
- **Work Breakdown Document** (`{slug}-WORK-BREAKDOWN.md`) — Jira-ready tasks consolidating product and technical breakdowns
- **Architecture Review** — Verification of implementation adherence to the plan

## Requirements

| Plugin | Required For |
|--------|-------------|
| `bitwarden-atlassian-tools` | Optional — Jira/Confluence fetching |

## Installation

Install via the Bitwarden AI Marketplace.
