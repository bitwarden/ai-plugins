# Bitwarden Delivery Tools

Delivery lifecycle skills for Bitwarden initiatives — from routing work through the Software Initiative Funnel and running cross-team work transitions, through drafting Tech Breakdowns and chasing cross-team signoffs, down to the day-to-day mechanics of committing, opening pull requests, running preflight checks, and labeling changes.

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

| Skill                          | Triggers                                                                                       | Purpose                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ------------------------------ | ---------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `writing-tech-breakdowns`      | "tech breakdown", "cross-team signoff", "affected teams", "stakeholder communication"          | End-to-end Tech Breakdown workflow: drafting the engineering content (Specification, Clarifications Log, Plan, Tasks, Agent Context), the status lifecycle (In Planning → In Progress → Proposed → Accepted → Complete / Rejected), the stakeholder-communication checklist at `In Progress → Proposed` (post to `#team-eng-tech-breakdowns`, contact QA, create Jira stories, hand off to refinement facilitator), the Cross-team engagement signoff table, chasing signoffs, and gate verification at `Proposed → Accepted` |
| `choosing-collaboration-model` | "cross-team change", "collaboration model", "File a Ticket vs Internal Open-Source", "Hodgson" | Per-impact collaboration-model picker (File a Ticket, Internal Open-Source, or rarely Embedded Expert) with `CODEOWNERS`-based trigger detection and an owning-team domain-velocity scan                                                                                                                                                                                                                                                                                                                                      |

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
The breakdown is at Proposed — who needs to sign off and how do I chase them?
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
