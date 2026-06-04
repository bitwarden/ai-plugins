# Bitwarden Designer Plugin

## Overview

Product designer agent for Bitwarden. Holds the design team's Code of Conduct and the 30/60/90 critique framework, and dispatches into the `bitwarden-design-tools` toolkit for everything else — content style, Figma reads, brand application, handoff prep, Design System governance, and the Product and Design Jira workflow.

The split is intentional: this plugin is the persona — the designer's judgment in the room. `bitwarden-design-tools` is the toolkit — the reusable workflow and reference skills the persona composes (and that anyone can use standalone). Treats content as first-class design and brand as a first-class lens. Reads Figma via the Dev Mode MCP server when one is available.

## Agent

| Agent                | What It Does                                                                                                                                                                                                                                                                                                                                        |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bitwarden-designer` | Bitwarden product designer. Critiques designs against the Code of Conduct and 30/60/90 framework, facilitates design critique sessions, and dispatches into the `bitwarden-design-tools` toolkit for copy review, Figma reads, brand application, design-to-engineering handoff, Design System evolution, and the Product and Design Jira workflow. |

## Skills

| Skill                          | What It Does                                                                                                                                                                                                                               |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `design-review`                | The design team's Code of Conduct combined with the 30/60/90 critique framework. Stage-appropriate critique, product-not-designer focus, content evaluated alongside visual design at 60% and 90%. Triggered for design critique requests. |
| `facilitating-design-critique` | Run or participate in a Bitwarden design critique — both the weekly team critique and one-off Product Design Reviews. Roles (presenter, facilitator, participants), session arc, etiquette, and the common participation traps to catch.   |

Six more skills — content style, Figma reads, brand application, handoff prep, Design System evolution, and the Product and Design Jira workflow — live in [`bitwarden-design-tools`](../bitwarden-design-tools/) and are required cross-plugin dependencies.

## Cross-Plugin Integration

| Plugin                      | How It's Used                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bitwarden-design-tools`    | Required. The agent dispatches into `content-style-guide`, `using-figma`, `applying-bitwarden-branding`, `preparing-design-handoff`, `evolving-design-system-components`, and `navigating-design-jira-process` by name. The toolkit is load-bearing — the persona is thin without it.                                                                           |
| `bitwarden-atlassian-tools` | Required. Skills here and in `bitwarden-design-tools` reference canonical Confluence pages (Weekly Design Critique & Etiquette, Product Design Review Guidelines, Creating new design patterns, Modifying an existing component, Product and Design Jira Process) and assume `get_confluence_page` is available to fetch them directly when prepping real work. |
| `bitwarden-tech-lead`       | Counterpart on the team-side engineering surface. When design questions touch team-scope architecture (component build plans, recipe ownership, technical breakdown), surface the touchpoint and hand off to the tech lead rather than absorbing it.                                                                                                            |
| `bitwarden-shepherd`        | Counterpart on the cross-team initiative surface. When design questions touch initiative shaping across teams (handoff coordination for a multi-team initiative, Design System evolution that crosses team boundaries), surface the touchpoint.                                                                                                                 |

All cross-plugin skills are required.

## External Dependency: Figma Dev Mode MCP Server

The `using-figma` skill (in `bitwarden-design-tools`) assumes the user has installed and authenticated Figma's Dev Mode MCP server in their client. This server is **Figma's own product**, not bundled. It comes in two flavors (desktop, which requires a Dev or Full Figma seat on a paid plan, and remote). Setup details live in `bitwarden-design-tools/skills/using-figma/references/setup.md`.

If the Figma MCP tools aren't available in the session, the `using-figma` skill stops and asks the user to install before continuing. Other skills continue to function — they only compose `using-figma` when a Figma URL is in play.

## Installation

```bash
/plugin install bitwarden-designer@bitwarden-marketplace
```

Install the required companions alongside it:

```bash
/plugin install bitwarden-design-tools@bitwarden-marketplace
/plugin install bitwarden-atlassian-tools@bitwarden-marketplace
```

## Usage

The designer agent activates when reviewing or critiquing a design, evaluating GUI copy, reading or inspecting a Figma file, facilitating a design review, preparing a design handoff, proposing or modifying a Design System component, checking Bitwarden brand application, or navigating the design side of an engineering epic:

```
Critique the 60% draft of the device-trust onboarding screen. Figma URL: ...
```

```
Take a pass on these strings — buttons, the empty state, and the toast on save failure.
```

```
Read this Figma frame and tell me which spacing values aren't bound to the library.
```

```
I'm facilitating critique this week and presenting two screens of my own. How do I set the room up and frame what I want feedback on?
```

```
I'm wrapping up design on the new vault filter project — Figma file is here, engineering epic is PM-XXXX. Is this ready to hand off?
```

```
Is this banner on-brand? It uses #175DDC for the headline and a green call-out for the CTA.
```

```
We keep building variations of this segmented selector — should it become a core component or stay a recipe?
```

```
PM created the epic, designs are at 60%. Walk me through the Jira choreography so engineering sees the right state.
```

## References

- [Weekly Design Critique & Etiquette (Quick Guide)](https://bitwarden.atlassian.net/wiki/spaces/PROD/pages/2329542659)
- [Product Design Review Guidelines](https://bitwarden.atlassian.net/wiki/spaces/PROD/pages/469925913)
