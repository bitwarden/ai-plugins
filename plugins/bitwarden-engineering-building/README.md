# Bitwarden Software Engineer Plugin

## Overview

Software engineer agent for a Bitwarden engineering team. Generic AI coding assistance doesn't know our zero-knowledge constraints, multi-client reality, dual-ORM strategy, Angular/RxJs conventions, or the verification commands we actually run before declaring work done — let alone the canonical Bitwarden "Software Engineer" role on the [Engineering Career Ladder](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/1027899486/Engineering+Ladder) that frames what the role is evaluated on. This plugin grounds the agent in that role: implementing stories, tasks, and bugs in the team's domain with code quality, performance, and security in mind, communicating clearly, and following our Git conventions.

## Agent

| Agent                         | What It Does                                                                                                                                                                                                                           |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bitwarden-software-engineer` | Implements stories, tasks, and bugs in the team's domain; runs the appropriate build/lint/test verifications for the repo; participates in refinement and PR review; surfaces ambiguity rather than guessing; prepares the deliverable |

## Cross-Plugin Integration

| Plugin                        | How It's Used                                                                                                                           |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `bitwarden-delivery-tools`    | `committing-changes`, `creating-pull-request`, `perform-preflight`, `labeling-changes` for the day-to-day PR loop                       |
| `bitwarden-atlassian-tools`   | `researching-jira-issues` when picking up a story                                                                                       |
| `bitwarden-security-engineer` | `reviewing-security-architecture`, `analyzing-code-security`, `reviewing-dependencies`, `detecting-secrets` when relevant to the change |

Per-repo skills (`implementing-dapper-queries`, `implementing-ef-core`, `writing-database-queries`, and similar) live in the relevant Bitwarden repos and are picked up by Claude Code's progressive disclosure.

## Related Plugins

- **`bitwarden-tech-lead`** — the next rung on the career ladder. Use that plugin when planning or architecting work inside a team's domain rather than implementing it.

## Installation

```bash
/plugin install bitwarden-software-engineer@bitwarden-marketplace
```

## Usage

```
Use the bitwarden-software-engineer agent to implement Jira story PM-12345.
```

```
Review PR #12345 with the bitwarden-software-engineer agent.
```

## References

- [Software Engineer role definition](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/1028423725/Software+Engineer)
- [Engineering Career Ladder](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/1027899486/Engineering+Ladder)
- [Bitwarden Contributing Guidelines](https://contributing.bitwarden.com/contributing/)
