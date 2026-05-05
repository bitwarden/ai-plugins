# Bitwarden Delivery Tools

Generic delivery workflow skills for committing, PR creation, preflight checks, and change labeling across any Bitwarden repository.

## Overview

These skills define the delivery **process** — commit formats, PR workflows, quality gates, and labeling conventions. Platform-specific details (build commands, lint tools, test runners) are discovered dynamically from each repo's CLAUDE.md.

## Skills

| Skill                   | Triggers                   | Purpose                                                |
| ----------------------- | -------------------------- | ------------------------------------------------------ |
| `committing-changes`    | "commit", "stage changes"  | Commit message format, staging best practices          |
| `creating-pull-request` | "create PR", "open PR"     | PR title/body format, draft workflow, AI review labels |
| `labeling-changes`      | "label", "change type"     | Conventional commit type keywords, CI label mapping    |
| `perform-preflight`     | "preflight", "self review" | Pre-commit quality gate checklist                      |

## Design Principle

Each skill owns the **workflow** (what steps to follow, what format to use). The repo's CLAUDE.md owns the **platform specifics** (which linter to run, which test command to use, which security rules apply). This separation allows the same skills to work across Android, iOS, Server, SDK, and Clients repos.

## Installation

```bash
/plugin install bitwarden-delivery-tools@bitwarden-marketplace
```

## Usage

Skills activate based on natural-language triggers during your delivery workflow:

```
Commit these changes
```

```
Create a PR for this branch
```

```
Run preflight before I commit
```

```
What change type should I use for this PR?
```
