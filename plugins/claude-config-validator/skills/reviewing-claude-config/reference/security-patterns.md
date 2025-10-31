# Security Patterns for Claude Configuration

Security checks, detection commands, and remediation patterns for Claude configuration files.

---

## Critical Security Checks

Perform these checks for EVERY Claude configuration review:

1. **settings.local.json NOT in git**
2. **No hardcoded credentials**
3. **Permissions appropriately scoped**
4. **No dangerous command auto-approvals**

If ANY check fails, flag as **CRITICAL** immediately.

---

## Detection Scripts

### Check 1: Detect Committed settings.local.json

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

| Pattern | Regex | Example |
|---------|-------|---------|
| OpenAI API Key | `sk-[a-zA-Z0-9]{32,}` | `sk-abc123def456...` |
| GitHub Token | `ghp_[a-zA-Z0-9]{36}` | `ghp_xxxxxxxxxxxx...` |
| Generic API Key | `(api[-_]?key)\s*[:=]\s*['"][^'"]+` | `apiKey: "abc123"` |
| Password | `(password\|passwd)\s*[:=]\s*['"][^'"]+` | `password: "secret"` |

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
# Check for overly broad permissions
grep -r "Read://\*" .claude/settings.json
grep -r "Write://\*" .claude/settings.json
grep -r "Bash:\*" .claude/settings.json
```

**Red Flags:**
- `Read://*` - Read access to entire filesystem
- `Write://*` - Write access to entire filesystem
- `Bash:*` - Auto-approve ALL bash commands
- `Read://Users/username/.ssh/**` - Access to SSH keys
- `Read:///etc/**` - Access to system config

**Automated Detection:**
```bash
#!/bin/bash
# detect-broad-permissions.sh

ISSUES=0

if grep -q 'Read://\*"' .claude/settings.json 2>/dev/null; then
    echo "CRITICAL: Overly broad Read permissions (Read://*)"
    ISSUES=1
fi

if grep -q 'Write://\*"' .claude/settings.json 2>/dev/null; then
    echo "CRITICAL: Overly broad Write permissions (Write://*)"
    ISSUES=1
fi

if grep -q '"Bash:\*"' .claude/settings.json 2>/dev/null; then
    echo "CRITICAL: Auto-approve all Bash commands (Bash:*)"
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

| Command | Risk | Why Dangerous |
|---------|------|---------------|
| `rm -rf` | Data loss | Recursive deletion without confirmation |
| `git push --force` | Data loss | Overwrites remote history |
| `chmod 777` | Security | Grants all permissions to everyone |
| `curl ... \| sh` | RCE | Executes arbitrary remote code |
| `dd` | Data loss | Low-level disk operations |
| `mkfs` | Data loss | Formats filesystems |
| `:(){ :\|:& };:` | DoS | Fork bomb |

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

**Full automated security scan:**

```bash
#!/bin/bash
# security-scan.sh
# Comprehensive security scan for Claude configuration files

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="${SCRIPT_DIR}/.."
ISSUES_FOUND=0

echo "=== Claude Configuration Security Scan ==="
echo ""

# Check 1: Committed settings.local.json
echo "[1/4] Checking for committed settings.local.json..."
if git ls-files | grep -q "settings.local.json"; then
    echo "  ❌ CRITICAL: settings.local.json is committed to git"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo "  ✅ OK: settings.local.json not in git"
fi
echo ""

# Check 2: Hardcoded secrets
echo "[2/4] Scanning for hardcoded secrets..."
SECRET_FOUND=0

if grep -rE "sk-[a-zA-Z0-9]{32,}" "${CLAUDE_DIR}" 2>/dev/null | grep -v "security-scan.sh"; then
    echo "  ❌ CRITICAL: OpenAI API key pattern detected"
    SECRET_FOUND=1
fi

if grep -rE "gh[po]_[a-zA-Z0-9]{36}" "${CLAUDE_DIR}" 2>/dev/null | grep -v "security-scan.sh"; then
    echo "  ❌ CRITICAL: GitHub token pattern detected"
    SECRET_FOUND=1
fi

if grep -rE '(apiKey|api_key|password|token)["'\'']?\s*[:=]\s*["'\''][^"'\'']{8,}' "${CLAUDE_DIR}" 2>/dev/null | grep -v "security-scan.sh" | grep -v "example"; then
    echo "  ❌ CRITICAL: Potential hardcoded credential detected"
    SECRET_FOUND=1
fi

if [ $SECRET_FOUND -eq 0 ]; then
    echo "  ✅ OK: No hardcoded secrets detected"
else
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi
echo ""

# Check 3: Broad permissions
echo "[3/4] Validating permission scoping..."
PERM_ISSUES=0

if [ -f "${CLAUDE_DIR}/settings.json" ]; then
    if grep -q 'Read://\*' "${CLAUDE_DIR}/settings.json"; then
        echo "  ❌ CRITICAL: Overly broad Read permissions (Read://*)"
        PERM_ISSUES=1
    fi

    if grep -q 'Write://\*' "${CLAUDE_DIR}/settings.json"; then
        echo "  ❌ CRITICAL: Overly broad Write permissions (Write://*)"
        PERM_ISSUES=1
    fi

    if grep -q '"Bash:\*"' "${CLAUDE_DIR}/settings.json"; then
        echo "  ❌ CRITICAL: Auto-approve all Bash commands"
        PERM_ISSUES=1
    fi

    if grep -qE '(\.ssh|\.aws|\.gnupg)' "${CLAUDE_DIR}/settings.json"; then
        echo "  ⚠️  WARNING: Permissions reference sensitive directories"
        PERM_ISSUES=1
    fi

    if [ $PERM_ISSUES -eq 0 ]; then
        echo "  ✅ OK: Permissions appropriately scoped"
    else
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
else
    echo "  ℹ️  No settings.json found (OK)"
fi
echo ""

# Check 4: Dangerous commands
echo "[4/4] Checking for dangerous command auto-approvals..."
DANGEROUS_FOUND=0

if [ -f "${CLAUDE_DIR}/settings.json" ]; then
    DANGEROUS_PATTERNS=(
        "rm -rf"
        "rm -fr"
        "git push --force"
        "git push -f"
        "chmod 777"
        "curl.*\| sh"
        "curl.*\| bash"
        "wget.*\| sh"
        "dd if="
        "mkfs"
    )

    for pattern in "${DANGEROUS_PATTERNS[@]}"; do
        if grep -qE "$pattern" "${CLAUDE_DIR}/settings.json"; then
            echo "  ❌ CRITICAL: Dangerous command auto-approved: ${pattern}"
            DANGEROUS_FOUND=1
        fi
    done

    if [ $DANGEROUS_FOUND -eq 0 ]; then
        echo "  ✅ OK: No dangerous command auto-approvals"
    else
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
else
    echo "  ℹ️  No settings.json found (OK)"
fi
echo ""

# Summary
echo "=== Scan Complete ==="
if [ $ISSUES_FOUND -eq 0 ]; then
    echo "✅ All security checks passed"
    exit 0
else
    echo "❌ Found ${ISSUES_FOUND} critical security issue(s)"
    echo ""
    echo "Review the issues above and remediate before approval."
    exit 1
fi
```

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
  "autoApprovedTools": [
    "Read://*"
  ]
}
```

**After:**
```json
{
  "autoApprovedTools": [
    "Read://Users/username/projects/myproject/**",
    "Read://Users/username/.claude/projects/**"
  ]
}
```

### Fix 4: Remove Dangerous Commands

**Before:**
```json
{
  "autoApprovedTools": [
    "Bash:*"
  ]
}
```

**After:**
```json
{
  "autoApprovedTools": [
    "Bash:git status:*",
    "Bash:git log:*",
    "Bash:git diff:*",
    "Bash:npm install:*",
    "Bash:./gradlew test:*"
  ]
}
```

---

## Safe Command Whitelist

**Read-Only Commands (Generally Safe):**
- `git status`, `git log`, `git diff`, `git show`
- `ls`, `cat`, `head`, `tail`, `less`
- `grep`, `find`, `wc`, `sort`
- `npm list`, `./gradlew tasks`

**Idempotent Commands (Safe):**
- `npm install`, `npm ci`
- `./gradlew build`, `./gradlew test`
- `git pull` (on feature branches)
- `mkdir -p` (with scoped paths)

**Commands Requiring Approval:**
- Any `rm` command
- `git push --force`
- `chmod`, `chown`
- Piped curl/wget
- System-level commands
