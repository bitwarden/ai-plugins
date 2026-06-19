---
name: completing-breakdown
description: Complete a Bitwarden Tech Breakdown — update the Status block to `Complete` and move the breakdown folder into the team's `completed/` subfolder so the active directory only contains in-flight work. Use when a team has finished delivering the work captured in a Tech Breakdown and is ready to archive it. Triggered by phrasings such as "complete this breakdown", "mark the breakdown as done", "archive the breakdown", "move breakdown to completed", "finish the breakdown", "wrap up the breakdown".
argument-hint: "[<breakdown-path | jira-key | slug>]"
arguments: breakdown
allowed-tools: Read, Edit, Glob, Bash(git mv:*), Bash(git status:*), Bash(mkdir:*), AskUserQuestion
---

# Completing a Tech Breakdown

## Overview

Help the user retire a Tech Breakdown once the work it describes has shipped. The skill flips the Status block in `breakdown.md` to `Complete`, then moves the entire breakdown folder (`breakdown.md`, `tasks.md`, any sibling artifacts) under the team's `completed/` subdirectory. The active team directory should only contain breakdowns that are still in flight; the `completed/` subfolder is the archive that preserves the design record without cluttering navigation and providing accurate information for in-flight research.

<HARD-GATE>
Orientation within a breakdown is required. If `$breakdown` was provided at invocation, treat it as the breakdown identifier (path, Jira key, or slug) and resolve it via `Glob` under `tech-breakdowns/` to a real `breakdown.md`, then confirm the resolved path with `AskUserQuestion` before proceeding. Otherwise, ask the user which breakdown to complete — they can give a path, a Jira key, or a slug — and resolve the same way. If the user already named it earlier in the conversation, confirm the resolved path with `AskUserQuestion` before proceeding.

Once the breakdown is found, do NOT update the Status or move the folder until both hold:

- The resolved folder is not already inside a `completed/` directory. If it is, surface that and stop — the breakdown is already archived.
- The working tree is clean (`git status` in the `tech-breakdowns` checkout shows no uncommitted changes that would be entangled with the move). If it is not clean, surface the dirty files and ask the user whether to proceed or stash first.

</HARD-GATE>

## Key Principles

- **Status flip then move.** Update `breakdown.md` first so the commit that moves the folder also carries the terminal-state edit. Reversing the order leaves a window where the file is at its new path with stale status.
- **Preserve history.** Use `git mv` rather than `mv`. The breakdown folder's history is the design record; moving outside git rewrites it as a delete + add and breaks blame.
- **Confirm before destructive operations.** The folder move is reversible but disruptive — links to the old path break. Surface the source path, destination path, and the affected files once before doing the move.
- **Don't touch sibling artifacts.** `tasks.md` and other files in the folder move with the folder unchanged.

## Phases

### Phase 1: Resolve the breakdown

Use the orientation rules from the HARD-GATE to locate `<team>/<JIRA-KEY>-<short-slug>/breakdown.md` in the `tech-breakdowns` working copy. Record the resolved values:

- `BREAKDOWN_PATH` — absolute path to `breakdown.md`.
- `BREAKDOWN_FOLDER` — the parent folder.
- `TEAM_DIR` — the team directory (`BREAKDOWN_FOLDER`'s parent).
- `DEST_FOLDER` — `<TEAM_DIR>/completed/<JIRA-KEY>-<short-slug>/`.

Read `breakdown.md` and surface the current Status block to the user before proceeding.

### Phase 2: Update the Status block

Edit `breakdown.md` in place. Update the Status block:

- `Status:` — `Complete`
- `Last substantive update:` — today's date + the literal note `breakdown completed`

Leave `Active owner / contact:` unchanged; the historical record should keep pointing at the engineer who ran the breakdown.

Do not edit the Spec, Plan, Tasks, or any other section. The breakdown's content is now the as-shipped record.

### Phase 3: Move the folder

1. Ensure the `completed/` directory exists under `TEAM_DIR`. `git mv` does not create missing parent directories — if `<TEAM_DIR>/completed/` does not exist yet, run `mkdir -p <TEAM_DIR>/completed/` first. The first breakdown a team completes will hit this case.
2. Run `git mv <BREAKDOWN_FOLDER> <DEST_FOLDER>` from inside the `tech-breakdowns` working copy. This moves `breakdown.md`, `tasks.md`, and any sibling artifacts in one operation while preserving history.
3. Surface the result to the user:
   - Old path: `<team>/<JIRA-KEY>-<short-slug>/`
   - New path: `<team>/completed/<JIRA-KEY>-<short-slug>/`
   - Files moved: list from `git status`.

Leave the commit to the user — they may want to bundle the status flip + move with a referencing message (`PM-XXXXX: complete breakdown`) and push at their own cadence.

## Output

When all phases are complete, tell the user:

1. The new path of `breakdown.md` under the `completed/` subfolder.
2. That the Status block now reads `Complete`.
3. That the move is staged in git and waiting for them to commit.
