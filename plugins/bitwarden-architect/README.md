# Bitwarden Software Architect Plugin

## Overview

Software architecture planning for Bitwarden repositories. Generic AI assistance doesn't know our zero-knowledge constraints, multi-client reality, dual-ORM strategy, or V+/-2 version matrix. This plugin keeps architecture decisions grounded in how we actually build software at Bitwarden.

## Agent

| Agent                 | What It Does                                                                                                 |
| --------------------- | ------------------------------------------------------------------------------------------------------------ |
| `bitwarden-architect` | Explores codebases and produces phased implementation plans grounded in Bitwarden's architectural principles |

## Skills

| Skill                    | What It Does                                                                                                                         |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| `architecting-solutions` | Principal engineer perspective on architecture decisions. Provides the architectural judgment framework applied across all planning. |

## Cross-Plugin Integration

| Plugin                        | How It's Used                                                            |
| ----------------------------- | ------------------------------------------------------------------------ |
| `bitwarden-security-engineer` | Security context (P01-P06), architecture pattern review, threat modeling |
| `bitwarden-product-analyst`   | Consumes requirements documents as upstream input                        |
| `bitwarden-software-engineer` | Implementation conventions for server, client, and database decisions    |
| `bitwarden-atlassian-tools`   | Jira issue research and Confluence page access                           |

All cross-plugin skills are required because we rely upon each of them for a rich, complete workflow.

## Installation

```bash
/plugin install bitwarden-architect@bitwarden-marketplace
```

## Usage

The architect agent activates when you need to plan a feature, review an architecture decision, assess blast radius, or produce an implementation plan:

```
Plan the implementation for PM-12345
```

```
Review the architecture of [feature area] and suggest improvements
```

```
Assess the blast radius of adding [capability] to [service]
```

## References

- [Bitwarden Security Definitions](https://contributing.bitwarden.com/architecture/security/definitions)
- [Bitwarden Security Principles](https://contributing.bitwarden.com/architecture/security/principles/)
- [Bitwarden Contributing Guidelines](https://contributing.bitwarden.com/contributing/)
