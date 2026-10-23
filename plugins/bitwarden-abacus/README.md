# bitwarden-abacus

## Overview

The Abacus profile for Bitwarden. Abacus runs an orchestrated, multi-agent development process.
Features include one worker per repository, gates, an independent reviewer, and verified evidence before anything
lands. This plugin tells Abacus which Bitwarden skills to use at each step of that process, so work Abacus does
follows the same conventions as work a Bitwarden engineer does by hand.

## What it does today

| Abacus slot   | Bitwarden skill                                                                        | Effect                                                                                         |
| ------------- | -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `land.commit` | `bitwarden-abacus:commit-message` (over `bitwarden-delivery-tools:committing-changes`) | Each bead's commit follows Bitwarden's format: `[PM-1234]`, or no bracket without a ticket     |
| `land.pr`     | `bitwarden-delivery-tools:applying-pr-conventions`                                     | Each bead's draft PR gets Bitwarden's conventional title, PR template body and `t:` type label |

**Work without a ticket.** When a bead's source isn't a Jira ticket, the commit drops the bracket rather than inventing a
key or writing a placeholder, the same rule `applying-pr-conventions` uses for pull request titles, so a bead's commit
and its PR title agree. The rule is settled in `skills/commit-message`, so Abacus never stops to ask.

Abacus still opens the pull request itself (through `abacus-finalize`), so stacking, cleanup on failure and the
evidence checks stay in place. The skill only supplies the content. Each result is recorded on the bead together
with the plugin versions that produced it.

The other slots (`plan.source`, `plan.analyze`, `implement.guide`, `review`, `retro.analyze`) are listed but empty
until Abacus uses them.

## Coordinating roles

The concierge and orchestrator launch with none of the Bitwarden plugins; the planner keeps
`bitwarden-atlassian-tools` and `bitwarden-product-analyst`. Workers keep every plugin you have installed.

## Requirements

- Abacus 0.13 or later (`land.commit` arrived in 0.13).
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

It shows the `bitwarden` profile, the `land.commit` and `land.pr` slots resolving to `commit-message` and
`applying-pr-conventions`, and any plugin the profile names that isn't installed. Then build as usual in a repository with draft-PR landing, for example by telling
the concierge:

```text
build PM-1234
```

Each bead's commit then follows Bitwarden's commit format, and its draft PR carries Bitwarden's title, template body and
`t:` type label. A repository can leave the
profile out with `"profile": "none"` in its `.abacus/config.json`.
