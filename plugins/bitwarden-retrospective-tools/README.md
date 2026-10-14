# Bitwarden Retrospective Tools Plugin

Tools for looking back on your own engineering work.

## Overview

This plugin holds skills whose subject is the work an engineer has already done, read from their Claude Code session logs and their GitHub activity. It depends on no other plugin.

Skills can be invoked individually. See the table below for what ships today.

## Skills

| Skill         | What It Does                                                                                                                                                                                                                  |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `daily-recap` | Builds an interactive HTML recap of one workday from your Claude Code sessions and GitHub events, with a standup card, themed work streams, and a filterable GitHub timeline. See [its README](skills/daily-recap/README.md). |

## Installation

```bash
/plugin install bitwarden-retrospective-tools@bitwarden-marketplace
```

## Usage

Skills activate based on natural-language triggers:

```
What did I work on yesterday?
Put together a recap I can use for standup
```

## Requirements

- `gh`, authenticated with `gh auth login`
- `jq`
- `bash` with GNU or BSD `date` (Linux and macOS)

## Privacy & Security

Everything runs locally. Session logs are only read, GitHub data comes from your own events feed through `gh`, and recap pages are written to your machine. A recap can include private-repository activity, so review it before sharing it outside the team.
