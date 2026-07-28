---
name: deliver-standup-report
description: |
  Delivers a finished standup report to the user's configured destination using optional, pluggable
  backends with graceful fallback. Destination is driven entirely by the user's
  preferences; no personal-skill names are hardcoded.
---

# Deliver Standup Report

This skill takes a finished standup report (markdown) plus the user's preferences and delivers it to a single destination. The user's preferences come from `~/.claude/standup/preferences.md`; read the destination the user configured in that file's `## Destination` section.

## Step 1: Destination Dispatch (single destination, first-match)

Read the destination the user configured in their preferences' `## Destination` section (a freeform value; the two suggestions `local markdown file` and `stdout to chat` are common, but the user may name any target) and deliver to exactly ONE
destination. Attempt the chosen backend; if its required capability is absent,
fall back down the chain and ANNOUNCE the substitution.

| Chosen destination                  | Required capability                                        | If available                                                                                                                                                  | If unavailable → fallback                                  |
| ----------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| an external notes/knowledge backend | a persistence tool for that backend in the current session | Persist the report to that backend as a new entry, and report back to the user how to find it (title / identifier / path as applicable).                      | Fall back to `local markdown file`; note the substitution. |
| `local markdown file`               | Write tool (always available)                              | Write to the user-specified path from prefs; if none specified, write the timestamped default (below). Create the parent directory if needed. Print the path. | n/a (always available)                                     |
| `stdout to chat`                    | none                                                       | Print the finished report directly into the conversation.                                                                                                     | n/a (always available)                                     |

The terminal fallback chain is **configured backend → local markdown → stdout**. Stdout is
always reachable, so delivery never hard-fails.

## Local-markdown Default Path

When `local markdown file` is chosen (or reached by fallback) and prefs specify
no path, write to `~/.claude/standup/reports/standup-<window-end>-<HHMM>.md`,
creating `~/.claude/standup/reports/` if absent. `<window-end>` is the report
window's end date (YYYY-MM-DD). This never overwrites prior reports.

## Graceful Degradation

The skill always delivers SOMETHING. A missing optional skill degrades quietly to
the next capability in the chain, with a one-line note to the user, never an
error.
