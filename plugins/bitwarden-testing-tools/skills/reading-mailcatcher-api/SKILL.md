---
name: reading-mailcatcher-api
description: Read an email from the local Bitwarden Mailcatcher inbox and extract a URL or token from it. Use for account verification links, magic-link logins, trial activations, OTP codes, password resets, organization invites, and other email-driven flows during local testing. Queries the Mailcatcher REST API at http://localhost:1080 by recipient and subject, and is preferred over the Mailcatcher browser UI in automated contexts because Playwright browser CORS blocks direct fetch. This skill reads messages only; it does not start, stop, or health-check the Mailcatcher container or any other service.
argument-hint: --recipient <email> [--pattern <subject-keyword>] [--link-filter <regex>]
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/read_mailcatcher.py *), Read
---

# Reading the Mailcatcher API

## Quick reference — use the script

For all programmatic uses (test runs, ad-hoc fetches, debugging), call the co-located script directly:

```
${CLAUDE_SKILL_DIR}/scripts/read_mailcatcher.py --recipient <email> --pattern <subject-keyword> [--link-filter <regex>]
```

- **stdout** (on success): the extracted URL, ready to navigate to or paste into a form field
- **exit code** (on failure): see the table below

| Exit | Meaning                                                                                                  | Correct response                                              |
| ---- | -------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| 0    | matching URL printed on stdout                                                                           | use it                                                        |
| 1    | `NO_MATCH`: no matching message arrived (the script retried once after a 3s sleep)                       | case-level failure                                            |
| 1    | matched a message but it held no local-host URL (no retry)                                               | case-level failure; check the `--pattern` and `--link-filter` |
| 2    | usage error (bad or missing arguments)                                                                   | fix the invocation                                            |
| 3    | Mailcatcher unreachable, invalid JSON, or `MAILCATCHER_URL` names a host outside the local dev allowlist | environment failure, not a test failure                       |

The script already retries once after a 3-second sleep on the first miss; callers don't need their own retry loop. See `references/manual-api-walkthrough.md` for the underlying Mailcatcher API the script wraps — consult it when modifying the script or debugging unexpected output.

## User invocation

This skill is user-invocable. From any Claude Code session you can trigger it directly with the arguments declared in the `argument-hint` frontmatter — Claude will run the script and return the extracted URL (or the `NO_MATCH` diagnostic). Useful for debugging email flows, exploring Mailcatcher contents, or sanity-checking the script outside the test pipeline.

Example:

```
--recipient testuser-s1@example.com --pattern "Verify"
```

## When to Use

Invoke this skill whenever a workflow needs to:

- Click a verification link sent to a new account's email
- Log into the Admin Portal via magic link
- Activate a trial or invite via a link in a welcome/trial email
- Extract a one-time code or token from any email body

## Prerequisites

Mailcatcher must be running (Docker Compose service) before invoking the script. If it isn't, the script exits 3 with an `ERROR: Mailcatcher unreachable` message on stderr. See `references/manual-api-walkthrough.md` for a manual reachability check.

The script reads Mailcatcher at `MAILCATCHER_URL` (default `http://localhost:1080`) and restricts extracted URLs to the local dev allowlist; add a custom local host with the comma-separated `PLAYWRIGHT_TESTING_ALLOWED_HOSTS` env var.

## Common Email Types and Patterns

See `${CLAUDE_SKILL_DIR}/references/email-patterns.md` for subject lines, link formats, and extraction commands for all common Bitwarden email types.

## Important Notes

- **Tokens expire** — extract and use links immediately; do not cache them for later steps
- **No auth required** — Mailcatcher runs with no credentials on localhost:1080
- **High-volume sessions** — when many test accounts are created, always filter by recipient email, not just subject, to avoid getting the wrong message
- **CORS blocker** — never attempt `fetch('http://localhost:1080/...')` from Playwright's browser context; always use the co-located script from the agent shell

## References

- `references/email-patterns.md` — per-email-type recipients, subjects, and link filters
- `references/manual-api-walkthrough.md` — raw REST API commands, for debugging the script only
