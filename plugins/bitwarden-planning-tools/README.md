# Bitwarden Planning Tools Plugin

Planning and preparation tools for Bitwarden — the pre-implementation half of the lifecycle.

## Overview

This plugin is the home for **pre-implementation planning and preparation** work: understanding a change, checking it against recorded architecture decisions, and shaping it before code is written. It is the counterpart to `bitwarden-delivery-tools`, which covers the **post-implementation** mechanics (commits, pull requests, preflight checks, change labeling, and fleet delivery).

Skills can be invoked individually, and the plugin is designed to grow. It is proposed as the future home for other planning tools — tech breakdowns, initiative-funnel navigation, and architecture solutioning — as those consolidate here over time. See the table below for what ships today.

## Skills

| Skill             | What It Does                                                                                                                                                                                                                                                                              |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `consulting-adrs` | Checks a design, change, plan, or threat model against Bitwarden's [Architecture Decision Records](https://contributing.bitwarden.com/architecture/adr/), or locates/summarizes the catalog. Returns structured findings (conflict, gap, aligned) with cited ADRs — not vague commentary. |

## Cross-Plugin Integration

| Plugin                        | How It's Used                                                                                                                                                      |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `bitwarden-security-engineer` | Consumer — its `bitwarden-security-context`, `reviewing-security-architecture`, and `threat-modeling` skills invoke `consulting-adrs` for the ADR-alignment check. |
| `bitwarden-delivery-tools`    | Counterpart — the post-implementation lifecycle (commits, PRs, preflight, delivery). Planning happens here; delivery happens there.                                |

## Installation

```bash
/plugin install bitwarden-planning-tools@bitwarden-marketplace
```

## Usage

Skills activate based on natural-language triggers:

```
Does this new sync endpoint conflict with any of our ADRs?
```
