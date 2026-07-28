---
name: deliver-standup-report
description: |
  Delivers a finished standup report to the user's configured destination
  (org-roam memory, local markdown file, or stdout) using optional, pluggable
  backends with graceful fallback. Destination is driven entirely by the user's
  preferences; no personal-skill names are hardcoded.
---

# Deliver Standup Report

This skill takes a finished standup report (markdown) plus the user's preferences and delivers it to a single destination. Preferences come from `~/.claude/standup/preferences.md` (load-on-demand per ADR-084): read the `## Output format` section's `Destination` value.

## Step 1 — Destination Dispatch (single destination, first-match)

Read `Destination` from `## Output format` and deliver to exactly ONE
destination. Attempt the chosen backend; if its required capability is absent,
fall back down the chain and ANNOUNCE the substitution.

| Chosen destination    | Required capability                                 | If available                                                                                                                                                                                        | If unavailable → fallback                          |
| --------------------- | --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| `org-roam memory`     | an org-roam persistence tool in the current session | Persist the report as a new org-roam memory node (wrap the report body in a `#+begin_src markdown … #+end_src` block); report the node's title, UUID, and path back to the user. | Fall back to `local markdown file`; note the substitution. |
| `local markdown file` | Write tool (always available)                       | Write to the user-specified path from prefs; if none specified, write the timestamped default (below). Create the parent directory if needed. Print the path.                      | n/a (always available)                             |
| `stdout to chat`      | none                                                | Print the finished report directly into the conversation.                                                                                                                           | n/a (always available)                             |

The terminal fallback chain is **org-roam → local markdown → stdout**. Stdout is
always reachable, so delivery never hard-fails.

## Local-markdown Default Path

When `local markdown file` is chosen (or reached by fallback) and prefs specify
no path, write to `~/.claude/standup/reports/standup-<window-end>-<HHMM>.md`,
creating `~/.claude/standup/reports/` if absent. `<window-end>` is the report
window's end date (YYYY-MM-DD). This never overwrites prior reports.

## org-roam Backend Detail

When persisting to org-roam, pass a sensible node:

- Title like `Standup report <window>`.
- A reference/episodic memory type.
- At least one tag and one alias.
- A short description.
- The report wrapped in a `#+begin_src markdown … #+end_src` block as content.

## Graceful Degradation

The skill always delivers SOMETHING. A missing optional skill degrades quietly to
the next capability in the chain, with a one-line note to the user — never an
error.
