---
description: Guided Q&A to capture your standup preferences into a dedicated, load-on-demand ~/.claude/standup/preferences.md
allowed-tools: Read, Write, Edit, Bash(diff:*), Bash(cp:*), Bash(mkdir:*), Bash(date:*), Bash(rm:*), Glob
---

Walk the user through a guided Q&A to assemble their standup preferences and write them to `~/.claude/standup/preferences.md`.

## Tone

Ask questions. Generate the file. Nothing else.

- No narration ("I will now...", "Next I'll...", "Bobert has read...")
- No explanations of what you're doing or why
- No meta-commentary about the process
- No confirmations between steps unless the user needs to approve the diff

Invisible work (reading files, detecting existing preferences) happens silently. The only output is questions, the diff preview, and the final summary.

## Target

`~/.claude/standup/preferences.md` — resolve the `~` against the current user's home directory. This is ALWAYS the target regardless of the current working directory. NEVER substitute cwd, and NEVER write to `~/.claude/CLAUDE.md` or any other auto-loaded file.

## Preference modules

The preferences file is assembled from module fragments under `${CLAUDE_PLUGIN_ROOT}/templates/user/`, concatenated in this fixed order:

| Order | Module file                    | `##` section it contributes    |
| ----- | ------------------------------ | ------------------------------ |
| 1     | `identity.md`                  | `## Identity & workspace`      |
| 2     | `output-format.md`             | `## Output format`             |
| 3     | `output-style.md`              | `## Output style`              |
| 4     | `recurring-responsibilities.md`| `## Recurring responsibilities`|

## Steps

1. **Detect existing file.** Use `Read` to read `~/.claude/standup/preferences.md`.
   - If it exists, use `AskUserQuestion` to ask how to proceed:
     - **Merge** — re-render only the `##` sections the user re-answers, leaving the file's other `##` sections intact.
     - **Replace** — back up and regenerate the whole file.
     - **Abort** — stop without changing anything.

     Default: **Abort**.
   - If it does not exist, proceed straight to step 2.

2. **Gather preferences via `AskUserQuestion`.** Ask across a few rounds, at most four questions per round. For free-text values that have no meaningful suggestions (Atlassian display name, GitHub username), ask as a **direct conversational question in prose** — do NOT use `AskUserQuestion` for these fields, since the tool requires at least 2 options and there are none to offer. For free-text values that do have suggestions (email, Jira base URL, timezone), use `AskUserQuestion` and present the suggestions plus **Other**. Cover:

   - **Identity & workspace:** Gather display name **before** email — the email suggestions are derived from it.
     - **Atlassian display name**: Ask as a direct conversational question: `"What is your Atlassian display name? Usually this is your first and last name."` Wait for the user's reply before proceeding to email.
     - **Atlassian email**: Offer exactly two suggestions derived from the display name, plus **Other**. Given a display name of `FirstName LastName`, the two suggestions are `firstinitiallastname@bitwarden.com` (e.g. `alovelace@bitwarden.com`) and `firstname@bitwarden.com` (e.g. `ada@bitwarden.com`). No other email guesses.
     - **GitHub username**: Ask as a direct conversational question: `"What is your GitHub username? (Your GitHub handle — this can be anything — or reply 'skip' to leave the placeholder.)"` Never guess or derive this from the display name.
     - **Jira base URL**: Offer `https://your-org.atlassian.net` plus **Other** — do NOT hardcode any specific organization's URL as the only choice.
     - **Timezone**: Offer `America/Chicago`, `America/New_York`, `Europe/London`, `UTC`, plus **Other**; note that a blank timezone falls back to `UTC`.
   - **Output format:** destination backend (`local markdown file` / `stdout to chat`); section labels (any three labels you prefer, e.g. `Last week` / `This week` / `Blockers`); markdown-link rendering (`on` / `off`).
   - **Output style:** whether to collapse routine/automated work into a single trailing tail bullet (`on` / `off`).

   For anything the user skips or leaves at default, keep that module's `[YOUR-PREFERENCE]`-style placeholder verbatim rather than inventing a value.

3. **Render.** For each module under `${CLAUDE_PLUGIN_ROOT}/templates/user/<slug>.md`:
   - Read the module and substitute the gathered answers for its placeholders. For any answer the user skipped, leave the `[YOUR-PREFERENCE]` placeholder verbatim.
   - Concatenate the module bodies in the fixed order above (identity → output-format → output-style → recurring-responsibilities), separated by a single blank line.
   - Prepend this generated header (read `{VERSION}` from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`; get `{YYYY-MM-DD}` via `Bash(date)`):

     ```
     # Standup Preferences

     <!-- Generated by standup v{VERSION} on {YYYY-MM-DD}.
          This is a load-on-demand file: the standup skill reads it explicitly at
          report time. It is NOT auto-loaded into other projects or conversations.
          Edit freely; replace any [YOUR-PREFERENCE] placeholder with your own value. -->
     ```

   - **Merge mode:** re-render ONLY the `##` sections the user re-answered in step 2, and splice them back into the existing file in place of the matching `##` sections, leaving all other sections (and the existing header) intact.

4. **Diff + confirm.**
   - If the target file exists, write the rendered content to a temp file (e.g. `/tmp/standup-prefs-preview-$$.md`) and run `diff -u "$HOME/.claude/standup/preferences.md" /tmp/standup-prefs-preview-$$.md` via `Bash`; display the diff.
   - If the target is new, display the full rendered content.

   Then use `AskUserQuestion` with options **Apply**, **Show diff again**, **Cancel**. On **Show diff again**, redisplay and ask again. On **Cancel**, stop without writing (and clean up the temp file).

5. **Backup, then write.**
   - Ensure the destination directory exists: `mkdir -p "$HOME/.claude/standup"` via `Bash`.
   - **If the target file already exists** (Merge or Replace path): copy it to `~/.claude/standup/preferences.md.bak-$(date -u +%Y%m%dT%H%M%SZ)` via `Bash` and capture the backup path. Then use `Edit` to update the file with the full rendered content. Fall back to `Write` only if `Edit`'s old-string match fails.
   - **If the target file is new:** use `Write` to create `~/.claude/standup/preferences.md` with the rendered content. (`Edit` is not viable for a file that was never Read.)
   - Clean up the temp preview file.

6. **Summary.** Report:
   - The target path written.
   - Which sections/modules were included (Merge mode: which were re-rendered).
   - The backup file path, if one was made.
   - A reminder that `~/.claude/standup/preferences.md` is **load-on-demand** — the standup skill/agent reads it explicitly at report time and it is NOT auto-loaded into other conversations — and to revisit any remaining `[YOUR-PREFERENCE]` placeholders before relying on it.

## Notes

- **Never write without an explicit Apply confirmation.**
- **Never skip the backup step** when overwriting an existing file.
- Preserve `[YOUR-PREFERENCE]` placeholders verbatim — do not invent answers for values the user skipped.
- The target is ALWAYS `~/.claude/standup/preferences.md`, regardless of the current working directory. NEVER substitute cwd, and NEVER write to `~/.claude/CLAUDE.md`.
