# Daily Recap

Generate polished, interactive HTML recaps of a person's daily work. Pulls activity from the relevant systems, shapes it into a standup-ready, colleague-shareable artifact, and applies Bitwarden brand styling.

## Skills

| Skill               | Purpose                                                                                                                                                                                                                                                                                                  |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `engineering-recap` | Generates a recap of the user's engineering work — Claude Code session activity combined with GitHub events (PRs, reviews, comments, pushes, branch ops, repo creates, sweeps). Produces an interactive HTML page with a copy-ready standup card, project workstreams, GitHub timeline, and theme block. |

## Usage

The `engineering-recap` skill triggers on retrospective queries about the user's own coding work — phrases like:

- _"what did I work on yesterday?"_
- _"recap please"_
- _"standup prep"_
- _"summarize my work this morning"_
- _"create me a daily recap for april 28 to show colleagues"_

The output is saved to `~/Documents/daily-recap/recap-{YYYY-MM-DD}.html` and opened in the default browser.

## Day boundary

The skill treats **7am Eastern** as the day boundary, not midnight UTC. Late-night work folds into the prior calendar day. A "Today / Fresh" banner appears only when there is post-7am-Eastern activity on the current day.

## Dependencies

- `claude-retrospective` — session extraction is delegated to `claude-retrospective:extracting-session-data`. Install this plugin first.
- `gh` CLI authenticated against GitHub — required for the events feed and PR title enrichment.
- `jq` — required by bundled scripts.

## Files

```
daily-recap/
├── .claude-plugin/plugin.json
├── CHANGELOG.md
├── README.md
└── skills/
    └── engineering-recap/
        ├── SKILL.md
        ├── assets/template.html       — Bitwarden-branded HTML scaffold
        ├── scripts/gather-gh-events.sh — Events feed window helper
        └── references/render-guide.md — Placeholder map + HTML recipes
```
