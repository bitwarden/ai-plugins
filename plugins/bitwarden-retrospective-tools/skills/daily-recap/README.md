# Daily Recap Skill

Builds an interactive HTML page summarizing one workday of your engineering work, drawn from your Claude Code sessions and your GitHub activity. It is meant for standup, 1:1 prep, or a quick share with colleagues, and it saves a file you can keep.

## When to Use

Ask about your own recent work and name a time window or a recap:

```
What did I work on yesterday?
Put together a recap for standup
Make a daily recap for 2026-10-12 that I can show my manager
Summarize what I shipped this morning
```

It does not cover a single PR or ticket lookup, someone else's activity, meeting notes, or a critique of how a single Claude Code session went.

## What You Get

A self-contained page with:

- A stats strip (repositories touched, sessions, PRs opened and approved, GitHub events)
- A standup card with a Copy button; Copy emits markdown links and backtick-wrapped code rather than stripping them
- Work grouped into themed streams per project, filterable by project, status, and keyword
- A GitHub timeline view, filterable by project and keyword
- A short theme-of-the-day summary with open threads

Pages are written to `daily-recaps/recap-YYYY-MM-DD.html` in the plugin's data directory (`${CLAUDE_PLUGIN_DATA}`, under `~/.claude/plugins/data/`) and opened in your browser (`open` on macOS, `xdg-open` on Linux; otherwise the path is printed).

## Configuration

| Variable                  | Default                              | Purpose                                                                                        |
| ------------------------- | ------------------------------------ | ---------------------------------------------------------------------------------------------- |
| `DAILY_RECAP_CUTOFF_HOUR` | `7`                                  | Local hour (0-23) when a workday starts, so late-night work counts toward the day it continues |
| `DAILY_RECAP_OUTPUT_DIR`  | `${CLAUDE_PLUGIN_DATA}/daily-recaps` | Where recap pages are written                                                                  |
| `TZ`                      | system timezone                      | Timezone used for the workday boundary                                                         |
| `CLAUDE_CONFIG_DIR`       | `~/.claude`                          | Where Claude Code session logs are read from                                                   |

Set them in your shell profile or in the `env` block of your Claude Code settings.

### Atlassian Setup (optional)

Jira and Confluence activity are each optional and included independently. Set these to pull them into the recap:

| Variable                               | Purpose                                |
| -------------------------------------- | -------------------------------------- |
| `ATLASSIAN_CLOUD_ID`                   | Your Atlassian Cloud ID                |
| `ATLASSIAN_EMAIL`                      | Account email for the API token        |
| `ATLASSIAN_JIRA_READ_ONLY_TOKEN`       | Enables Jira activity collection       |
| `ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN` | Enables Confluence activity collection |

Without `ATLASSIAN_JIRA_READ_ONLY_TOKEN`, Jira activity is not included. Without `ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN`, Confluence activity is not included. Each source is skipped cleanly on its own; neither requires the other.

These are the same env vars used by `bitwarden-atlassian-tools`. See [its README](../../../bitwarden-atlassian-tools/README.md) for how to obtain and scope the tokens.

## Requirements

- `gh`, authenticated with `gh auth login` (without it the recap covers sessions only)
- `jq`
- `bash` with GNU or BSD `date` (Linux and macOS both work)
- `curl` (only needed for Jira and Confluence collection)

## Scripts

These scripts can be run on their own for debugging:

```bash
# Window and GitHub events for a workday (defaults to the most recently completed one)
scripts/gather-gh-events.sh 2026-10-13

# Authored, reviewed, and commented PRs for the same workday, via GitHub search
scripts/gather-gh-search.sh 2026-10-13

# The same, across a 7-day window (START-DATE to END-DATE, both inclusive)
scripts/gather-gh-search.sh 2026-10-15 2026-10-21

# Jira and Confluence activity for the same workday
scripts/gather-atlassian.sh 2026-10-13

# Session digests for a UTC window
scripts/find-sessions.sh 2026-10-13T11:00:00Z 2026-10-14T11:00:00Z [--include-home]
```

`find-sessions.sh` skips sessions launched from your home directory or temp directories, since those tend to be ad-hoc. Pass `--include-home` to keep home-directory sessions.

GitHub's events feed only holds your most recent 300 events from the last 30 days. Recaps for older or very busy days note when early events may be missing. `gather-gh-search.sh` has no such cap: it searches instead of reading the feed, so it also covers authored, reviewed, and commented PRs over multi-day windows the events feed can't reach.

`scripts/daily-recap.test.sh` tests all five scripts against fixture session logs and stubbed `gh` and `curl`, so it reads no real data and makes no network calls. It is plain bash and needs only `jq`:

```bash
scripts/daily-recap.test.sh
```

## Privacy & Security

- Everything runs locally. Session logs are read, never modified, and the scripts keep temporary data in a private temp directory that is removed when they exit. The gathered events and session digests go in a `work/` subdirectory of the output directory, which the skill deletes at the end of every run, so only the rendered page is left behind.
- GitHub data comes from your own events feed through `gh`, including private-repository activity you can see, and Jira and Confluence data from your own read-only API tokens, including private content you can see. Review a recap before sharing it outside the team.
- Text from GitHub, sessions, and Jira and Confluence is HTML-escaped when the page is rendered, and the page's Content-Security-Policy only lets its own script run and blocks network requests other than the brand fonts.

## Maintaining the Template

The Content-Security-Policy in `assets/template.html` pins the inline script by its SHA-256 hash. After changing the script (or reformatting it with Prettier), regenerate the hash and replace the `sha256-...` value in the policy:

```bash
perl -0777 -ne 'print $1 if /<script>(.*?)<\/script>/s' assets/template.html | openssl dgst -sha256 -binary | openssl base64
```

A stale hash leaves the page readable but disables filtering and the Copy button, and the browser console reports the blocked script.
