---
name: reading-mailcatcher-api
description: Read an email from the local Bitwarden Mailcatcher inbox and extract a URL or token from it. Use for account verification links, magic-link logins, trial activations, organization invites, emergency access, and other email-driven flows in local testing. Queries the Mailcatcher REST API at http://localhost:1080 by recipient and subject; preferred over the browser UI in automation because Playwright CORS blocks direct fetch.
argument-hint: "--recipient <email> [--pattern <subject-keyword>] [--link-filter <regex>]"
allowed-tools: "Read, Bash(${CLAUDE_PLUGIN_ROOT}/skills/reading-mailcatcher-api/scripts/read_mailcatcher.py:*), Bash(${CLAUDE_PLUGIN_ROOT}/skills/reading-mailcatcher-api/scripts/get_admin_email.py:*)"
---

# Reading the Mailcatcher API

## Quick reference — use the script

For all programmatic uses (test runs, ad-hoc fetches, debugging), call the co-located script directly. It is user-invocable: trigger it from any Claude Code session with the arguments below and Claude runs the script and returns the extracted URL (or the `NO_MATCH` diagnostic).

```
${CLAUDE_PLUGIN_ROOT}/skills/reading-mailcatcher-api/scripts/read_mailcatcher.py --recipient <email> [--pattern <subject-keyword>] [--link-filter <regex>]
```

For example, to pull a verification link:

```
${CLAUDE_PLUGIN_ROOT}/skills/reading-mailcatcher-api/scripts/read_mailcatcher.py --recipient testuser-s1@example.com --pattern "Verify"
```

- **`--pattern`** is optional; omit it to select the most recent message for the recipient
- **`--link-filter`** is optional; it defaults to `verify|confirm|signup|token|trial|login|finish-signup`. This is the value the exit rows below tell you to "loosen or fix", so it is what you are starting from
- **stdout** (on success): the extracted URL, ready to navigate to or paste into a form field
- **exit code** (on failure): see the table below

| Exit | Meaning                                                                            | Correct response                                                                                                                             |
| ---- | ---------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| 0    | matching URL printed on stdout                                                     | use it                                                                                                                                       |
| 1    | `NO_MATCH`: no matching message arrived (the script retried once after a 3s sleep) | the email has not arrived yet or the filters are too narrow; re-check `--recipient`, then widen or drop `--pattern`                          |
| 1    | matched a message, but no URL in it matched `--link-filter` (no retry)             | the link is there but the filter missed it; loosen or fix `--link-filter`                                                                    |
| 1    | matched URLs, but none is on the local dev allowlist (no retry)                    | stderr names the rejected host(s); add the right one to `MAILCATCHER_ALLOWED_HOSTS` (see Prerequisites) rather than widening `--link-filter` |
| 2    | usage error (bad or missing arguments)                                             | fix the invocation                                                                                                                           |
| 3    | Mailcatcher unreachable or returned invalid JSON                                   | Mailcatcher is not running or unreachable, so start its Docker Compose service and retry                                                     |

The script already retries once after a 3-second sleep on the first miss; callers don't need their own retry loop. See `references/manual-api-walkthrough.md` for the underlying Mailcatcher API the script wraps — consult it when modifying the script or debugging unexpected output.

A second granted helper, `${CLAUDE_PLUGIN_ROOT}/skills/reading-mailcatcher-api/scripts/get_admin_email.py`, prints the Bitwarden dev admin address (read only from `adminSettings.admins` in your `bitwarden/server` checkout's `dev/secrets.json`). Use it to supply `--recipient` for the Admin Portal magic-link flow. See `references/email-patterns.md` for the exact invocation, the `--secrets-file` override, the `--all` flag, and its exit-3 behavior.

## When to Use

Invoke this skill whenever a workflow needs to:

- Click a verification link sent to a new account's email
- Log into the Admin Portal via magic link
- Activate a trial or invite via a link in a welcome/trial email
- Extract a token embedded in a link from an email body

## Prerequisites

Mailcatcher must be running (Docker Compose service) before invoking the script. If it isn't, the script exits 3 with an `ERROR: Mailcatcher unreachable` message on stderr. A `WARNING: plain body empty ... using HTML body for URL extraction` line on stderr is non-fatal: the script falls back to the HTML body and still succeeds.

The script always reads Mailcatcher at `http://localhost:1080`, the fixed endpoint across Bitwarden dev environments; there is no URL override. Extracted URLs are restricted to a local dev allowlist (`localhost`, `127.0.0.1`, `::1`, `bitwarden.test`). If your environment's emails link to another local hostname, add it to the comma-separated `MAILCATCHER_ALLOWED_HOSTS` env var, which extends (never replaces) that allowlist.

## Common Email Types and Patterns

See `references/email-patterns.md` for subject lines, link formats, and extraction commands for each email type: account verification, Admin Portal magic link, trial activation, organization invite, emergency access, and the welcome email.

## Important Notes

- **Tokens expire** — extract and use links immediately; do not cache them for later steps
- **No auth required** — Mailcatcher runs with no credentials on localhost:1080
- **High-volume sessions** — when many test accounts are created, always filter by recipient email, not just subject, to avoid getting the wrong message
- **CORS blocker** — never attempt `fetch('http://localhost:1080/...')` from Playwright's browser context; always use the co-located script from the agent shell
