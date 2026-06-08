# Bitwarden Delivery Tools

Delivery lifecycle skills for Bitwarden initiatives — from routing work through the Software Initiative Funnel and running cross-team work transitions, through starting and developing Tech Breakdowns and syncing their Tasks sections with Jira, down to the day-to-day mechanics of committing, opening pull requests, running preflight checks, and labeling changes.

## Overview

These skills define delivery **process** — initiative phases, transition playbooks, tech-breakdown drafting and cross-team signoff workflows, commit formats, PR workflows, quality gates, and labeling conventions. Platform-specific details (build commands, lint tools, test runners) are discovered dynamically from each repo's CLAUDE.md.

The plugin spans three concerns:

- **Lifecycle** — how cross-cutting initiatives move through phases and how ownership transitions between teams.
- **Technical design** — how teams draft and circulate Tech Breakdowns under Bitwarden's standard template, and how cross-team signoff and completion communication get coordinated.
- **Mechanics** — how individual changes get committed, reviewed, and merged.

Any agent (tech-lead, software-engineer, shepherds, others) can compose these skills as needed.

## Skills

### Lifecycle

| Skill                              | Triggers                                                | Purpose                                                                                                    |
| ---------------------------------- | ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `navigating-the-initiative-funnel` | "initiative funnel", "scoping & commitment", "shepherd" | Phase-by-phase tech-lead participation across Bitwarden's Software Initiative Funnel                       |
| `running-work-transitions`         | "work transition", "handoff", "transition playbook"     | Both-sides playbook for receiving or originating ownership transitions (initiatives, frameworks, runbooks) |

### Technical design

| Skill                       | Triggers                                                                                     | Purpose                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| --------------------------- | -------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `starting-a-tech-breakdown` | "start a tech breakdown", "create a new breakdown for X", "set up the breakdown file"        | Set up a new Tech Breakdown file in `bitwarden/tech-breakdowns`: gather context from the user, copy the template, fill the Status block. Stops at status `In Planning`.                                                                                                                                                                                                                                                                                                       |
| `doing-a-tech-breakdown`    | "do the breakdown", "work the breakdown", "develop the design", "continue our breakdown"     | Walk the engineer through understanding the work: orient, resolve open design questions one at a time, develop the design (articulate, alternatives, per-layer impact, decomposition, in-flight scan, cross-team impact identification with depth + churn characterization, surface what would surprise, curate Clarifications Log, AI clarify pass). Picking a collaboration model on each impact is an owner task, informed by the depth and churn data the skill captures. |
| `syncing-tasks-with-jira`   | "sync the Jira stories with the breakdown", "create stories from the breakdown", "reconcile" | Keep the Tasks section and its Jira stories in sync — initial creation and ongoing bidirectional reconciliation. Bakes in Bitwarden field mapping (`Technical breakdown`, `Acceptance Criteria`, `Team`), stack-area prefix, dependency links.                                                                                                                                                                                                                                |

### Mechanics

| Skill                   | Triggers                   | Purpose                                                |
| ----------------------- | -------------------------- | ------------------------------------------------------ |
| `committing-changes`    | "commit", "stage changes"  | Commit message format, staging best practices          |
| `creating-pull-request` | "create PR", "open PR"     | PR title/body format, draft workflow, AI review labels |
| `labeling-changes`      | "label", "change type"     | Conventional commit type keywords, CI label mapping    |
| `perform-preflight`     | "preflight", "self review" | Pre-commit quality gate checklist                      |

## Design Principle

Each skill owns the **workflow** (what steps to follow, what format to use). The repo's CLAUDE.md owns the **platform specifics** (which linter to run, which test command to use, which security rules apply). This separation allows the same skills to work across Android, iOS, Server, SDK, and Clients repos.

The lifecycle skills follow the same principle: they describe the funnel and transition mechanics. The canonical references — [Software Initiative Funnel](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/584515614) and [Work Transition Playbook](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2521038855) — live in Confluence and are fetched on demand.

## Installation

```bash
/plugin install bitwarden-delivery-tools@bitwarden-marketplace
```

## Usage

Skills activate based on natural-language triggers during your delivery workflow:

```
What's my role at the scoping & commitment phase of the funnel?
```

```
We're handing off this framework to another team — walk me through the playbook
```

```
Start a Tech Breakdown for this feature — walk me through the scope checklist
```

```
Sync the breakdown's Tasks section with Jira
```

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
