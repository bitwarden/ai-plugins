# Bitwarden Delivery Tools

Delivery lifecycle skills for Bitwarden initiatives — from routing work through the Software Initiative Funnel and running cross-team work transitions, down to the day-to-day mechanics of committing, opening pull requests and stacks of them, running preflight checks, and labeling changes.

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

| Skill                     | Triggers                                             | Purpose                                                                                            |
| ------------------------- | ---------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `applying-pr-conventions` | Invoked by the PR workflows, rarely direct           | Composes one PR's title/type-prefix, template body, and label; never reviews, previews, or submits |
| `committing-changes`      | "commit", "stage changes"                            | Default-branch check, commit message format, staging best practices                                |
| `creating-pull-request`   | "create PR", "open PR"                               | Single-branch PR workflow: review gate, conventions, submission preview, `gh pr create`            |
| `filing-breakdown-tasks`  | "tickets from tasks.md", "file the epic and stories" | Turn a breakdown's `tasks.md` into epic + child ticket drafts for `filing-jira-tickets` to file    |
| `force-multiplier`        | "across all repos", "in bulk"                        | Fan one change across many repos or monorepo projects as isolated, piloted draft PRs               |
| `labeling-changes`        | "label", "change type"                               | Conventional commit type keywords, CI label mapping                                                |
| `perform-preflight`       | "preflight", "self review"                           | Pre-commit quality gate checklist, including the per-layer checks for a stacked branch             |
| `stacking-pull-requests`  | "stack these PRs", "stacked diffs"                   | Bitwarden conventions across a chain of dependent PRs; mechanics delegated to `gh-stack`           |

## Design Principle

Each skill owns the **workflow** (what steps to follow, what format to use). The repo's CLAUDE.md owns the **platform specifics** (which linter to run, which test command to use, which security rules apply). This separation allows the same skills to work across Android, iOS, Server, SDK, and Clients repos.

The lifecycle skills follow the same principle: they describe the funnel and transition mechanics. The canonical references — [Software Initiative Funnel](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/584515614) and [Work Transition Playbook](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2521038855) — live in Confluence and are fetched on demand.

## Related Plugins

Several skills in this plugin reference tools or skills provided by sibling plugins. Install these alongside `bitwarden-delivery-tools` for full functionality:

- **`bitwarden-atlassian-tools`** — provides the Jira/Confluence MCP tools used by `navigating-the-initiative-funnel`, and the `filing-jira-tickets` skill plus its opt-in Jira write tools that `filing-breakdown-tasks` hands off to.
- **`bitwarden-security-engineer`** — provides `Skill(bitwarden-security-context)`, referenced from `architecting-solutions`.
- **`bitwarden-code-review`** — provides `/bitwarden-code-review:code-review-local` and `Skill(performing-multi-agent-code-review)`, the code-review gate `creating-pull-request` runs before opening a PR. If it is absent, `creating-pull-request` prompts you to install it rather than skip the review.

`stacking-pull-requests` also invokes `Skill(addressing-code-review-comments)` from `bitwarden-code-review` when handling feedback on a lower layer, and treats it as optional.

It additionally depends on two pieces of tooling outside this marketplace, both from GitHub's [`gh-stack`](https://github.com/github/gh-stack) repository, which owns the `gh stack` command surface. Install both — with only the extension, every stack request takes the single-branch fallback.

1. The CLI extension:

   ```bash
   gh extension install github/gh-stack --pin v0.1.0
   ```

2. The `gh-stack` skill, from that repository's `skills/gh-stack/` directory. `gh extension install` fetches a platform binary only and never places the skill, so install it as a Claude skill separately.

`stacking-pull-requests` checks for both up front and falls back to a single-branch PR rather than improvising the commands. The documented flag sets were verified against `gh-stack` v0.1.0, the first release containing `gh stack merge`. It is pre-1.0 and still moving.

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
Split this into a stack of dependent PRs
```

```
Run preflight before I commit
```

```
What change type should I use for this PR?
```
