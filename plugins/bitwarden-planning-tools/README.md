# Bitwarden Planning Tools Plugin

Planning and preparation tools for Bitwarden — the pre-implementation half of the lifecycle.

## Overview

This plugin is the home for **pre-implementation planning and preparation** work: understanding a change, checking it against recorded architecture decisions, and shaping it before code is written.

Skills can be invoked individually. See the table below for what ships today.

## Skills

| Skill             | What It Does                                                                                                                                                                                                                                                                        |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `consulting-adrs` | Checks a design, change, plan, or threat model against Bitwarden's [Architecture Decision Records](https://contributing.bitwarden.com/architecture/adr/), or locates/summarizes the catalog. Returns structured findings (conflict, gap, stale-reference, aligned) with cited ADRs. |

## Installation

```bash
/plugin install bitwarden-planning-tools@bitwarden-marketplace
```

## Usage

Skills activate based on natural-language triggers:

```
Does this new sync endpoint conflict with any of our ADRs?
```
