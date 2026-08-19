# Bitwarden Delivery Tools

Delivery lifecycle skills for Bitwarden initiatives — from routing work through the Software Initiative Funnel and running cross-team work transitions, down to the day-to-day mechanics of committing, opening pull requests, running preflight checks, and labeling changes.

## Overview

These skills define delivery **process** — initiative phases, transition playbooks, commit formats, PR workflows, quality gates, and labeling conventions. Platform-specific details (build commands, lint tools, test runners) are discovered dynamically from each repo's CLAUDE.md.

The plugin spans three concerns:

- **Lifecycle** — how cross-cutting initiatives move through phases and how ownership transitions between teams.
- **Technical design** — how teams apply architectural judgment inside their scope.
- **Mechanics** — how individual changes get committed, reviewed, and merged.

Tech Breakdown drafting lives in the [`bitwarden/tech-breakdowns`](https://github.com/bitwarden/tech-breakdowns) repository, where the templates and per-team folder conventions are canonical.

Any agent (tech-lead, software-engineer, shepherds, others) can compose these skills as needed.

## Skills

### Lifecycle

| Skill                              | Triggers                                                | Purpose                                                                                                    |
| ---------------------------------- | ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `navigating-the-initiative-funnel` | "initiative funnel", "scoping & commitment", "shepherd" | Phase-by-phase tech-lead participation across Bitwarden's Software Initiative Funnel                       |
| `running-work-transitions`         | "work transition", "handoff", "transition playbook"     | Both-sides playbook for receiving or originating ownership transitions (initiatives, frameworks, runbooks) |

### Technical design

| Skill                    | Triggers                                                                                          | Purpose                                                                                                                                                           |
| ------------------------ | ------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `architecting-solutions` | "plan the solution", "assess blast radius", "evaluate trade-offs", "should Architecture weigh in" | Architectural judgment framework: security mindset, blast radius, Bitwarden-specific constraints, and the signals that warrant pulling in the Architecture group. |

### Mechanics

| Skill                    | Triggers                                                                                                 | Purpose                                                                                                                                                     |
| ------------------------ | -------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `committing-changes`     | "commit", "stage changes"                                                                                | Default-branch check, commit message format, staging best practices                                                                                         |
| `creating-pull-request`  | "create PR", "open PR"                                                                                   | PR title/body format, draft workflow, AI review labels                                                                                                      |
| `filing-breakdown-tasks` | "create the tickets from tasks.md", "turn this breakdown into Jira tickets", "file the epic and stories" | Turn a `tasks.md` decomposition into epic + child ticket drafts, then hand off to `filing-jira-tickets` to file them. Requires `bitwarden-atlassian-tools`. |
| `force-multiplier`       | "across all repos", "in bulk"                                                                            | Fan one change across many repos or monorepo projects as isolated, piloted draft PRs                                                                        |
| `labeling-changes`       | "label", "change type"                                                                                   | Conventional commit type keywords, CI label mapping                                                                                                         |
| `perform-preflight`      | "preflight", "self review"                                                                               | Pre-commit quality gate checklist                                                                                                                           |

## Design Principle

Each skill owns the **workflow** (what steps to follow, what format to use). The repo's CLAUDE.md owns the **platform specifics** (which linter to run, which test command to use, which security rules apply). This separation allows the same skills to work across Android, iOS, Server, SDK, and Clients repos.

The lifecycle skills follow the same principle: they describe the funnel and transition mechanics. The canonical references — [Software Initiative Funnel](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/584515614) and [Work Transition Playbook](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2521038855) — live in Confluence and are fetched on demand.

## Related Plugins

Several skills in this plugin reference tools or skills provided by sibling plugins. Install these alongside `bitwarden-delivery-tools` for full functionality:

- **`bitwarden-atlassian-tools`** — provides the Jira/Confluence MCP tools used by `navigating-the-initiative-funnel`, and the `filing-jira-tickets` skill plus its opt-in Jira write tools that `filing-breakdown-tasks` hands off to.
- **`bitwarden-security-engineer`** — provides `Skill(bitwarden-security-context)`, referenced from `architecting-solutions`.
- **`bitwarden-code-review`** — provides `/bitwarden-code-review:code-review-local` and `Skill(performing-multi-agent-code-review)`, the code-review gate `creating-pull-request` runs before opening a PR. If it is absent, `creating-pull-request` prompts you to install it rather than skip the review.

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
