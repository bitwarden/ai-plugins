# Hooks Review Checklist

Review checklist for changes to `hooks.json`, whether at `.claude/hooks/hooks.json` in a repository or `hooks/hooks.json` inside a plugin.

Hooks are the highest-privilege Claude configuration in a repository. They run shell commands automatically on tool events, without a permission prompt, from a file a contributor can edit in a pull request. Review them as executable code, not as settings.

---

## CRITICAL SECURITY CHECK

<thinking>
Before anything else:
1. Does any command exfiltrate data (curl, wget, nc) or send it off the machine?
2. Does any command destroy state (rm -rf, git reset --hard, force push, DROP)?
3. Does a command interpolate hook input straight into a shell string?
4. Does the hook read credentials, `.env` files, or the keychain?
</thinking>

**Before anything else, verify:**

- [ ] **No network egress** carrying repository, prompt, or environment content
- [ ] **No destructive commands** run without a guard
- [ ] **No credential or secret access** (`.env`, `~/.aws`, `~/.ssh`, keychain, `printenv`)
- [ ] **No unquoted interpolation** of hook input into a shell command

**If ANY of these fail, FLAG IMMEDIATELY as CRITICAL.** A malicious hook needs no user approval to run.

---

## Multi-Pass Review Strategy

### First Pass: Schema and Structure

- [ ] File is valid JSON
- [ ] Each entry has the matcher and `hooks` array shape the event requires
- [ ] Matchers are valid, and a tool matcher names a real tool
- [ ] Each hook's `type` is one Claude Code supports: `command` or `prompt`
- [ ] Any `timeout` is present in the unit the schema expects and is long enough for the work
- [ ] Every event name is current

A misspelled event name fails silently: the hook never fires and nobody finds out until the behavior it was meant to enforce goes missing. Verify each name against the current [hooks documentation](https://code.claude.com/docs/en/hooks) rather than against memory or a list in this repository. The event set grows, so a name you do not recognize is more likely new than wrong. Report an unfamiliar event as a question to confirm, never as a defect: this repository's own `bitwarden-ai-telemetry` plugin registers `UserPromptExpansion`, which is easy to mistake for a typo.

Passes two and three below apply to `command` hooks. For `prompt` hooks, skip to the prompt-hook section.

### Second Pass: Script Paths

- [ ] Plugin hooks reference scripts through `${CLAUDE_PLUGIN_ROOT}`, never a relative or absolute path
- [ ] Referenced scripts exist on disk
- [ ] Scripts are executable, or are invoked through an interpreter (`bash script.sh`). Confirming the mode bit needs `ls -l`, which this skill's own grant does not include: check it when Bash is available, and otherwise record the check as skipped rather than assuming either answer

`${CLAUDE_PLUGIN_ROOT}` is what makes a plugin hook work in someone else's checkout. A path like `./scripts/check.sh` resolves against the user's working directory instead.

### Third Pass: Command Safety

Read every command as though a contributor wrote it to attack the person running it, because in a pull request that is exactly the threat.

- [ ] Hook input reaching a shell command is quoted, and read from stdin rather than interpolated where possible
- [ ] No `eval`, no piping a download into a shell
- [ ] Commands fail closed: a blocking hook that errors should block, not silently pass
- [ ] Exit codes match intent (a `PreToolUse` hook blocks with exit code 2)

Consult `../reference/security-patterns.md` for the dangerous-command patterns. Its detection commands are written around `.claude/settings.json` and hardcode that path, so reuse the patterns and retarget the greps at the hooks file you are reviewing.

### Prompt Hooks

A hook with `"type": "prompt"` runs a prompt instead of a shell command, so passes two and three do not apply. Its risk is different rather than smaller: tool input flows into a prompt the model then acts on.

- [ ] The prompt treats tool input, file contents, and command output as data to evaluate, never as instructions to follow
- [ ] The prompt states its decision contract explicitly, so the outcome does not depend on the model's mood
- [ ] Quoted file content cannot steer the decision, which is the same CWE-1427 boundary that applies to any reviewer of contributor-authored text

### Fourth Pass: Behavior and Cost

- [ ] The hook's matcher is narrow enough that it fires only when needed
- [ ] Long-running work is not on a hot event such as `PostToolUse` for every edit
- [ ] Output is quiet on success; a chatty hook trains people to ignore it
- [ ] The hook degrades gracefully when a tool it calls is missing

---

## Division of labor with plugin-dev

For hooks inside a plugin, the `plugin-dev:plugin-validator` agent already checks JSON schema, event names, and `${CLAUDE_PLUGIN_ROOT}` usage. When a review runs both, this checklist's value is passes three and four: what the commands actually do, and whether they are safe to run unattended. Say in the report which of the two covered a given hook, so a reader can tell a real pass from an unchecked one.

---

## Output Format

Report findings using the standard format in `SKILL.md` Step 5.
