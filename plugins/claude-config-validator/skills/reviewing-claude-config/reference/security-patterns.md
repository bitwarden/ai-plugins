# Security Patterns for Claude Configuration

Security checks, detection commands, and remediation patterns for Claude configuration files.

---

## Critical Security Checks

Perform these checks for EVERY Claude configuration review:

1. **settings.local.json absent from the changeset**
2. **No hardcoded credentials**
3. **Permissions appropriately scoped**
4. **Every string the file runs or auto-approves has been read**

If any check fails, report it first, then finish the remaining checks so the report can say
which ran. Severity comes from the Security Issues and Settings Issues tables in
`priority-framework.md`, not from having failed here: a committed `settings.local.json`, a
hardcoded credential, and a filesystem-wide or sensitive-path rule in `allow` are CRITICAL,
while a permission merely broader than it needs to be is IMPORTANT.

---

## Detection Scripts

### Check 1: Detect settings.local.json in the changeset

When reviewing, resolve this from the changed-files list, and record the check as skipped
when there is none. The git commands below belong to the human-run `security-scan.sh` path,
which has a shell the skill does not.

**Manual Detection:**

```bash
# Confirm the directory is inside a repository first: outside one, git errors and an
# unguarded check reads as a pass.
git -C /path/to/.claude rev-parse --git-dir >/dev/null 2>&1 || echo "cannot tell: not a repository"

# Ask git directly rather than piping it to grep. Under `pipefail` a matching `grep -q`
# exits first, git takes SIGPIPE, and the pipeline reports failure, so a committed file
# reads as absent whenever git's output is long enough.
git -C /path/to/.claude ls-files -- '*settings.local.json'
```

**Expected Output:**

- **Empty:** File not committed (GOOD)
- **File path:** File is committed (CRITICAL)

For the scripted form, run [`../scripts/security-scan.sh`](../scripts/security-scan.sh). It
is not reproduced here, for the reason recorded at the end of this file.

---

### Check 2: Scan for Hardcoded Secrets

**Pattern Detection:**

```bash
# Search for common secret patterns
grep -rE "(apiKey|api_key|API_KEY|password|passwd|token|secret)\s*[:=]\s*['\"]" .claude/

# Search for specific key prefixes
grep -rE "(sk-[a-zA-Z0-9]{32,}|ghp_[a-zA-Z0-9]{36}|gho_[a-zA-Z0-9]{36})" .claude/
```

**Common Secret Patterns:**

| Pattern         | Regex                                    | Example               |
| --------------- | ---------------------------------------- | --------------------- |
| OpenAI API Key  | `sk-[a-zA-Z0-9]{32,}`                    | `sk-abc123def456...`  |
| GitHub Token    | `ghp_[a-zA-Z0-9]{36}`                    | `ghp_xxxxxxxxxxxx...` |
| Generic API Key | `(api[-_]?key)\s*[:=]\s*['"][^'"]+`      | `apiKey: "abc123"`    |
| Password        | `(password\|passwd)\s*[:=]\s*['"][^'"]+` | `password: "secret"`  |

**Automated Detection:**

```bash
#!/bin/bash
# detect-hardcoded-secrets.sh

FOUND_SECRETS=0

# OpenAI keys
if grep -rE "sk-[a-zA-Z0-9]{32,}" .claude/ 2>/dev/null; then
    echo "CRITICAL: Found OpenAI API key pattern"
    FOUND_SECRETS=1
fi

# GitHub tokens
if grep -rE "gh[po]_[a-zA-Z0-9]{36}" .claude/ 2>/dev/null; then
    echo "CRITICAL: Found GitHub token pattern"
    FOUND_SECRETS=1
fi

# Generic API keys and passwords
if grep -rE "(apiKey|api_key|password|token)\s*[:=]\s*['\"][^'\"]{8,}" .claude/ 2>/dev/null; then
    echo "CRITICAL: Found potential hardcoded credential"
    FOUND_SECRETS=1
fi

if [ $FOUND_SECRETS -eq 0 ]; then
    echo "OK: No hardcoded secrets detected"
    exit 0
else
    exit 1
fi
```

---

### Check 3: Validate Permission Scoping

**Dangerous Permission Patterns:**

```bash
# Filesystem-wide read, write, or edit
grep -nE '"(Read|Write|Edit)\(//\*\*\)"' .claude/settings.json
# Bare tool rules, which match every use of the tool. A hit here is a candidate, not a
# finding: this is line-oriented, so it cannot tell permissions.allow from deny or ask, and
# a hooks matcher written as "matcher": "Write" matches too. Read the array the hit sits in
# before reporting, and report only rules in allow. The Automated Detection block below uses
# jq for the same reason.
grep -nE '"(Bash|Read|Write|Edit|WebFetch|WebSearch|Glob|Grep|Task|NotebookEdit)"' .claude/settings.json
# Credential and system paths, in any specifier form. Also a candidate rather than a finding,
# for the same reason, and it covers Bash rules that read the file as well as Read and Edit.
grep -nE '"[A-Za-z]+\([^"]*(\.ssh|\.aws|\.gnupg|/etc|id_rsa|credentials)' .claude/settings.json
# Rule forms Claude Code does not read, so the file looks configured and is not. Both are
# CRITICAL per ../../reviewing-runtime-configuration/SKILL.md. The colon form fails open in
# either array: in allow it grants nothing, and in deny it is a restriction that never applies.
grep -nE '"(autoApprovedTools|autoApproved)"' .claude/settings.json
grep -nE '"(Bash|Read|Write|Edit|WebFetch|WebSearch|Glob|Grep|Task|NotebookEdit):' .claude/settings.json
# Every tool call runs unprompted, which is broader than any single rule.
grep -nE '"defaultMode"[[:space:]]*:[[:space:]]*"bypassPermissions"' .claude/settings.json
# Fields that execute a command outright, so what they hold is not gated by any rule.
grep -nE '"(apiKeyHelper|command)"[[:space:]]*:' .claude/settings.json
```

**Red Flags:**

- `Read(//**)` - Read access to entire filesystem
- `Write(//**)` - Write access to entire filesystem
- A bare `Bash` rule in `allow` - auto-approves every shell command
- `Read(//Users/username/.ssh/**)` - access to SSH keys
- `Read(//etc/**)` - access to system config, when it sits in `allow`

A bare rule in `deny` is the opposite: `"deny": ["WebFetch"]` is the strongest form of that
control, not a defect.

**Automated Detection:**

```bash
#!/bin/bash
# detect-broad-permissions.sh
# Mirrors Check 3 of scripts/security-scan.sh. Keep the two in step.

SETTINGS=.claude/settings.json
ISSUES=0
SKIPPED=0

if [ ! -f "$SETTINGS" ]; then
    echo "OK: no settings.json"
    exit 0
fi

# Whole-file checks: a defect in any array, or a top-level key.
# Raw-text fallback for the no-jq path; jq repeats both below with escapes decoded.
if ! command -v jq >/dev/null 2>&1 &&
    grep -qE '"(autoApprovedTools|autoApproved)"' "$SETTINGS" 2>/dev/null; then
    echo "CRITICAL: autoApprovedTools is not read; use permissions.allow/deny/ask"
    ISSUES=1
fi

if ! command -v jq >/dev/null 2>&1 &&
    grep -qE '"defaultMode"[[:space:]]*:[[:space:]]*"bypassPermissions"' "$SETTINGS" 2>/dev/null; then
    echo "CRITICAL: permissions.defaultMode is bypassPermissions, so every tool call runs unprompted"
    ISSUES=1
fi

# Rules that grant reach. A path here is the whole meaning of the rule, so a match is a fact
# about the configuration rather than a judgement about a command. A path merely mentioned by a
# command is a judgement call, and Check 4 lists it for a reviewer instead of guessing.
GRANT_STRINGS='[ (.permissions? | objects | .allow? | arrays | .[]),
                 (.permissions? | objects | .additionalDirectories? | arrays | .[]) ]
               | .[] | strings'

# Whole-file keys. They do not depend on the shape of any rule array, so they run outside the
# allow-scoped gate: a malformed allow must not drop them.
if command -v jq >/dev/null 2>&1 && jq -e '(.permissions?.defaultMode? // "") == "bypassPermissions"' \
    "$SETTINGS" >/dev/null 2>&1; then
    echo "CRITICAL: permissions.defaultMode is bypassPermissions, so every tool call runs unprompted"
    ISSUES=1
fi

if command -v jq >/dev/null 2>&1 && jq -e '[paths | last | strings] | any(. == "autoApprovedTools" or . == "autoApproved")' "$SETTINGS" >/dev/null 2>&1; then
    echo "CRITICAL: autoApprovedTools is not read; use permissions.allow/deny/ask"
    ISSUES=1
fi


# A filesystem-wide, bare, rule-form or sensitive-path grant is a defect only where it grants.
# Telling that from deny needs the array the rule sits in, so the four share one gate and report
# themselves skipped together rather than letting a pass stand for a check that never ran.
if ! command -v jq >/dev/null 2>&1; then
    echo "SKIPPED: filesystem-wide, bare-rule, rule-form and sensitive-path checks need jq to tell allow from deny"
    SKIPPED=4
elif ! jq -e 'type == "object"' "$SETTINGS" >/dev/null 2>&1; then
    echo "CRITICAL: jq cannot read settings.json as a JSON object, so these checks could not run"
    echo "SKIPPED: filesystem-wide, bare-rule, rule-form and sensitive-path checks need a settings.json that parses"
    ISSUES=1
    SKIPPED=4
elif ! jq -e '[(.permissions.allow // [])[]] | all(type == "string")' \
    "$SETTINGS" >/dev/null 2>&1; then
    echo "CRITICAL: a permissions.allow rule is not a string, so Claude Code cannot read it"
    echo "SKIPPED: filesystem-wide, bare-rule, rule-form and sensitive-path checks need string rules"
    ISSUES=1
    SKIPPED=4
else
    # Scoped to the rule arrays: a colon inside a command or env value is not a rule.
    if jq -e '(.permissions? | objects | (.allow?, .deny?, .ask?) | arrays | .[] | strings
               | select(test("^(Bash|Read|Write|Edit|WebFetch|WebSearch|Glob|Grep|Task|NotebookEdit):")))' \
        "$SETTINGS" >/dev/null 2>&1; then
        echo "CRITICAL: colon-separated Tool:specifier rule is not read; use Tool(specifier)"
        ISSUES=1
    fi

    if jq -e '(.permissions.allow // [])[] | select(test("^(Read|Write|Edit)\\(//\\*\\*\\)$"))' \
        "$SETTINGS" >/dev/null 2>&1; then
        echo "CRITICAL: Filesystem-wide rule in allow (Read(//**), Write(//**), or Edit(//**))"
        ISSUES=1
    fi

    if jq -e '(.permissions.allow // [])[] | select(test("^(Bash|Read|Write|Edit|WebFetch|WebSearch|Glob|Grep|Task|NotebookEdit)$"))' \
        "$SETTINGS" >/dev/null 2>&1; then
        echo "CRITICAL: Bare tool rule in allow matches every use of the tool"
        ISSUES=1
    fi

    for p in .ssh .aws .gnupg /etc id_rsa credentials; do
        if jq -e --arg p "$p" "${GRANT_STRINGS} | select(contains(\$p))" \
            "$SETTINGS" >/dev/null 2>&1; then
            echo "CRITICAL: a grant references a sensitive path: $p"
            ISSUES=1
        fi
    done
fi

if [ $ISSUES -ne 0 ]; then
    exit 1
elif [ $SKIPPED -ne 0 ]; then
    echo "INCOMPLETE: nothing found, but ${SKIPPED} check(s) could not run"
    exit 2
else
    echo "OK: Permissions appropriately scoped"
    exit 0
fi
```

---

### Check 4: List Every String the Configuration Runs or Auto-Approves

**Locating the fields that hold a command:**

```bash
# Read the strings, do not pattern-match them. Without jq, this lists the fields that hold a
# command; with jq, the Automated Detection block below lists every one with its location.
grep -nE '"(command|apiKeyHelper)"[[:space:]]*:' .claude/settings.json
```

**What to look for when reading the inventory.** These are shapes to recognize, not patterns
to match. A regex over shell strings cannot tell `curl … | sudo bash` from `docker run alpine
sh`, or `eval "$x"` from `npm run eval-suite`, which is why the check lists rather than judges.

| Shape                               | Why it matters                                                                               |
| ----------------------------------- | -------------------------------------------------------------------------------------------- |
| A fetch reaching an interpreter     | `curl`/`wget` into `sh`, `eval`, or `sh -c "$(…)"` runs code the repository does not contain |
| A destructive command with no guard | `rm -rf`, `dd`, `mkfs`, `> /dev/sd*`, `git push --force`                                     |
| A credential read                   | `~/.ssh`, `~/.aws`, `.env`, `printenv`, the keychain                                         |
| A permission widening               | `chmod 777`, `chmod 666`                                                                     |
| Egress                              | Anything carrying repository, prompt, or environment content off the machine                 |

A command that merely mentions one of these is not a finding. What matters is whether it
performs the action, and on input the contributor controls.

**Automated Detection:**

```bash
#!/bin/bash
# list-executed-strings.sh
# Mirrors Check 4 of scripts/security-scan.sh. Keep the two in step.
#
# This does not classify. Pattern-matching shell strings traded a false negative for a false
# positive every time it was tightened, so it reports what will run and leaves the judgement
# to the reviewer, who has the context a regex does not.

SETTINGS=.claude/settings.json

if [ ! -f "$SETTINGS" ]; then
    echo "OK: no settings.json"
    exit 0
elif ! command -v jq >/dev/null 2>&1; then
    echo "SKIPPED: the inventory needs jq to read the file"
    exit 2
elif ! jq -e 'type == "object"' "$SETTINGS" >/dev/null 2>&1; then
    echo "SKIPPED: the inventory needs a settings.json that parses"
    exit 2
fi

# Every string the file runs or auto-approves, paired with its location. Rules in deny and ask
# are controls rather than grants, so they are deleted by position first. Derived from the
# document rather than an enumerated field list, which is what kept missing fields.
jq -r '[ (if type == "object" then del(.permissions?.deny?, .permissions?.ask?) else . end)
         | paths(strings) as $p
         | select(($p | last | tostring) as $k
                  | ($k | IN("type", "matcher", "$schema")) | not)
         | [($p | map(tostring) | join(".")), getpath($p)] ]
       | sort | .[] | @tsv' "$SETTINGS"
```

---

## Comprehensive Security Scan Script

The shipped script is the single source: [`../scripts/security-scan.sh`](../scripts/security-scan.sh).
Run it yourself, optionally passing the directory to scan:

```bash
../scripts/security-scan.sh /path/to/.claude
```

The whole script is not reproduced here. The two Automated Detection blocks above mirror its
Check 3 and Check 4 and are marked to be edited alongside it; everything else lives only in
the script, so there is one copy of the parts most prone to drift.

---

## Remediation Patterns

### Fix 1: Remove Committed settings.local.json

```bash
# Remove from git but keep locally
git rm --cached .claude/settings.local.json

# Ensure .gitignore includes it
if ! grep -q "settings.local.json" .gitignore; then
    echo ".claude/settings.local.json" >> .gitignore
fi

# Commit the fix
git add .gitignore
git commit -m "Remove settings.local.json from git tracking"
```

### Fix 2: Remove Hardcoded Secrets

**Before:**

```json
{
  "apiKey": "sk-1234567890abcdef"
}
```

**After:**

```json
{
  "apiKeyVar": "$OPENAI_API_KEY",
  "note": "Set API key: export OPENAI_API_KEY=your-key"
}
```

**Or remove entirely and document:**

```markdown
# Configuration

Set required environment variables:

- `OPENAI_API_KEY` - Your OpenAI API key
```

### Fix 3: Scope Down Permissions

**Before:**

```json
{
  "permissions": { "allow": ["Read(//**)"] }
}
```

**After:**

```json
{
  "permissions": {
    "allow": [
      "Read(//Users/username/projects/myproject/**)",
      "Read(//Users/username/.claude/projects/**)"
    ]
  }
}
```

### Fix 4: Remove Dangerous Commands

**Before:**

```json
{
  "permissions": { "allow": ["Bash"] }
}
```

**After:**

```json
{
  "permissions": {
    "allow": [
      "Bash(git status:*)",
      "Bash(git log:*)",
      "Bash(git diff --stat)",
      "Bash(npm run build)"
    ]
  }
}
```

`npm install` and `./gradlew test` are deliberately absent; the Safe Command Whitelist below
gives the reason.

---

## Safe Command Whitelist

This is the canonical tiering. `reviewing-runtime-configuration` points here rather than
restating it.

**Read-only:**

- `ls`, `cat`, `head`, `tail`, `less`
- `grep`, `find`, `wc`, `sort`
- `git status`, `npm list`, `./gradlew tasks`

**Read-only in effect, but they honour repository-controlled config:**

- `git log`, `git diff`, `git show` - `textconv` and external diff drivers run code the
  reviewer did not audit, so these want narrow patterns rather than a bare grant

**State-changing, and they execute project- or registry-controlled code:**

- `npm install`, `npm ci`, `./gradlew build`, `./gradlew test` - narrow patterns only, and only
  with a stated reason. A lock file makes `npm ci` reproducible, not inert: lifecycle scripts
  still run at install time, and a Gradle task runs whatever the build file names. None of the
  four is idempotent in any useful sense
- `git pull` (on feature branches)
- `mkdir -p` (with scoped paths)

**Commands Requiring Approval:**

- Any `rm` command
- `git push --force`
- `chmod`, `chown`
- Piped curl/wget
- System-level commands
