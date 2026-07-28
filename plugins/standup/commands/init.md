---
description: Guided Q&A to capture your standup preferences into a dedicated, load-on-demand ~/.claude/standup/preferences.md
allowed-tools: Read, Write, Edit, Bash(diff:*), Bash(cp:*), Bash(mkdir:*), Bash(date:*), Bash(rm:*)
---

Walk the user through a guided Q&A to assemble their standup preferences and write them to `~/.claude/standup/preferences.md`.

## Tone

Ask questions. Generate the file. Nothing else.

- No narration ("I will now...", "Next I'll...", "I've read...")
- No explanations of what you're doing or why
- No meta-commentary about the process
- No confirmations between steps unless the user needs to approve the diff

Invisible work (reading files, detecting existing preferences) happens silently. The only output is questions, the diff preview, and the final summary.

## Target

`~/.claude/standup/preferences.md`. Resolve the `~` against the current user's home directory. This is ALWAYS the target regardless of the current working directory. NEVER substitute cwd, and NEVER write to `~/.claude/CLAUDE.md` or any other auto-loaded file.

## Preference modules

The preferences file is assembled from module fragments under `${CLAUDE_PLUGIN_ROOT}/templates/user/`, concatenated in this fixed order. Each module is a clean skeleton: heading plus value target(s) only; all question wording, option suggestions, and the default template text live in this command, not in the modules:

| Order | Module file        | `##` section it contributes |
| ----- | ------------------ | --------------------------- |
| 1     | `identity.md`      | `## Identity & workspace`   |
| 2     | `destination.md`   | `## Destination`            |
| 3     | `output-format.md` | `## Output format`          |
| 4     | `team.md`          | `## Team`                   |

## Steps

1. **Detect existing file.** Use `Read` to read `~/.claude/standup/preferences.md`.
   - If it exists, use `AskUserQuestion` to ask how to proceed:
     - **Replace**: back up and regenerate the whole file.
     - **Abort**: stop without changing anything.

     Default: **Abort**. This command only creates or fully replaces the preferences file; it does not edit an existing file in place. To change individual preferences later, edit `~/.claude/standup/preferences.md` directly.

   - If it does not exist, proceed straight to step 2.

2. **Gather preferences via `AskUserQuestion`.** Ask across a few rounds, at most four questions per round. For free-text values that have no meaningful suggestions (Atlassian display name, GitHub username), ask as a **direct conversational question in prose**, not via `AskUserQuestion`, since the tool requires at least 2 options and there are none to offer. For free-text values that do have suggestions (email, Jira base URL, timezone), use `AskUserQuestion` and present the suggestions plus **Other**. Cover:
   - **Identity & workspace:** Gather display name **before** email; the email suggestions are derived from it.
     - **Atlassian display name**: Ask as a direct conversational question: `"What is your Atlassian display name? Usually this is your first and last name."` Wait for the user's reply before proceeding to email.
     - **Atlassian email**: Offer exactly two suggestions derived from the display name, plus **Other**. Given a display name of `FirstName LastName`, the two suggestions are `firstinitiallastname@your-org.com` (e.g. `alovelace@your-org.com`) and `firstname@your-org.com` (e.g. `ada@your-org.com`). No other email guesses.

<!-- cspell:ignore alovelace firstinitiallastname firstname -->

     - **GitHub username**: Ask as a direct conversational question: `"What is your GitHub username?"` This is required. Do not offer to skip it and never leave a placeholder; if the user does not answer, ask again. Never guess or derive it from the display name.
     - **Jira base URL**: Offer `https://your-org.atlassian.net` plus **Other**. Do NOT hardcode any specific organization's URL as the only choice.
     - **Timezone**: Offer `America/Chicago`, `America/New_York`, `Europe/London`, `UTC`, plus **Other**; note that a blank timezone falls back to `UTC`.

- **Destination:** ask where the user wants the report delivered via `AskUserQuestion`. Offer `local markdown file` and `stdout to chat` as suggestions, plus **Other** for any freeform destination (the destination is not restricted to those two; the user may name any target, e.g. a notes app, a knowledge base, a specific file path). Capture the chosen value verbatim into the `## Destination` section as the `Destination:` value. If the user picks `local markdown file` and wants a specific path, capture the path as the value; otherwise the report defaults to a timestamped file under `~/.claude/standup/reports/` at delivery time.
- **Output format:** ask whether the user wants to describe their own report format or accept the built-in default. If they describe one, capture it verbatim as the entire body of the `## Output format` section. If they accept the default, write the canonical default text VERBATIM as the body of the `## Output format` section: read `${CLAUDE_PLUGIN_ROOT}/skills/synthesize-standup-report/default-output-example.md` and copy its body (the format-description paragraph followed by the fenced sample report) verbatim. There is no in-file "default" placeholder: on default the concrete default text is written out. Either way the `[YOUR-PREFERENCE]` target in `output-format.md` is fully replaced.
  - **Team (optional)**: Ask as a direct conversational question: `"What team are you on? (Optional — used to detect and credit cross-team PR contributions. Leave blank to skip.)"` If the user provides a value, use it as the `[YOUR-PREFERENCE]` in `team.md`. If the user leaves it blank or says skip, write `Team: ` (empty value after the colon) into the rendered module.

Every value in the file is required and concrete: always collect identity and workspace (Atlassian display name, Atlassian email, GitHub username, Jira base URL, timezone), always capture a destination, and always write a concrete output format (the user's custom template or the canonical default verbatim). Re-ask if the user does not provide a required value. A fully-init'd file contains NO `[YOUR-PREFERENCE]` placeholders. Exception: the `Team` field is optional; if the user skips it, write `Team: ` (empty value) and do not re-ask.

3. **Render.** For each module under `${CLAUDE_PLUGIN_ROOT}/templates/user/<slug>.md`:
   - Read the module and substitute the gathered answers for its `[YOUR-PREFERENCE]` targets. Every target must be replaced with a concrete value: all identity/workspace value lines, the destination value, and the output-format body. For `output-format.md`, replace the single `[YOUR-PREFERENCE]` body target with either the user's custom template verbatim or, on default, the verbatim body of `skills/synthesize-standup-report/default-output-example.md` (format-description paragraph + fenced sample). Leave NO `[YOUR-PREFERENCE]` in the rendered output.
   - Concatenate the module bodies in the fixed order above (identity → destination → output-format → team), separated by a single blank line.
   - Prepend this generated header (read `{VERSION}` from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`; get `{YYYY-MM-DD}` via `Bash(date)`):

     ```
     # Standup Preferences

     <!-- Generated by standup v{VERSION} on {YYYY-MM-DD}.
          This is a load-on-demand file: the standup skill reads it explicitly at
          report time. It is NOT auto-loaded into other projects or conversations.
          Edit freely. -->
     ```

4. **Diff + confirm.**
   - If the target file exists, write the rendered content to a temp file (e.g. `/tmp/standup-prefs-preview-$$.md`) and run `diff -u "$HOME/.claude/standup/preferences.md" /tmp/standup-prefs-preview-$$.md` via `Bash`; display the diff.
   - If the target is new, display the full rendered content.

   Then use `AskUserQuestion` with options **Apply**, **Show diff again**, **Cancel**. On **Show diff again**, redisplay and ask again. On **Cancel**, stop without writing (and clean up the temp file).

5. **Backup, then write.**
   - Ensure the destination directory exists: `mkdir -p "$HOME/.claude/standup"` via `Bash`.
   - **If the target file already exists** (Replace path): copy it to `~/.claude/standup/preferences.md.bak-$(date -u +%Y%m%dT%H%M%SZ)` via `Bash` and capture the backup path. Then use `Edit` to update the file with the full rendered content. Fall back to `Write` only if `Edit`'s old-string match fails.
   - **If the target file is new:** use `Write` to create `~/.claude/standup/preferences.md` with the rendered content. (`Edit` is not viable for a file that was never Read.)
   - Clean up the temp preview file.

6. **Summary.** Report:
   - The target path written.
   - Which sections/modules were included (`identity.md`, `destination.md`, `output-format.md`, `team.md`).
   - The backup file path, if one was made.
   - A reminder that `~/.claude/standup/preferences.md` is **load-on-demand** (the standup skill/agent reads it explicitly at report time and it is NOT auto-loaded into other conversations), and, if the user accepted the default output format, that they can edit the `## Output format` section later (e.g. via `edit-standup-preferences`) to customize it.

## Notes

- **Never write without an explicit Apply confirmation.**
- **Never skip the backup step** when overwriting an existing file.
- Every value is required and concrete: never leave a `[YOUR-PREFERENCE]` placeholder anywhere and never invent identity/workspace values. Re-ask if missing. On default output format, write the canonical default text verbatim rather than leaving a placeholder.
- The target is ALWAYS `~/.claude/standup/preferences.md`, regardless of the current working directory. NEVER substitute cwd, and NEVER write to `~/.claude/CLAUDE.md`.
