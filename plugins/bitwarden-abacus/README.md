# bitwarden-abacus

## Overview

The Abacus profile for Bitwarden. Abacus runs an orchestrated, multi-agent development process.
Features include one worker per repository, gates, an independent reviewer, and verified evidence before anything
lands. This plugin tells Abacus which Bitwarden skills to use at each step of that process, so work Abacus does
follows the same conventions as work a Bitwarden engineer does by hand.

## What it does today

| Abacus slot | Bitwarden skill                                    | Effect                                                                                |
| ----------- | -------------------------------------------------- | ------------------------------------------------------------------------------------- |
| `land.pr`   | `bitwarden-delivery-tools:applying-pr-conventions` | Each bead's draft PR gets Bitwarden's conventional title, PR template body and labels |

Abacus still opens the pull request itself (through `abacus-finalize`), so stacking, cleanup on failure and the
evidence checks stay in place. The skill only supplies the content. Each result is recorded on the bead together
with the plugin versions that produced it.

The other slots (`plan.source`, `plan.analyze`, `implement.guide`, `review`, `retro.analyze`) are listed but empty
until Abacus uses them.

## Coordinating roles

The concierge and orchestrator launch with none of the Bitwarden plugins; the planner keeps
`bitwarden-atlassian-tools` and `bitwarden-product-analyst`. Workers keep every plugin you have installed.

## Requirements

- Abacus 0.11 or later.
- The plugins it names, installed from this marketplace. If they aren't installed on a machine, Abacus can't use
  them; `abacus doctor` reports what's missing.

## Installation

```bash
/plugin install bitwarden-abacus@bitwarden-marketplace
```

## Usage

There's nothing to invoke. Abacus finds the profile among your installed plugins. To check that it's picked up:

```bash
abacus doctor
```

It shows the `bitwarden` profile, the `land.pr` slot resolving to `applying-pr-conventions`, and any plugin the
profile names that isn't installed. Then build as usual in a repository with draft-PR landing, for example by telling
the concierge:

```text
build PM-1234
```

Each bead's draft PR then carries Bitwarden's title, template body and labels. A repository can leave the profile
out with `"profile": "none"` in its `.abacus/config.json`.
