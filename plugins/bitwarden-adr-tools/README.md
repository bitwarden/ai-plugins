# Bitwarden ADR Tools Plugin

Tools that act on Bitwarden's Architecture Decision Records.

## Overview

This plugin holds skills whose subject is Bitwarden's [Architecture Decision Records](https://contributing.bitwarden.com/architecture/adr/). It depends on no other plugin, so any plugin can compose it without creating a dependency cycle.

Skills can be invoked individually. See the table below for what ships today.

## Skills

| Skill             | What It Does                                                                                                                                                                                                                                                                        |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `consulting-adrs` | Checks a design, change, plan, or threat model against Bitwarden's [Architecture Decision Records](https://contributing.bitwarden.com/architecture/adr/), or locates/summarizes the catalog. Returns structured findings (conflict, gap, stale-reference, aligned) with cited ADRs. |

## Installation

```bash
/plugin install bitwarden-adr-tools@bitwarden-marketplace
```

## Usage

Skills activate based on natural-language triggers:

```
Does this new sync endpoint conflict with any of our ADRs?
```
