# Bitwarden Implementer Plugin

## Overview

Workflow-shaped agent that drives a single task or story through the **plan → implement → validate → self-review → ship** loop inside a Bitwarden team's codebase, ending at PR open. Input is a task from Jira, typically originating from a tech breakdown but standalone backlog tickets are also in scope. Generic AI coding assistance doesn't know our zero-knowledge constraints, multi-client reality, dual-ORM strategy, Angular/RxJs conventions, or the verification and self-review gates we run before a human ever sees the diff. This plugin composes the delivery-tools skills already in the marketplace at each phase and stops rather than absorbing work that belongs to the code reviewer or the breakdown author.

## Agent

| Agent                   | What It Does                                                                                                                                                                                                                                |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bitwarden-implementer` | Orients on a Jira task, drafts an implementation plan, edits code following repo patterns, runs preflight, self-reviews the diff via multi-agent code review, then commits and opens the PR. Surfaces scope drift rather than absorbing it. |

## The Loop

| Phase       | Composes                                                                                                                                                                                        |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Orient      | `bitwarden-atlassian-tools:researching-jira-issues` on the Jira task; if the epic has a tech breakdown, also read it and the sibling Jira tasks in the epic; read the target repo's `CLAUDE.md` |
| Plan        | `Plan` agent (Claude Code built-in)                                                                                                                                                             |
| Implement   | Read/Write/Edit/Bash/Grep + repo-specific implementation skills (loaded via progressive disclosure)                                                                                             |
| Preflight   | `bitwarden-delivery-tools:perform-preflight`                                                                                                                                                    |
| Self-review | `bitwarden-code-review:performing-multi-agent-code-review` on the local diff                                                                                                                    |
| Ship        | `bitwarden-delivery-tools:labeling-changes` → `committing-changes` → `creating-pull-request`                                                                                                    |

The loop ends at PR open. Addressing reviewer feedback on the opened PR is a separate follow-up — invoke `bitwarden-code-review:addressing-code-review-comments` as a bare skill call; it doesn't need the agent form.

## Cross-Plugin Integration

| Plugin                        | How It's Used                                                                                                                           |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `bitwarden-delivery-tools`    | `perform-preflight`, `labeling-changes`, `committing-changes`, `creating-pull-request` for the validate → ship path                     |
| `bitwarden-code-review`       | `performing-multi-agent-code-review` for self-review before shipping                                                                    |
| `bitwarden-atlassian-tools`   | `researching-jira-issues` on the Jira task                                                                                              |
| `bitwarden-security-engineer` | `reviewing-security-architecture`, `analyzing-code-security`, `reviewing-dependencies`, `detecting-secrets` when the diff triggers them |

Repo-specific implementation skills (`implementing-dapper-queries`, `implementing-ef-core`, `writing-database-queries`, and similar) live in the relevant Bitwarden repos and are picked up by Claude Code's progressive disclosure.

## Related Plugins

- **`bitwarden-code-review`** — the review counterpart. Use code-review when reviewing a _teammate's_ PR, or when addressing feedback on a PR (including one this agent opened). Use this plugin when driving the implementation loop that produces the PR.

## Installation

```bash
/plugin install bitwarden-implementer@bitwarden-marketplace
```

### Upgrading from `bitwarden-software-engineer`

This plugin was previously named `bitwarden-software-engineer`. The rename reflects a scope change from a persona-shaped agent (a "software engineer" doing anything a software engineer does) to a workflow-shaped agent (drive one Jira task through plan → implement → validate → self-review → ship, ending at PR open). To upgrade:

```bash
/plugin uninstall bitwarden-software-engineer@bitwarden-marketplace
/plugin install bitwarden-implementer@bitwarden-marketplace
```

Responsibilities that used to live here now live elsewhere: teammate PR review and post-PR feedback iteration moved to `bitwarden-code-review`; commit and PR conventions moved to `bitwarden-delivery-tools`. Install those plugins alongside this one for the composed loop.

## Usage

```
Use the bitwarden-implementer agent to take PM-12345 to PR.
```

## Evals

`evals/` contains the case set that certifies the agent as additive per the [AI Review Guidelines](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/3101458451/AI+Review+Guidelines). Run via `/skill-creator:skill-creator`. Every change to `AGENT.md` must hold or beat the recorded baseline.

## References

- [AI Review Guidelines](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/3101458451/AI+Review+Guidelines)
- [Engineering Career Ladder](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/1027899486/Engineering+Ladder)
- [Bitwarden Contributing Guidelines](https://contributing.bitwarden.com/contributing/)
