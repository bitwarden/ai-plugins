---
name: reading-mailcatcher-api
description: Use this skill whenever you need to read an email from the local Bitwarden Mailcatcher inbox — account verification, magic link login, trial activation, OTP codes, password resets, or any other email-driven flow. Queries the Mailcatcher REST API at http://localhost:1080 to find a message by recipient or subject and extract URLs or tokens from its body. Prefer this over the Mailcatcher browser UI in automated contexts (Playwright's browser CORS restrictions block direct fetch access). Invoke whenever a workflow needs to read, click, or extract content from a message Bitwarden just sent — including account creation, login flows, organization invites, trial activations, and password resets.
argument-hint: --recipient <email> --pattern <subject-keyword> [--link-filter <regex>]
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/read_mailcatcher.py *), Read
---

## Quick reference — use the script

For all programmatic uses (test runs, ad-hoc fetches, debugging), call the co-located script directly:

```
${CLAUDE_PLUGIN_ROOT}/skills/reading-mailcatcher-api/scripts/read_mailcatcher.py --recipient <email> --pattern <subject-keyword> [--link-filter <regex>]
```

- **stdout** (on success): the extracted URL, ready to navigate to or paste into a form field
- **exit 1 + stderr** (on failure): `NO_MATCH: <diagnostic>` — either no message matched after one retry, or the matched message contained no URL passing the link filter

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

## Result

See the **Quick reference** at the top of this file for the script's exit-and-stdout contract — that is the authoritative return shape.
