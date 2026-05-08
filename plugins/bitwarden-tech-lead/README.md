# Bitwarden Tech Lead Plugin

## Overview

Tech lead agent for a Bitwarden product team. Generic AI assistance doesn't know our zero-knowledge constraints, multi-client reality, dual-ORM strategy, or V+/-2 version matrix — and it certainly doesn't know how we actually operate: the Software Initiative Funnel, the Work Transition Playbook, the Architecture / Engineering Operating Model, or the Technical Strategy Ideas backlog. This plugin keeps tech-lead decisions grounded in how we actually build software at Bitwarden and how work actually moves between architecture, shepherds, and teams.

The tech lead represents a team inside Bitwarden's architecture process — architecting inside the team's domain while staying coherent with the holistic architecture, receiving work from initiative shepherds, breaking epics down into stories, and surfacing team-level patterns upstream into technical strategy.

## Agent

| Agent                 | What It Does                                                                                                                                                                                                                                    |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bitwarden-tech-lead` | Plans and architects inside a team's scope, works alongside initiative shepherds (or shepherds smaller-scope initiatives directly), runs work transitions in either direction, breaks down initiative epics, and surfaces ideas to architecture |

## Skills

| Skill                                | What It Does                                                                                                                                          |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `architecting-solutions`             | Architectural judgment framework: security mindset, blast radius, Bitwarden constraints, working with the architecture group and initiative shepherds |
| `contributing-to-technical-strategy` | Full vertical from Technical Strategy Ideas through BW Initiatives to team epics and stories — recognizing, framing, tracing, breaking down           |

## Cross-Plugin Integration

| Plugin                        | How It's Used                                                                                                                                               |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bitwarden-delivery-tools`    | Delivery lifecycle skills — `navigating-the-initiative-funnel` for funnel phase mechanics, `running-work-transitions` for ownership transitions either side |
| `bitwarden-security-engineer` | Security context (P01-P06), architecture pattern review, threat modeling                                                                                    |
| `bitwarden-product-analyst`   | Consumes requirements documents as upstream input                                                                                                           |
| `bitwarden-software-engineer` | Implementation conventions for server, client, and database decisions                                                                                       |
| `bitwarden-atlassian-tools`   | Jira issue research and Confluence page access for the funnel, operating model, and TSI documents this plugin's skills reference                            |

All cross-plugin skills are required because we rely upon each of them for a rich, complete workflow.

## Installation

```bash
/plugin install bitwarden-tech-lead@bitwarden-marketplace
```

### Upgrading from `bitwarden-architect`

This plugin was previously named `bitwarden-architect`. The rename reflects Bitwarden's actual role nomenclature — teams are led by tech leads, not team-level architects; the architecture group operates upstream. To upgrade:

```bash
/plugin uninstall bitwarden-architect@bitwarden-marketplace
/plugin install bitwarden-tech-lead@bitwarden-marketplace
```

The `architecting-solutions` skill is retained (refactored around the holistic-architecture framing). A new `contributing-to-technical-strategy` skill is added. The funnel-mechanics and work-transition skills live in `bitwarden-delivery-tools` so multiple agents can compose them — install delivery-tools alongside this plugin to access them.

## Usage

The tech lead agent activates when planning work inside a team's scope, receiving an initiative epic, preparing to break it down, running a work transition (in either direction), shepherding a smaller-scope initiative, or evaluating whether a team-level pattern of pain belongs upstream in the funnel:

```
Plan the implementation for PM-12345 within our team
```

```
Break down the epic BW-123 into stories for our team
```

```
We're receiving a framework transition from the Platform team. Help me prepare.
```

```
Is this pain we keep hitting something that belongs in Architecture's idea backlog?
```

## References

- [Software Initiative Funnel](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/584515614)
- [Work Transition Playbook](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2521038855)
- [Architecture / Engineering Operating Model](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/1286963201)
- [Technical Strategy Ideas](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2344517656)
- [Idea-Based Initiatives](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2785181779)
- [Bitwarden Security Definitions](https://contributing.bitwarden.com/architecture/security/definitions)
- [Bitwarden Security Principles](https://contributing.bitwarden.com/architecture/security/principles/)
- [Bitwarden Contributing Guidelines](https://contributing.bitwarden.com/contributing/)
