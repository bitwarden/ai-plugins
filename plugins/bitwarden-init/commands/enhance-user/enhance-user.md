---
description: Refresh an existing user-level ~/.claude/CLAUDE.md by adding missing modules from the Bitwarden init template library
allowed-tools: Read, Write, Edit, Bash(diff:*), Bash(cp:*), Bash(date:*), Bash(rm:*), Glob
---

Refresh an existing `~/.claude/CLAUDE.md` by detecting which behavioral modules from the Bitwarden init template library are already present and offering to add the missing ones. Same safety guardrails as `/bitwarden-init:init-user` — backup before overwrite, diff preview, explicit Apply confirmation.

## Prerequisites

`~/.claude/CLAUDE.md` must already exist. If it doesn't, stop and point the user at `/bitwarden-init:init-user` instead.

## Steps

1. **Read existing file.** Read `~/.claude/CLAUDE.md`. If missing, exit with the message above.

2. **Detect installed modules.** For each module in `${CLAUDE_PLUGIN_ROOT}/templates/user/`, read its file and extract the top-level `## Heading`. A module is considered "installed" if its exact heading (case-insensitive match on the first `## ` line) appears anywhere in the existing file.

   Build two lists:
   - **Installed**: modules whose heading is present.
   - **Missing**: modules whose heading is not present.

3. **Offer missing modules.** Use `AskUserQuestion` with `multiSelect: true` showing only the **missing** modules. If the missing list is empty, tell the user all known modules are already present and exit cleanly. Each option's description should be the one-line summary (see `/bitwarden-init:init-user` for the full table).

4. **Render new content.**
   - Start from the existing file content.
   - For each selected missing module, read `${CLAUDE_PLUGIN_ROOT}/templates/user/<slug>.md` and append it to the end of the file, separated by a single blank line.
   - Do not modify any of the existing content. Do not reorder existing sections.

5. **Diff + confirm.** Write the rendered content to a temp file. Run `diff -u "$HOME/.claude/CLAUDE.md" <temp>` and display. Use `AskUserQuestion` with **Apply**, **Show diff again**, **Cancel**.

6. **Backup, then write.**
   - Copy the existing file to `~/.claude/CLAUDE.md.bak-$(date -u +%Y%m%dT%H%M%SZ)`.
   - Use `Edit` to update `~/.claude/CLAUDE.md` with the full rendered content. (`Write` works as a fallback if `Edit`'s old-string match fails for any reason — the file always exists at this point.)
   - Clean up the temp preview.

7. **Summary.** Report which modules were added, the backup path, and a reminder to revisit any `[YOUR-PREFERENCE]` placeholders.

## Notes

- This command **only adds** modules. It never rewrites or removes existing content. If the user wants a from-scratch rebuild, they should use `/bitwarden-init:init-user` with the **Replace** option.
- Preserve `[YOUR-PREFERENCE]` placeholders verbatim in any newly-added modules.
