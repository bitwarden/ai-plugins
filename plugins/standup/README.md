# standup

Generate a terse, honest, RAG-status standup report from your real GitHub and Jira/Confluence activity.

## Overview

standup gathers your recent activity — GitHub pull requests, Jira tickets and comments, and Confluence edits — over a configurable time window and synthesizes a short first-person status update with red/amber/green signal. All access is read-only. Identity, workspace, and output preferences are supplied by you (never hardcoded) and are captured by the `/standup:init` command.

Run `/standup:init` once to capture your preferences, then `/standup:generate` whenever you need a report.

## Installation

```bash
/plugin install standup@bitwarden-marketplace
```

Restart Claude Code after installation.

## Commands

### `/standup:init`

Guided Q&A that captures your standup preferences and writes them to a dedicated preferences file. It covers:

- **Identity & workspace** — Atlassian display name and email, GitHub username, Jira base URL, timezone.
- **Output format** — where the report is delivered (org-roam memory, a local markdown file, or straight to chat), the section labels, and markdown-link rendering.
- **Output style** — the RAG GREEN/YELLOW/RED heuristic, the routine-tail collapse rule, name discipline, and any other output rules you want applied.

**Where it writes.** Preferences are saved to a dedicated, load-on-demand file at `~/.claude/standup/preferences.md`. This is **not** `~/.claude/CLAUDE.md` — it does **not** auto-load into other projects or conversations. The standup skill reads it explicitly at report time, so it never pollutes the context of unrelated work.

**Safety flow.** The command never writes without your explicit confirmation. When a preferences file already exists it shows a unified diff of the proposed changes, makes a timestamped backup (`preferences.md.bak-<ISO>`) before overwriting, and only writes after you choose **Apply**. Any `[YOUR-PREFERENCE]` placeholders you leave untouched are preserved verbatim so you can fill them in later.

### `/standup:generate`

Produce a standup report from your real activity. Pass an optional target user or time window as an argument, or run it blank to use your preferences file.

The command is a thin dispatcher: it hands off to the `standup-report-generator` agent, which reads `~/.claude/standup/preferences.md`, preflights credentials, then runs the pipeline — `generate-standup-report` collects your GitHub and Jira/Confluence activity as JSON, `synthesize-standup-report` turns it into RAG-status markdown, and `deliver-standup-report` routes the output to your configured destination. All API access is read-only.

## Example Output

```
:large_green_circle: Steady progress on three active tracks; no blockers.

`Last week:`
- Resolved a request-timeout regression in the vault sync flow by capping the retry budget in the client layer — [PM-12345](https://example.atlassian.net/browse/PM-12345) (`Done`)
- Reviewed the new device-trust onboarding PR; left detailed feedback on the key-derivation boundary — [bitwarden/clients#9876](https://github.com/bitwarden/clients/pull/9876)
- Organized the Q3 auth initiative ticket tree: created parent/child structure across four epics and set goals, priority, and owners ([BW-456](https://example.atlassian.net/browse/BW-456), [BW-457](https://example.atlassian.net/browse/BW-457))

`This week:`
- Continue the SSO session-binding refactor [PM-23456] (`In Development`)
- Begin scoping the emergency-access flow redesign [PM-34567] (`In Development`)

`Blockers:`
- None
```

Report window, section labels, destination, and markdown-link rendering are all configurable via `/standup:init`.

## Usage

```
/standup:generate
/standup:generate last two weeks
```

Run `/standup:init` first so the generator has your identity, workspace, and output preferences on hand.
