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
# Bare tool rules, which match every use of the tool
grep -nE '"(Bash|WebFetch|WebSearch|Write|Edit)"' .claude/settings.json
# Credential directories
grep -nE '"(Read|Edit)\(//[^"]*/\.(ssh|aws|gnupg)/' .claude/settings.json
```

**Red Flags:**

- `Read(//**)` - Read access to entire filesystem
- `Write(//**)` - Write access to entire filesystem
- A bare `Bash` rule in `allow` - auto-approves every shell command
- `Read(//Users/username/.ssh/**)` - access to SSH keys
- `Read(//etc/**)` - access to system config

A bare rule in `deny` is the opposite: `"deny": ["WebFetch"]` is the strongest form of that
control, not a defect.

**Automated Detection:**

```bash
#!/bin/bash
# detect-broad-permissions.sh

ISSUES=0

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
elif jq -e '.permissions.allow[]? | select(. == "Bash")' .claude/settings.json >/dev/null 2>&1; then
    echo "CRITICAL: Bare Bash rule in allow auto-approves every shell command"
    ISSUES=1
fi

# Check for sensitive paths
if grep -rE '(\.ssh|/etc|\.aws|\.config)' .claude/settings.json 2>/dev/null; then
    echo "WARNING: Permissions reference sensitive directories"
    ISSUES=1
fi

if [ $ISSUES -eq 0 ]; then
    echo "OK: Permissions appropriately scoped"
    exit 0
else
    exit 1
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
    "curl.*| sh"
    "curl.*| bash"
    "wget.*| sh"
    "dd if="
    "mkfs"
    "> /dev/sd"
)

FOUND_DANGEROUS=0

for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if grep -qE "$pattern" .claude/settings.json 2>/dev/null; then
        echo "CRITICAL: Dangerous command auto-approved: $pattern"
        FOUND_DANGEROUS=1
    fi
done

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
      "Bash(git diff:*)",
      "Bash(npm run build)"
    ]
  }
}
```

`npm install` and `./gradlew test` are deliberately absent; the Safe Command Whitelist below
gives the reason.

---

## Safe Command Whitelist

**Read-Only Commands (Generally Safe):**

- `git status`, `git log`, `git diff`, `git show`
- `ls`, `cat`, `head`, `tail`, `less`
- `grep`, `find`, `wc`, `sort`
- `npm list`, `./gradlew tasks`

**State-changing but conventionally approved, with narrow patterns only:**

- `npm ci`, `./gradlew build` - reproducible from a lock file or build script, but both still
  execute project-controlled code
- `git pull` (on feature branches)
- `mkdir -p` (with scoped paths)

`npm install` and `./gradlew test` are deliberately absent. An npm lifecycle script is arbitrary
code execution at install time, and a Gradle test task runs whatever the build file names, so
neither belongs in a list offered as the safe default.

**Commands Requiring Approval:**

- Any `rm` command
- `git push --force`
- `chmod`, `chown`
- Piped curl/wget
- System-level commands
