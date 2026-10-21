# Bitwarden Beads Tools Plugin

Keeps the project's beads in view while you work in Claude Code.

## Overview

[Beads](https://github.com/steveyegge/beads) is a git-backed issue tracker driven by the `bd` CLI. This plugin reads the current project's open, in-progress, and blocked beads with `bd list --json` and shows them beside the conversation, so the state of the work is visible without leaving the session or running `bd` by hand. It is a hooks module (`hooks/register.tsx`) loaded through Claude Code's function hooks.

The plugin refreshes when an interactive session starts, every 30 seconds after that, whenever a Bash tool call runs a `bd` command, and when the session's working directory changes. In a directory that is not a beads project, `bd list` fails and the plugin stays out of the way: no pane opens and the status line is left empty.

## What It Shows

| Surface     | What It Shows                                                                                                                                                                                           |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Pane        | A **Beads** pane grouped into In progress, Blocked, and Open, each with its count. Every row shows the priority, the bead id, and the title, sorted by priority and then id within each group.          |
| Status line | A one-line count such as `beads: 1 in progress, 2 blocked, 4 open`, or `beads: none open` when the project has nothing outstanding, or `beads: error reading bd list` when its output cannot be parsed. |
| Command     | `/beads-pane` refreshes the list and opens the pane, replying with the same count. Outside a beads project it replies that there is nothing to read.                                                    |

The pane opens on its own at session start when the directory is a beads project. Headless runs (`claude -p` and the SDK) skip the pane and the 30-second poll.

## Installation

```bash
/plugin install bitwarden-beads-tools@bitwarden-marketplace
```

## Usage

Start Claude Code in a directory that holds a beads project and the pane opens with the session. To bring it back after closing it, or to refresh it on demand:

```
/beads-pane
```

## Requirements

- The `bd` CLI from [beads](https://github.com/steveyegge/beads), version 1.3 or later, on `PATH`. The plugin passes `--brief`, which earlier releases reject, so an older `bd` reads as a directory with no beads project.
- A Claude Code build with function hooks (plugins whose `hooks/hooks.json` lists `modules`).

## Development

The plugin's tests run under Claude Code's plugin test runner, and the manifest and hooks module are checked by the validator:

```bash
claude plugin validate plugins/bitwarden-beads-tools
claude plugin test plugins/bitwarden-beads-tools
```

When the plugin is loaded from this folder with `--plugin-dir` in an interactive session, Claude Code writes its API declarations to `.claude-plugin/types/`, which `tsconfig.json` extends so `tsc -p plugins/bitwarden-beads-tools` type-checks the module. That folder is generated on each load and ignores itself.

## Privacy & Security

Everything runs locally. The plugin runs `bd list` in the session's working directory with a fixed argument list and a 10-second timeout, reads only the id, title, status, priority, and type of each bead, and sends nothing anywhere.
