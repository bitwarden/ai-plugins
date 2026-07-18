# Bitwarden Delivery Tools

Delivery lifecycle skills for Bitwarden initiatives — from routing work through the Software Initiative Funnel and running cross-team work transitions, through drafting Tech Breakdowns and decomposing them into tasks, down to the day-to-day mechanics of committing, opening pull requests, running preflight checks, and labeling changes.

## Overview

These skills define delivery **process** — initiative phases, transition playbooks, tech-breakdown drafting, task decomposition, commit formats, PR workflows, quality gates, and labeling conventions. Platform-specific details (build commands, lint tools, test runners) are discovered dynamically from each repo's CLAUDE.md.

The plugin spans three concerns:

- **Lifecycle** — how cross-cutting initiatives move through phases and how ownership transitions between teams.
- **Technical design** — how teams apply architectural judgment inside their scope, draft Tech Breakdowns under Bitwarden's standard template, and decompose them into tasks.
- **Mechanics** — how individual changes get committed, reviewed, and merged.

Any agent (tech-lead, software-engineer, shepherds, others) can compose these skills as needed.

## Skills

### Lifecycle

| Skill                              | Triggers                                                | Purpose                                                                                                    |
| ---------------------------------- | ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `navigating-the-initiative-funnel` | "initiative funnel", "scoping & commitment", "shepherd" | Phase-by-phase tech-lead participation across Bitwarden's Software Initiative Funnel                       |
| `running-work-transitions`         | "work transition", "handoff", "transition playbook"     | Both-sides playbook for receiving or originating ownership transitions (initiatives, frameworks, runbooks) |

### Technical design

| Skill                       | Triggers                                                                                                                              | Purpose                                                                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `architecting-solutions`    | "plan the solution", "assess blast radius", "evaluate trade-offs", "should Architecture weigh in"                                     | Architectural judgment framework: security mindset, blast radius, Bitwarden-specific constraints, and the signals that warrant pulling in the Architecture group.                       |
| `starting-breakdown`        | "start a tech breakdown", "create a new breakdown for X", "set up the breakdown file"                                                 | Set up a new Tech Breakdown file in `bitwarden/tech-breakdowns`: gather context from the user, copy the template, fill the Status block.                                                |
| `developing-breakdown-spec` | "understand the work", "resolve open questions", "write the breakdown spec", "Spec Alternatives"                                      | Resolve open design questions one at a time with concrete options, then capture what's being built into the Specification section.                                                      |
| `developing-breakdown-plan` | "develop the plan", "draft the implementation plan", "map per-layer impact", "scan for in-flight work", "identify cross-team impacts" | Develop the Plan section after the Spec is filled: technical architecture, per-layer impact, in-flight collision scan, cross-team impact mapping, and self-review. Supports resumption. |
| `decomposing-into-tasks`    | "decompose into tasks", "draft the tasks section", "break this into stories", "split into Jira tickets", "fill in the tasks table"    | Decompose a Plan into a `tasks.md` document with one entry per future Jira work item.                                                                                                   |

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

## Related Plugins

Several skills in this plugin reference tools or skills provided by sibling plugins. Install these alongside `bitwarden-delivery-tools` for full functionality:

- **`bitwarden-atlassian-tools`** — provides the Jira/Confluence MCP tools used by `navigating-the-initiative-funnel` and the breakdown skills.
- **`bitwarden-security-engineer`** — provides `Skill(bitwarden-security-context)` and `Skill(threat-modeling)`, referenced from `architecting-solutions`.

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
Decompose this breakdown's Plan into tasks
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
