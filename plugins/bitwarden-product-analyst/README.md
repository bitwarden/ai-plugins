# Bitwarden Product Analyst Plugin

Claude Code skills for product analysis at Bitwarden. Generic AI assistance doesn't know our requirements format, security principles, Confluence initiative structure, or how we think about plan tiers and client surfaces. These skills keep Claude focused on how we specify software here.

## Agent

| Agent             | What It Does                                                                                                                                                                                                                                                                                                                       |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `product-analyst` | Reads Confluence initiative pages, Jira tickets, and other sources to produce structured requirements documents following Bitwarden's template. Applies security principles (P01–P06), distinguishes all four web surfaces and all plan tiers, attributes TBDs by owner (PM/Design/Engineering), and surfaces post-MVP candidates. |

## Skills

| Skill                      | What It Does                                                                                                                                                                                                 |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `requirements-elicitation` | Extracts functional, non-functional, and security requirements from specifications. Flags ambiguities, identifies constraints, and creates testable acceptance criteria using Bitwarden security vocabulary. |
| `work-breakdown`           | Decomposes features into implementable tasks organized by phase. Identifies cross-repo dependencies (`bitwarden/server` vs. `bitwarden/clients`), task ordering, and team assignments.                       |

## Installation

Available through Bitwarden's internal Claude Code marketplace:

```bash
# Add the Bitwarden marketplace (if not already added)
/plugin marketplace add https://github.com/bitwarden/ai-plugins

# Install the product analyst plugin
/plugin install bitwarden-product-analyst@bitwarden-marketplace

# Restart Claude Code
```

## Usage

```
Analyze requirements from https://bitwarden.atlassian.net/wiki/spaces/PROD/pages/123456/Feature-Name
```

```
Create a spec document from PROJ-1234
```

```
Write a spec for adding passkey support to the browser extension
```

## References

### requirements-elicitation / product-analyst

- [Bitwarden Security Definitions](https://contributing.bitwarden.com/architecture/security/definitions) — Vault Data, Protected Data, Secure Channel, Trusted Channel vocabulary
- [Bitwarden Security Principles](https://contributing.bitwarden.com/architecture/security/principles/) — P01–P06 foundation principles
- [Product Initiative Template](https://bitwarden.atlassian.net/wiki/spaces/PROD/pages/171507714/Product+initiative+template) — Canonical PM template; maps to `references/requirements-template.md`
- [Requirements Template](references/requirements-template.md) — Full requirements document structure
