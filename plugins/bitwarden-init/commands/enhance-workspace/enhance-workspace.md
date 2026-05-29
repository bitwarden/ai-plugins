---
description: Refresh an existing workspace-level CLAUDE.md by adding missing Bitwarden domain modules
allowed-tools: Read, Write, Edit, Bash(find:*), Bash(wc:*), Bash(tr:*), Bash(dirname:*), Bash(diff:*), Bash(cp:*), Bash(date:*), Bash(rm:*), Glob
---

Refresh an existing workspace-level CLAUDE.md by detecting which Bitwarden domain modules are already present and offering to add the missing ones. Same safety guardrails as `/bitwarden-init:init-workspace` — backup before overwrite, diff preview, explicit Apply confirmation.

## Prerequisites

A workspace-level CLAUDE.md must already exist. If it doesn't, stop and point the user at `/bitwarden-init:init-workspace` instead.

## Steps

1. **Resolve workspace root** the same way `/bitwarden-init:init-workspace` does:
   - Walk up from `cwd`. For each ancestor, count subdirectories containing a `.git` entry. If any ancestor has 2+, propose it.
   - If detection succeeds, ask the user to confirm via `AskUserQuestion` (**Yes, use this** / **No, let me type a different path** / **Cancel**).
   - If detection fails or the user declines, ask them to provide the absolute path.

2. **Locate the target file.** Target is `<workspace-root>/.claude/CLAUDE.md`. If it does not exist, exit with the message above.

3. **Detect installed modules.** For each module in `${CLAUDE_PLUGIN_ROOT}/templates/workspace/`, extract the top-level `## Heading` and check whether it appears in the existing file.

   Build **Installed** and **Missing** lists.

4. **Offer missing modules.** Use `AskUserQuestion` with `multiSelect: true` showing only **Missing** modules. If empty, tell the user all known modules are already present and exit cleanly. Use the one-line summaries from `/bitwarden-init:init-workspace`.

5. **Render new content.**
   - Start from the existing file content.
   - For each selected missing module, append its body to the end, separated by a single blank line.
   - Do not modify or reorder existing content.

6. **Diff + confirm.** Write the rendered content to a temp file. Run `diff -u <target> <temp>` and display. Use `AskUserQuestion` with **Apply**, **Show diff again**, **Cancel**.

7. **Backup, then write.**
   - Copy the existing target to `<target>.bak-$(date -u +%Y%m%dT%H%M%SZ)`.
   - Use `Edit` to update the target with the full rendered content. (`Write` works as a fallback if `Edit`'s old-string match fails for any reason — the file always exists at this point.)
   - Clean up the temp preview.

8. **Summary.** Report which modules were added, the backup path, and a reminder that this file applies to every Bitwarden repo under `<workspace-root>`.

## Notes

- This command **only adds** modules. For a from-scratch rebuild, use `/bitwarden-init:init-workspace` with the **Replace** option.
- If the user added the `sources-of-truth.md` module, newly-appended modules will continue to use the same bracketed reference numbers. The numbers stay meaningful as long as `sources-of-truth.md` is present.
