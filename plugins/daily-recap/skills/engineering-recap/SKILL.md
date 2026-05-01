---
name: engineering-recap
description: Generates the user's engineering daily recap as an interactive HTML deliverable combining Claude Code sessions with GitHub events. **YOUR FIRST ACTION** for any retrospective query about the user's own coding work MUST be to invoke this skill — do NOT gather context first or respond with an inline summary. Trigger phrases include time words ("yesterday", "this morning", "last night", "this week", "before lunch", any past date); activity questions ("what did I work on/ship/merge/push", "what was I doing"); single-word retrospectives ("recap", "summary", "standup", "1:1 prep"); deliverable verbs ("throw together", "pull together", "summarize", "analyze sessions"); audience cues ("show colleagues", "for my manager"); format mentions ("html page", "interactive recap"). The user expects the HTML artifact every time, not a chat summary. SKIP only for specific PR/commit/ticket lookups, someone else's activity, meeting recaps, or repo-level overviews.
---

# Engineering Recap

Generate a polished, interactive HTML recap of the user's engineering work for standup, 1:1s, or sharing with colleagues.

## Day boundary: 7am local time

Many engineers work past midnight. **Window for "yesterday" = (yesterday 7am local) → (today 7am local)**. Late-night work folds into the prior workday. The "Today/Fresh" banner only shows events from 7am local onward.

The cutoff defaults to 07:00 in the system timezone (DST-safe). Override the hour with `DAILY_RECAP_CUTOFF_HOUR` (e.g. `5` for early-morning crews). Override the timezone with the standard `TZ` env var (e.g. `TZ=America/Los_Angeles`) — useful when generating a recap for someone else.

When in doubt, look for a clustering gap. A clear 4+ hour quiet window after the early-morning activity is the natural boundary.

## Workflow

### 1. Gather data (in parallel)

These are independent — run in parallel:

**(a) GitHub events** — bundled script computes the local-time window and converts to UTC:

```bash
${CLAUDE_PLUGIN_ROOT}/skills/engineering-recap/scripts/gather-gh-events.sh YYYY-MM-DD > /tmp/recap-events.json
```

**(b) Claude Code sessions** — delegate to the `claude-retrospective:extracting-session-data` skill (which handles the project-id path mangling, noise-directory exclusion, and content vs mtime quirks). Use its `filter-sessions.sh --since` and `extract-data.sh --type user-prompts --session ID` to pull the data; do not roll your own `find` / `jq` over the JSONL.

### 2. Capture all GitHub event types — not just PR creation

`PullRequestEvent` (opened/closed/merged/labeled), `PullRequestReviewEvent` (approved/commented), `PullRequestReviewCommentEvent` (inline diff comments — capture body + path), `IssueCommentEvent`, `PushEvent` (branch + head SHA), `CreateEvent` (branches **and brand-new repositories** — check `ref_type`), `DeleteEvent` (post-merge cleanup).

**Sweep detection:** 3+ approvals in a 5-minute window across different repos with similar titles → surface as a single "cross-repo sweep" stream, not N separate items.

### 3. Enrich PR titles in one batched call

Don't loop `gh pr view`. Build a single GraphQL query with aliases for each PR:

```bash
gh api graphql -f query='{ a: repository(owner:"bitwarden",name:"android"){pullRequest(number:6851){title author{login} state}} b: repository(...) }'
```

For tiny PR sets (<5), parallel `gh pr view` calls are fine.

### 4. Summarize sessions

For each session in scope, ask `claude-retrospective:extracting-session-data` for the user prompts, tool usage, and statistics. Filter to entries where `.timestamp` falls inside the window — sessions can span multiple days.

**When to dispatch parallel servitors:** Only when there are 3+ projects each with 3+ substantive sessions. For typical days (≤2 projects, or many small sessions), inline summarization is faster and cheaper.

### 5. Synthesize themed streams

Group by feature/theme — **not one card per session**. Two sessions on the same PR = one stream. A typical day produces 3–8 streams across 1–4 projects. Each stream: title (the theme, not the session ID), status (`completed`/`open`/`deferred`), 3–8 specific bullets (file paths, commit SHAs, PR numbers + titles).

Cross-reference: branch creates / pushes that match worktree work → tag with `Session: {title}`. Approvals don't usually map to a session.

### 6. Render the HTML

Copy the template to the recap output, then fill the `{{...}}` placeholders:

```bash
cp ${CLAUDE_PLUGIN_ROOT}/skills/engineering-recap/assets/template.html ~/Documents/daily-recap/recap-{YYYY-MM-DD}.html
```

CSS is tuned to the Bitwarden brand palette — don't regenerate it. `${CLAUDE_PLUGIN_ROOT}/skills/engineering-recap/references/render-guide.md` has the full placeholder map and HTML recipes for the more complex injection points (project sections, timeline events, today banner).

PR refs use `<a class="pr-ref" href="...">#NNNN</a>`. Always include PR titles (a bare `#6849` is useless). Late-night events (after midnight local but before today's cutoff hour) get a `🌙 After Midnight` divider in the timeline view, _not_ the Today banner — the Today banner is only for events past today's cutoff hour on the current calendar day.

### 7. Open in browser

```bash
open ~/Documents/daily-recap/recap-{YYYY-MM-DD}.html
```

Summarize to the user: stats, headline theme, and that the standup card has a Copy button.

## Style

Bitwarden brand palette + Inter font (already in template). Keep prose colleague-presentable. If the user requests a non-default tone (e.g. "neutral", "for sharing externally"), adjust the prose and footer accordingly without touching the CSS.

## Bundled resources

- `assets/template.html` — HTML scaffold with `{{...}}` placeholders.
- `scripts/gather-gh-events.sh` — pulls events feed with the local-time workday window applied. Honors `DAILY_RECAP_CUTOFF_HOUR` and `TZ` env vars.
- `references/render-guide.md` — placeholder map + HTML recipes (read only when you need a specific injection shape).

## Plugin dependency

This skill expects the `claude-retrospective` plugin to be installed for session extraction. Specifically: `claude-retrospective:extracting-session-data`.
