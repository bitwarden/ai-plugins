# Security Patterns for Claude Configuration

Security checks, detection commands, and remediation patterns for Claude configuration files.

---

## Critical Security Checks

Perform these checks for EVERY Claude configuration review:

1. **settings.local.json absent from the changeset**
2. **No hardcoded credentials**
3. **Permissions appropriately scoped**
4. **No dangerous command auto-approvals**

If ANY check fails, flag as **CRITICAL** immediately, then finish the remaining checks so the report can say which ran.

---

## Detection Scripts

### Check 1: Detect settings.local.json in the changeset

When reviewing, resolve this from the changed-files list, and record the check as skipped
when there is none. The git commands below belong to the human-run `security-scan.sh` path,
which has a shell the skill does not.

**Manual Detection:**

```bash
# Check if file is tracked by git
git ls-files | grep "settings.local.json"

# If output exists, file is incorrectly committed
```

**Expected Output:**

- **Empty:** File not tracked (GOOD)
- **File path:** File is tracked (CRITICAL)

**Automated Detection:**

```bash
#!/bin/bash
# detect-committed-local-settings.sh

if git ls-files | grep -q "settings.local.json"; then
    echo "CRITICAL: settings.local.json is committed to git"
    exit 1
else
    echo "OK: settings.local.json not in git"
    exit 0
fi
```

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
grep -nE '"(Bash|WebFetch|WebSearch|Write|Edit)"' .claude/settings.json
# Credential directories
grep -nE '"(Read|Edit)\(//[^"]*/\.(ssh|aws|gnupg)/' .claude/settings.json
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

ISSUES=0
SKIPPED=0

if grep -qE '"Read\(//\*\*\)"' .claude/settings.json 2>/dev/null; then
    echo "CRITICAL: Overly broad Read permissions (Read(//**))"
    ISSUES=1
fi

if grep -qE '"Write\(//\*\*\)"' .claude/settings.json 2>/dev/null; then
    echo "CRITICAL: Overly broad Write permissions (Write(//**))"
    ISSUES=1
fi

# A bare rule is only a defect in allow. In deny it is the strongest form of the control,
# so this needs the array the rule sits in rather than a file-wide grep. Without jq the check
# cannot tell them apart, so it reports itself skipped rather than letting a pass stand for a
# check that never ran.
if ! command -v jq >/dev/null 2>&1; then
    echo "SKIPPED: bare-rule check needs jq to tell allow from deny"
    SKIPPED=1
elif jq -e '.permissions.allow[]? | select(. == "Bash")' .claude/settings.json >/dev/null 2>&1; then
    echo "CRITICAL: Bare Bash rule in allow auto-approves every shell command"
    ISSUES=1
fi

# Sensitive paths, in allow only. The same path in deny is the control, not a defect.
if ! command -v jq >/dev/null 2>&1; then
    echo "SKIPPED: sensitive-path check needs jq to tell allow from deny"
    SKIPPED=$((SKIPPED + 1))
else
    for p in .ssh .aws .gnupg .config /etc id_rsa credentials; do
        if jq -e --arg p "$p" '(.permissions.allow // [])[] | select(contains($p))' \
            .claude/settings.json >/dev/null 2>&1; then
            echo "WARNING: permissions.allow references a sensitive path: $p"
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

### Check 4: Detect Dangerous Command Auto-Approvals

**Dangerous Command Patterns:**

```bash
# Check for dangerous commands
grep -E "(rm -rf|chmod 777|mkfs|dd|curl.*\| sh)" .claude/settings.json
```

**Dangerous Commands List:**

| Command            | Risk      | Why Dangerous                           |
| ------------------ | --------- | --------------------------------------- |
| `rm -rf`           | Data loss | Recursive deletion without confirmation |
| `git push --force` | Data loss | Overwrites remote history               |
| `chmod 777`        | Security  | Grants all permissions to everyone      |
| `curl ... \| sh`   | RCE       | Executes arbitrary remote code          |
| `dd`               | Data loss | Low-level disk operations               |
| `mkfs`             | Data loss | Formats filesystems                     |
| `:(){ :\|:& };:`   | DoS       | Fork bomb                               |

**Automated Detection:**

```bash
#!/bin/bash
# detect-dangerous-commands.sh

DANGEROUS_PATTERNS=(
    "rm -rf"
    "rm -fr"
    "git push --force"
    "git push -f"
    "chmod 777"
    "chmod 666"
    "curl.*\\| *sh"
    "curl.*\\| *bash"
    "wget.*\\| *sh"
    "wget.*\\| *bash"
    "dd if="
    "mkfs"
    "> /dev/sd"
)

FOUND_DANGEROUS=0

# allow only: the same command in deny is the control, not an auto-approval. An unescaped
# pipe in a pattern would become ERE alternation and match any quoted string containing curl.
if ! command -v jq >/dev/null 2>&1; then
    echo "SKIPPED: dangerous-command check needs jq to tell allow from deny"
else
    for pattern in "${DANGEROUS_PATTERNS[@]}"; do
        if jq -e --arg p "$pattern" '(.permissions.allow // [])[] | select(test($p))' \
            .claude/settings.json >/dev/null 2>&1; then
            echo "CRITICAL: Dangerous command auto-approved: $pattern"
            FOUND_DANGEROUS=1
        fi
    done
fi

if [ $FOUND_DANGEROUS -eq 0 ]; then
    echo "OK: No dangerous command auto-approvals"
    exit 0
else
    exit 1
fi
```

---

## Comprehensive Security Scan Script

The shipped script is the single source: [`../scripts/security-scan.sh`](../scripts/security-scan.sh).
Run it yourself, optionally passing the directory to scan:

```bash
../scripts/security-scan.sh /path/to/.claude
```

It is not reproduced here. An inline copy drifts from the file that actually runs, and the
two had already diverged on how they resolve the directory to scan.

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
