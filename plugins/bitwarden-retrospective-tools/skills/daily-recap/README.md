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
- A standup card with a Copy button
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

## Requirements

- `gh`, authenticated with `gh auth login` (without it the recap covers sessions only)
- `jq`
- `bash` with GNU or BSD `date` (Linux and macOS both work)

## Scripts

Both scripts can be run on their own for debugging:

```bash
# Window and GitHub events for a workday (defaults to the most recently completed one)
scripts/gather-gh-events.sh 2026-10-13

# Session digests for a UTC window
scripts/find-sessions.sh 2026-10-13T11:00:00Z 2026-10-14T11:00:00Z [--include-home]
```

`find-sessions.sh` skips sessions launched from your home directory or temp directories, since those tend to be ad-hoc. Pass `--include-home` to keep home-directory sessions.

GitHub's events feed only holds your most recent 300 events from the last 30 days. Recaps for older or very busy days note when early events may be missing.

`scripts/daily-recap.test.sh` tests all three scripts against fixture session logs and a stubbed `gh`, so it reads no real data and makes no network calls. It is plain bash and needs only `jq`:

```bash
scripts/daily-recap.test.sh
```

## Privacy & Security

- Everything runs locally. Session logs are read, never modified, and the scripts keep temporary data in a private temp directory that is removed when they exit. The gathered events and session digests are kept beside the recap pages and replaced on each run.
- GitHub data comes from your own events feed through `gh`, including private-repository activity you can see. Review a recap before sharing it outside the team.
- Text from GitHub and sessions is HTML-escaped when the page is rendered, and the page's Content-Security-Policy only lets its own script run and blocks network requests other than the brand fonts.

## Maintaining the Template

The Content-Security-Policy in `assets/template.html` pins the inline script by its SHA-256 hash. After changing the script (or reformatting it with Prettier), regenerate the hash and replace the `sha256-...` value in the policy:

```bash
perl -0777 -ne 'print $1 if /<script>(.*?)<\/script>/s' assets/template.html | openssl dgst -sha256 -binary | openssl base64
```

A stale hash leaves the page readable but disables filtering and the Copy button, and the browser console reports the blocked script.
