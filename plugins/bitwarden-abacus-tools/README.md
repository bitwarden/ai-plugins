# bitwarden-abacus-tools

## Overview

The Abacus profile for Bitwarden. Abacus runs an orchestrated, multi-agent development process.
Features include one worker per repository, gates, an independent reviewer, and verified evidence before anything
lands. This plugin tells Abacus which Bitwarden skills to use at each step of that process, so work Abacus does
follows the same conventions as work a Bitwarden engineer does by hand.

## What it does today

| Abacus slot   | Bitwarden skill                                                                                                   | Effect                                                                                                            |
| ------------- | ----------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `plan.source` | `bitwarden-atlassian-tools:researching-jira-issues`                                                               | "Plan PM-1234" works: the planner reads the issue, its links and Confluence pages into beads                      |
| `land.commit` | `bitwarden-abacus-tools:commit-message` (over `bitwarden-delivery-tools:committing-changes`)                      | Each bead's commit follows Bitwarden's format: `[PM-1234]`, or no bracket without a ticket                        |
| `land.pr`     | `bitwarden-abacus-tools:composing-abacus-pull-requests` (over `bitwarden-delivery-tools:applying-pr-conventions`) | Each bead's draft PR gets Bitwarden's conventional title, PR template body, `t:` type label and `ai-review` label |

**Planning from Jira.** The planner reads the issue through the Atlassian tools, drafts beads with the issue key as
their source, and turns the issue's acceptance criteria into checkable ones. It only reads: Abacus refuses Jira
writes (creating issues, comments, links) in its sessions, even with a write token configured. The Atlassian tools'
MCP server needs Node and the `ATLASSIAN_*` tokens from that plugin's README; without them, the planner says so and
asks for the text.

**Work without a ticket.** When a bead's source isn't a Jira ticket, the commit drops the bracket rather than inventing a
key or writing a placeholder, the same rule `applying-pr-conventions` uses for pull request titles, so a bead's commit
and its PR title agree. The rule is settled in `skills/commit-message`, so Abacus never stops to ask.

**The AI review label.** `applying-pr-conventions` asks a person whether to add an AI review label, and nobody attends an Abacus stage to answer. `skills/composing-abacus-pull-requests` settles it as `ai-review`, which belongs only on a pull request created as a draft, and Abacus opens every pull request as one, so every draft PR Abacus opens in a Bitwarden repository is queued for AI review, and the bead's recorded answers say the profile chose it. The body shape Abacus asks for (gherkin acceptance criteria with their test names, review guidance, the AI-assisted review section) wins over the PR template wherever the two differ.

Abacus still opens the pull request itself (through `abacus-finalize`), so stacking, cleanup on failure and the
evidence checks stay in place. The skill only supplies the content. Each result is recorded on the bead together
with the plugin versions that produced it.

The other slots (`plan.analyze`, `implement.guide`, `review`, `retro.analyze`) are listed but empty
until Abacus uses them.

## Substantial code review

`substantial-review` is the deep review Abacus runs on high-risk changes, and on changes with no recorded risk assessment, before it lands a pull request. It is a workflow rather than a skill because a workflow stage can't start subagents, so the multi-agent pipeline from `bitwarden-code-review:performing-multi-agent-code-review` is laid out as workflow stages instead: an architecture reviewer, quality, bug and security reviewers in parallel (plus Claude configuration and skill reviewers when the change touches those files), validation of every finding, and a severity audit. The skill's prompt rules are carried over word for word, so both reviews judge a change the same way.

Abacus calls it with `workflow("bitwarden-abacus-tools:substantial-review", args)`:

| Argument | Required | Meaning                                                                                                                                         |
| -------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `repo`   | yes      | Absolute path to the worktree holding the change                                                                                                |
| `base`   | yes      | Full SHA of the commit the change branched from. The change is the working tree against it, so a moving branch tip would pull in unrelated work |
| `bead`   | no       | Bead id, shown in progress labels                                                                                                               |

It returns one object for Abacus's assess stage to read:

- `status` is `complete`, `incomplete` when a reviewer or stage failed or every changed path was filtered out before review (Abacus treats that as no review), or `empty` when the change has no tracked or untracked paths at all.
- `reviewed` holds `repo`, `base`, the `head` SHA and whether uncommitted work was included (`dirty`), so the review record can be tied to the exact change.
- `findings` lists each surviving finding with `severity` (`CRITICAL`, `IMPORTANT` or `DEBT`, the `classifying-review-findings` names for the pipeline's Blocker, Important and Refactor tiers), `file`, `line`, `title`, `detail`, a `security` flag, the `reviewer` that raised it, its `confidence`, and whether validation and the audit ran on it.
- `dismissed` lists what validation or the audit dropped, and why.
- `summary` and `not_covered` say what the review concluded and what it couldn't look at.

The security reviewer runs as `bitwarden-security-engineer:bitwarden-security-engineer`, so that plugin must be enabled for the worker; without it every review comes back `incomplete`. `claude-config-validator` and `plugin-dev` add the configuration and skill reviewers when present, and a skipped skill review is named in `not_covered`.

## Coordinating roles

The concierge and orchestrator launch with none of the Bitwarden plugins; the planner keeps
`bitwarden-atlassian-tools` and `bitwarden-product-analyst`. Workers keep every plugin you have installed.

## Requirements

- Abacus 0.15 or later to plan from Jira (`plan.source` arrived in 0.15); `land.commit` and `land.pr` work from 0.13.
- The plugins it names, installed from this marketplace. If they aren't installed on a machine, Abacus can't use
  them; `abacus doctor` reports what's missing.

## Installation

```bash
/plugin install bitwarden-abacus-tools@bitwarden-marketplace
```

## Usage

There's nothing to invoke. Abacus finds the profile among your installed plugins. To check that it's picked up:

```bash
abacus doctor
```

It shows the `bitwarden` profile, each slot resolving to its skill, and any plugin the profile names that isn't
installed. Then tell the concierge to plan a Jira issue, approve the plan, and build it, in a repository with
draft-PR landing:

```text
plan PM-1234
build PM-1234
```

Each bead's commit then follows Bitwarden's commit format, and its draft PR carries Bitwarden's title, template body,
`t:` type label and `ai-review` label. A repository can leave the
profile out with `"profile": "none"` in its `.abacus/config.json`.
