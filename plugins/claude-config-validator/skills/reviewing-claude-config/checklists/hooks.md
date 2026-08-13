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
- [ ] Every event name is one Claude Code recognizes: `PreToolUse`, `PostToolUse`, `Stop`, `SubagentStop`, `SessionStart`, `SessionEnd`, `UserPromptSubmit`, `PreCompact`, `Notification`
- [ ] Each entry has the matcher and `hooks` array shape the event requires
- [ ] Matchers are valid, and a tool matcher names a real tool

A misspelled event name fails silently: the hook never fires and nobody finds out until the behavior it was meant to enforce goes missing.

### Second Pass: Script Paths

- [ ] Plugin hooks reference scripts through `${CLAUDE_PLUGIN_ROOT}`, never a relative or absolute path
- [ ] Referenced scripts exist on disk
- [ ] Scripts are executable, or are invoked through an interpreter (`bash script.sh`)

`${CLAUDE_PLUGIN_ROOT}` is what makes a plugin hook work in someone else's checkout. A path like `./scripts/check.sh` resolves against the user's working directory instead.

### Third Pass: Command Safety

Read every command as though a contributor wrote it to attack the person running it, because in a pull request that is exactly the threat.

- [ ] Hook input reaching a shell command is quoted, and read from stdin rather than interpolated where possible
- [ ] No `eval`, no piping a download into a shell
- [ ] Commands fail closed: a blocking hook that errors should block, not silently pass
- [ ] Exit codes match intent (a `PreToolUse` hook blocks with exit code 2)

Consult `../reference/security-patterns.md` for the dangerous-command patterns and detection commands.

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
