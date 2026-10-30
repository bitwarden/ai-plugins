---
name: weekly-recap
context: fork
agent: general-purpose
description: Generates an interactive HTML recap of the user's own engineering work over one Monday-to-Friday workweek, ready for a weekly standup, 1:1 prep, or sharing with colleagues. Use when the user asks what they worked on, shipped, merged, reviewed, or moved tickets and docs on over a week ("this week", "last week", "the week of" a date), or asks for a "weekly recap", "weekly standup", "weekly summary", "week in review", or "weekly update", including phrasings like "throw together what I did last week". Not for a single day or part of a day, for looking up a single specific PR, commit, ticket, or document, for someone else's activity, for meeting recaps, for repository-level overviews, or for critiquing how a single Claude Code session went.
---

# Weekly Recap

Generate the daily-recap page for a whole workweek. This skill defines only what differs for a week. Everything else comes from the daily-recap skill in the same plugin.

## Using the daily-recap skill

Read `${CLAUDE_PLUGIN_ROOT}/skills/daily-recap/SKILL.md` and follow its workflow (steps 1-7), its `references/render-guide.md`, and its rules on escaping, credentials, untrusted text, the Content-Security-Policy, and deleting `work/`. Where this file says something different, this file wins.

That file is read as plain text, so two things in it need translating:

- Its relative paths (`scripts/`, `assets/`, `references/`) are under `${CLAUDE_PLUGIN_ROOT}/skills/daily-recap/`. Call the scripts by that absolute path.
- Its `${CLAUDE_PLUGIN_DATA}` is not set in the Bash environment. Use this output directory instead: `out_dir="${DAILY_RECAP_OUTPUT_DIR:-${CLAUDE_PLUGIN_DATA}/daily-recaps}"`.

## The week

A week is the five workdays Monday through Friday. Each workday uses daily-recap's day boundary (`DAILY_RECAP_CUTOFF_HOUR`, default 07:00, and `TZ`), so the week runs from the cutoff on Monday to the cutoff on Saturday. Pick the dates, then take the actual bounds from the scripts' `window` output rather than recomputing them.

- "last week", "weekly standup", or no time given: the most recent Monday-to-Friday week whose Friday workday has ended.
- "this week": Monday of the current week through today. Today's window ends in the future, which is fine.
- A specific date: the Monday-to-Friday week containing it.

To step between dates, source `${CLAUDE_PLUGIN_ROOT}/skills/daily-recap/scripts/date-utils.sh` and use `add_days`, which handles GNU and BSD `date`.

## Collecting

In daily-recap's step 1, run (a), (b), and (d) once per workday in the week, passing that day's date and naming each file by it (`events-YYYY-MM-DD.json`, `sessions-YYYY-MM-DD.json`, `atlassian-YYYY-MM-DD.json`). Run (c) once for the whole week: `gather-gh-search.sh MONDAY LAST-DAY`, where LAST-DAY is Friday, or today for "this week". Skip (e) and leave `{{TODAY_BANNER}}` empty: "this week" already covers today, and for a past week the banner would sit across a weekend gap.

GitHub's events feed holds only the last 300 events from the last 30 days, so a busy week can be truncated, and a week more than 30 days old has no events at all. When any day's `feed_complete` is `false`, say so in the recap and rely on `search.json` for PRs.

Merge the per-day results before step 5. A session or PR that spans several days is one item, and a stream can run across the whole week.

## Rendering

- Page file: `recap-week-YYYY-MM-DD.html` in `$out_dir`, named by Monday's date. Use this name in steps 6 and 7.
- Page title: in the copied page, replace "Daily Recap" with "Weekly Recap" in the `<title>`, the "Engineering Daily Recap" header span, the "Daily Recap · Interactive" eyebrow, and the "Bitwarden · Engineering Daily Recap" footer. All four sit outside the `<script>` block, so the Content-Security-Policy hash is unaffected.
- `{{DATE}}`: the range, for example `2026-10-19 – 2026-10-23`.
- `{{STANDUP_PERIOD}}`: `Week · {range}`.
- `{{STANDUP_LABEL_PAST}}` is `Last week` and `{{STANDUP_LABEL_NEXT}}` is `This week`, per the render guide's Weekly column.
- Stats sum across the week. Count each PR, repository, and session once, and follow the render guide's dedupe rules for Jira and Confluence.
- Timeline: order events across the week and put a day divider before each day's events, using the After Midnight divider's markup with the text `{Weekday} · {YYYY-MM-DD}`. Leave out the After Midnight divider; post-midnight events stay under their workday.
- The BLUF and Last week bullets summarize the week's main outcomes, not each day in turn.
