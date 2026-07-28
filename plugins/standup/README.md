# standup

Generate a standup report from your real GitHub and Atlassian activity.

## What it does

standup gathers your recent activity over a configurable time window and synthesizes a terse Mode A draft scaffold. It reads from GitHub, Jira, and Confluence (all read-only) and produces a structured starting point in whatever format you specify. The output is a draft — impersonal and data-grounded by design — intended to be rewritten through your own voice. Human finishing is expected, not optional.

Run `/standup:init` once to capture your preferences, then `/standup:generate` whenever you need a report.

## Installation

```bash
/plugin install standup@bitwarden-marketplace
```

Restart Claude Code after installation.

## Requirements

Before `/standup:generate` will run, the following must be available:

| Requirement             | How to satisfy                                                                                                                                                                         |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Python 3.11+            | Must be on `PATH`. No pip installs required (stdlib only).                                                                                                                             |
| `gh` CLI, authenticated | Run `gh auth login`. The CLI must report success on `gh auth status`. Minimum scope: `repo` (or `public_repo` for public-only access).                                                 |
| `JIRA_API_TOKEN`        | Set in your environment. An [Atlassian API token](https://id.atlassian.com/manage-profile/security/api-tokens) with read access to Jira and Confluence. No write permissions required. |
| `JIRA_EMAIL`            | Set in your environment. Your Atlassian account email (e.g. `you@your-org.com`).                                                                                                       |
| `JIRA_BASE_URL`         | Set in your environment. Your Atlassian instance root (e.g. `https://your-org.atlassian.net`).                                                                                         |
| `STANDUP_TZ`            | Optional. IANA timezone name for date calculations (e.g. `America/New_York`). Defaults to `UTC`.                                                                                       |

A preflight hook verifies credentials before any collection starts. If `JIRA_API_TOKEN` is unset or `gh auth status` fails, the plugin blocks collection and surfaces a specific message for each missing prerequisite; it never reads or prints any token value.

## Commands

### `/standup:init`

Guided Q&A that captures your standup preferences and writes them to `~/.claude/standup/preferences.md`. Covers three sections:

- **Identity & workspace:** Atlassian display name and email, GitHub username, Jira base URL, timezone.
- **Destination:** where the report is delivered: a local markdown file at `~/.claude/standup/reports/`, straight to chat, or any destination you describe.
- **Output format:** a freeform Template: describe your desired format, paste in a sample, or accept the built-in default (the default is written verbatim into your preferences file so it is fully visible and editable).

Preferences are saved to `~/.claude/standup/preferences.md` (never auto-loaded into every conversation; loaded only when you run `/standup:generate`).

To update a single section later without regenerating the whole file, say something like "update my output format"; the `standup-report-generator` agent will remind you of this after each report delivery.

### `/standup:generate`

Produces a standup report from your real activity.

```
/standup:generate
/standup:generate last two weeks
/standup:generate 2026-08-01 - 2026-08-15
```

The command hands off to the `standup-report-generator` agent, which reads `~/.claude/standup/preferences.md`, preflights credentials, then runs the pipeline: `generate-standup-report` collects your GitHub and Jira/Confluence activity as JSON, `synthesize-standup-report` turns it into a report matching your output preferences, and `deliver-standup-report` routes the output to your configured destination.

Pass any argument to override the time window or add a one-off instruction. The default window is the last week.

## Output style

The report format is driven entirely by the `## Output format` section of your preferences file: a single freeform Template. Write a few sentences describing how you want the report structured, paste in an example from a past report, or leave it blank to use the plugin's built-in default.

The built-in default produces:

- A one-line red/amber/green (RAG) status summary
- A `Last week` section of past work items
- A `This week` section of in-progress and upcoming work
- A `Blockers` section

The synthesizer treats your Template as applied-as-written. It does not impose extra structure on top of what you describe.

**Per-run overrides.** You can adjust the report for a single run without touching your preferences file by passing an instruction to `/standup:generate`. For example:

```
/standup:generate last two weeks
/standup:generate summarize in three bullet points
/standup:generate focus on Jira items only
```

These override the Template for that run only.

## Sources

The plugin collects nine categories of activity. The time window applies to all categories except `in_progress` and `blocked`, which are current-state snapshots.

| Category           | What it captures                                               |
| ------------------ | -------------------------------------------------------------- |
| `authored_prs`     | GitHub PRs you opened or updated in the window                 |
| `reviews_given`    | GitHub reviews and inline comments you left on others' PRs     |
| `jira_done`        | Jira tickets you resolved in the window                        |
| `jira_created`     | Jira tickets you created in the window                         |
| `jira_comments`    | Jira comments you posted in the window                         |
| `confluence_edits` | Confluence pages you edited in the window                      |
| `jira_grooming`    | Jira field edits you made (via Activity Streams) in the window |
| `in_progress`      | All your in-progress tickets right now (not windowed)          |
| `blocked`          | All your blocked tickets right now (not windowed)              |

GitHub data is collected via the `gh` CLI GraphQL API. Jira and Confluence data is collected via the Atlassian REST API (JQL and CQL search plus the Activity Streams feed for grooming edits).

## Security and privacy

All API access is strictly read-only. The plugin never writes to GitHub, Jira, or Confluence.

**Credentials** are never surfaced to the LLM. `JIRA_API_TOKEN` is read from the environment by the Python collectors and passed as an HTTP Basic auth header. The LLM runner sees only the collection result JSON, never the token. GitHub authentication is handled entirely by the `gh` CLI; the token is not read or printed.

**Minimum permissions required:**

| Service    | Credential                    | Minimum scope                                                  |
| ---------- | ----------------------------- | -------------------------------------------------------------- |
| GitHub     | `gh` CLI session              | `repo` (private repos) or `public_repo` (public only)          |
| Jira       | `JIRA_API_TOKEN`              | Read access to issues, comments, and the Activity Streams feed |
| Confluence | `JIRA_API_TOKEN` (same token) | Read access to pages                                           |

A single Atlassian API token covers both Jira and Confluence. No write permissions are required for either service.

## Cost and performance

**Live-test cost:** <!-- STUB: Addison to fill in — run `/standup:generate` against a real week of activity and record the approximate token count and wall-clock time here. -->

**Time window:** The default window is the last seven days (`last 1 week`). Pass an argument to `/standup:generate` to change it: relative (`last 2 weeks`) or absolute (`2026-08-01 - 2026-08-15`).

**What is and is not windowed:** `in_progress` and `blocked` are current-state snapshots taken at run time, not filtered by the time window. All other categories (authored PRs, reviews, Jira activity, Confluence edits, grooming) are filtered to events within the window.

**GitHub coarse filtering:** GitHub's `updated:>=` filter matches a PR's last-updated timestamp, not per-event activity. The collector fetches any PR last touched within the window and then filters individual events client-side. This means a PR with many old events may be fetched and then produce zero in-window items; that does not indicate an error.

## Example output

<!-- STUB: Addison to fill in — paste the output of a real `/standup:generate` run here, with any sensitive details redacted, so new users can see what an actual report looks like. -->

The example below illustrates the built-in default format:

```
:large_green_circle: Steady progress on three active tracks; no blockers.

`Last week:`
- Resolved a request-timeout regression in the vault sync flow by capping the retry budget in the client layer — [PM-12345](https://example.atlassian.net/browse/PM-12345) (`Done`)
- Reviewed the new device-trust onboarding PR; left detailed feedback on the key-derivation boundary — [your-org/your-repo#9876](https://github.com/your-org/your-repo/pull/9876)
- Organized the Q3 auth initiative ticket tree: created parent/child structure across four epics and set goals, priority, and owners ([BW-456](https://example.atlassian.net/browse/BW-456), [BW-457](https://example.atlassian.net/browse/BW-457))

`This week:`
- Continue the SSO session-binding refactor [PM-23456] (`In Development`)
- Begin scoping the emergency-access flow redesign [PM-34567] (`In Development`)

`Blockers:`
- None
```
