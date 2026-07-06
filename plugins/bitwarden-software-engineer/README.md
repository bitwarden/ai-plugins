# Bitwarden Software Engineer Plugin

## Overview

Software engineer agent for a Bitwarden product team. Generic AI coding assistance doesn't know our zero-knowledge constraints, multi-client reality, dual-ORM strategy, Angular/RxJs conventions, or the verification commands we actually run before declaring work done — let alone the canonical Bitwarden "Software Engineer" role on the [Engineering Career Ladder](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/1027899486/Engineering+Ladder) that frames what the role is evaluated on. This plugin grounds the agent in that role: implementing stories, tasks, and bugs in the team's domain with code quality, performance, and security in mind, communicating clearly, and following our Git conventions.

## Agent

| Agent                         | What It Does                                                                                                                                                                                                                           |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bitwarden-software-engineer` | Implements stories, tasks, and bugs in the team's domain; runs the appropriate build/lint/test verifications for the repo; participates in refinement and PR review; surfaces ambiguity rather than guessing; prepares the deliverable |

## Cross-Plugin Integration

| Plugin                        | How It's Used                                                                                                                                                                                                                                                                                                      |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `bitwarden-delivery-tools`    | `committing-changes`, `creating-pull-request`, `perform-preflight`, `labeling-changes` for the day-to-day PR loop                                                                                                                                                                                                  |
| `bitwarden-atlassian-tools`   | `researching-jira-issues` when picking up a story                                                                                                                                                                                                                                                                  |
| `bitwarden-security-engineer` | `reviewing-security-architecture`, `analyzing-code-security`, `reviewing-dependencies`, `detecting-secrets` when relevant to the change                                                                                                                                                                            |
| `launchdarkly` (optional)     | `launchdarkly-flag-discovery` / `launchdarkly-flag-command`, `launchdarkly-flag-create`, `launchdarkly-flag-targeting`, `launchdarkly-flag-cleanup` for the feature-flag lifecycle — requires the LaunchDarkly plugin and its hosted MCP server ([install](https://mcp.launchdarkly.com/mcp/launchdarkly/install)) |

**Feature flags** follow the [Bitwarden feature flags guidance](https://contributing.bitwarden.com/contributing/feature-flags) (flags in general always used for new work, one flag per independent feature, default off, kebab-case; release flags are temporary while operational kill-switches may be permanent). Server-side .NET evaluates them through our core [`Bitwarden.Server.Sdk.Features`](https://github.com/bitwarden/dotnet-extensions/tree/main/extensions/Bitwarden.Server.Sdk.Features/src) package (`IFeatureService`, `FeatureFlagKeys`, `[RequireFeature]`), which wraps LaunchDarkly — the agent uses it rather than hand-rolling a flag abstraction or calling the LaunchDarkly SDK directly. Clients (web/browser/desktop/mobile) are simple consumers that read flag state from the server's `/config` endpoint via `ConfigService` / `IConfigService`, never from LaunchDarkly directly.

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
