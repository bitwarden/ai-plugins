# Bitwarden Pickup Plugin

Adds `/pickup`: clear the conversation, then start the next one where the cleared one ended.

## Overview

`/clear` gives a long conversation a fresh context, but the new conversation starts with no idea what you were doing. `/pickup` clears the conversation and carries the end of it across. You keep working without a long recap and without the old context.

When you type `/pickup`, the plugin:

1. Reads the last two exchanges of the conversation: each prompt and the final reply to it. Tool calls, tool output, and skill bodies stay behind. It cuts each part at 1,000 characters.
2. Runs `/clear`.
3. Adds the two exchanges to the new conversation as a row that the model reads and you do not see.
4. Submits this prompt as you: "We're continuing where another session (`<session id>`, transcript `<path>`) ended. Where did we leave off?"

The model answers from the two exchanges. It opens the old transcript only for what they do not cover.

## Commands

| Command              | What It Does                                                           |
| -------------------- | ---------------------------------------------------------------------- |
| `/pickup`            | Clears, then asks "Where did we leave off?" in the new conversation.   |
| `/pickup <question>` | Clears, then asks your question in place of "Where did we leave off?". |

## Prerequisites

- A Claude Code version that loads hooks modules (`"modules"` in `hooks/hooks.json`).

The plugin has no other dependencies. It makes no network calls and runs no shell commands.

## Installation

```bash
/plugin install bitwarden-pickup@bitwarden-marketplace
```

## Usage

```
/pickup
```

```
/pickup Is the flaky test fixed now?
```

## How It Works

- The plugin is one hooks module, `hooks/register.ts`. It registers `/pickup` when a session starts.
- Only Claude Code's `SessionStart` and `Stop` hook inputs name the transcript path. The plugin keeps the path in its own store, one entry for each session, and removes the entry at `SessionEnd`.
- When no hook has named the path for the session, the prompt names the session ID only. This can happen before the first reply, or when another plugin stops the `SessionStart` hook before it reaches this one.
- `/clear` waits until a command finishes, so the plugin runs it from a timer after `/pickup` returns. If `/clear` fails, a toast says why and nothing is submitted.

## Development

Run the tests and the validator from the repository root:

```bash
claude plugin test plugins/bitwarden-pickup
claude plugin validate plugins/bitwarden-pickup
```

Claude Code writes the API types to `.claude-plugin/types/` when it loads the plugin. That folder ignores itself in git. After a load, type-check with:

```bash
tsc -p plugins/bitwarden-pickup
```

To try a change, start a session with the plugin loaded from disk:

```bash
claude --plugin-dir plugins/bitwarden-pickup
```

## References

- [Claude Code Plugins](https://code.claude.com/docs/en/plugins-reference)
