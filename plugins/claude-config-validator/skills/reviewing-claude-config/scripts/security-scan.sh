#!/bin/bash
# security-scan.sh
# Comprehensive security scan for Claude configuration files
#
# Usage: ./security-scan.sh [claude-directory]
# Default: the .claude directory of the current working directory, falling back to
# three levels above this script, which is the .claude root under the standalone
# .claude/skills/reviewing-claude-config/scripts/ layout. Under a plugin install that
# fallback resolves to the plugin root instead, so pass the directory explicitly there.

set -eo pipefail

# Determine Claude directory
if [ -n "$1" ]; then
    CLAUDE_DIR="$1"
elif [ -d "${PWD}/.claude" ]; then
    CLAUDE_DIR="${PWD}/.claude"
else
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    CLAUDE_DIR="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
fi

# Validate directory exists
if [ ! -d "${CLAUDE_DIR}" ]; then
    echo "Error: Directory '${CLAUDE_DIR}' does not exist"
    exit 1
fi

echo "=== Claude Configuration Security Scan ==="
echo "Scanning: ${CLAUDE_DIR}"
echo ""

ISSUES_FOUND=0
CHECKS_SKIPPED=0

# ============================================================================
# Check 1: Committed settings.local.json
# ============================================================================
echo "[1/4] Checking for committed settings.local.json..."

if git ls-files 2>/dev/null | grep -q "settings.local.json"; then
    echo "  ❌ CRITICAL: settings.local.json is committed to git"
    echo "     Files found:"
    git ls-files | grep "settings.local.json" | sed 's/^/     - /'
    echo ""
    echo "     Remediation:"
    echo "     git rm --cached .claude/settings.local.json"
    echo "     echo '.claude/settings.local.json' >> .gitignore"
    echo ""
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo "  ✅ OK: settings.local.json not in git"
fi
echo ""

# ============================================================================
# Check 2: Hardcoded secrets
# ============================================================================
echo "[2/4] Scanning for hardcoded secrets..."

SECRET_FOUND=0
TEMP_FILE=$(mktemp)

# OpenAI API keys (sk-...)
if grep -rE "sk-[a-zA-Z0-9]{32,}" "${CLAUDE_DIR}" 2>/dev/null | grep -v "security-scan.sh" | grep -v "security-patterns.md" | grep -vE '(^|[:=[:space:]"'\''])sk-EXAMPLE' > "${TEMP_FILE}"; then
    echo "  ❌ CRITICAL: OpenAI API key pattern detected"
    echo "     Locations:"
    cat "${TEMP_FILE}" | sed 's/^/     /'
    echo ""
    SECRET_FOUND=1
fi

# GitHub tokens (ghp_..., gho_...)
if grep -rE "gh[po]_[a-zA-Z0-9]{36}" "${CLAUDE_DIR}" 2>/dev/null | grep -v "security-scan.sh" | grep -v "security-patterns.md" | grep -vE '(^|[:=[:space:]"'\''])ghp_EXAMPLE' > "${TEMP_FILE}"; then
    echo "  ❌ CRITICAL: GitHub token pattern detected"
    echo "     Locations:"
    cat "${TEMP_FILE}" | sed 's/^/     /'
    echo ""
    SECRET_FOUND=1
fi

# Generic credentials (apiKey: "...", password: "...", etc.)
# More sophisticated: Look for quotes around values, exclude documentation examples
if grep -rE '(apiKey|api_key|password|passwd|token|secret)["'\'']?\s*[:=]\s*["'\''][^"'\'']{8,}' "${CLAUDE_DIR}" 2>/dev/null | \
   grep -v "security-scan.sh" | \
   grep -v "security-patterns.md" | \
   grep -vE '[:=][[:space:]]*["'\''](sk-EXAMPLE|ghp_EXAMPLE|EXAMPLE|your-key-here|xxx|XXX|<)' > "${TEMP_FILE}"; then
    echo "  ❌ CRITICAL: Potential hardcoded credential detected"
    echo "     Locations:"
    cat "${TEMP_FILE}" | sed 's/^/     /'
    echo ""
    echo "     Note: Review these manually - may be false positives in documentation"
    echo ""
    SECRET_FOUND=1
fi

rm -f "${TEMP_FILE}"

if [ $SECRET_FOUND -eq 0 ]; then
    echo "  ✅ OK: No hardcoded secrets detected"
else
    echo "     Remediation:"
    echo "     - Remove hardcoded credentials from files"
    echo "     - Use environment variables instead"
    echo "     - Document required env vars in README"
    echo ""
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi
echo ""

# ============================================================================
# Check 3: Broad permissions
# ============================================================================
echo "[3/4] Validating permission scoping..."

if [ -f "${CLAUDE_DIR}/settings.json" ]; then
    PERM_ISSUES=0
    PERM_SKIPPED=0

    # Check for wildcard permissions
    if grep -qE '"(Read|Write|Edit)\(//\*\*\)"' "${CLAUDE_DIR}/settings.json" 2>/dev/null; then
        echo "  ❌ CRITICAL: Filesystem-wide permission rule"
        echo "     File: ${CLAUDE_DIR}/settings.json"
        echo "     Issue: Read(//**), Write(//**), or Edit(//**) covers the whole filesystem"
        echo ""
        PERM_ISSUES=1
    fi

    if command -v jq >/dev/null 2>&1 && ! jq empty "${CLAUDE_DIR}/settings.json" >/dev/null 2>&1; then
        echo "  ❌ CRITICAL: settings.json is not valid JSON, so Claude Code does not load it"
        echo "     File: ${CLAUDE_DIR}/settings.json"
        echo ""
        PERM_ISSUES=1
        SETTINGS_PARSE_FAILED=1
    fi

    # A bare tool rule matches every use of the tool. In allow that is the broadest grant
    # available; in deny it is the strongest control. Telling them apart needs the array the
    # rule sits in, so this check requires jq and is recorded as skipped without it.
    if [ "${SETTINGS_PARSE_FAILED:-0}" -eq 1 ]; then
        echo "  ⚠️  SKIPPED: bare-tool-rule check needs a settings.json that parses"
        echo ""
        CHECKS_SKIPPED=$((CHECKS_SKIPPED + 1))
        PERM_SKIPPED=1
    elif command -v jq >/dev/null 2>&1; then
        if jq -e '.permissions.allow[]? | select(test("^(Bash|Write|Edit|WebFetch|WebSearch)$"))' \
            "${CLAUDE_DIR}/settings.json" >/dev/null 2>&1; then
            echo "  ❌ CRITICAL: Bare tool rule in permissions.allow"
            echo "     File: ${CLAUDE_DIR}/settings.json"
            echo "     Issue: a bare rule such as \"Bash\" matches every use of the tool"
            echo ""
            PERM_ISSUES=1
        fi
    else
        echo "  ⚠️  SKIPPED: bare-tool-rule check needs jq to tell allow from deny"
        echo ""
        CHECKS_SKIPPED=$((CHECKS_SKIPPED + 1))
        PERM_SKIPPED=1
    fi

    if grep -qE '"(autoApprovedTools|autoApproved)"' "${CLAUDE_DIR}/settings.json" 2>/dev/null; then
        echo "  ❌ CRITICAL: Unread permission key"
        echo "     File: ${CLAUDE_DIR}/settings.json"
        echo "     Issue: Claude Code reads permissions.allow/deny/ask, not autoApprovedTools."
        echo "            The file looks configured but has no effective rules."
        echo ""
        PERM_ISSUES=1
    fi

    # Sensitive paths, in allow only. The same path in deny is the control, not a defect,
    # so this needs the array the rule sits in and is recorded as skipped without jq.
    if [ "${SETTINGS_PARSE_FAILED:-0}" -eq 1 ]; then
        echo "  ⚠️  SKIPPED: sensitive-path check needs a settings.json that parses"
        echo ""
        CHECKS_SKIPPED=$((CHECKS_SKIPPED + 1))
        PERM_SKIPPED=1
    elif command -v jq >/dev/null 2>&1; then
        SENSITIVE_PATHS=(".ssh" ".aws" ".gnupg" ".config/" "/etc" "id_rsa" "credentials")
        for path in "${SENSITIVE_PATHS[@]}"; do
            if jq -e --arg p "$path" \
                '(.permissions.allow // [])[] | select(contains($p))' \
                "${CLAUDE_DIR}/settings.json" >/dev/null 2>&1; then
                echo "  ⚠️  WARNING: permissions.allow references a sensitive path: $path"
                echo "     File: ${CLAUDE_DIR}/settings.json"
                echo "     Review manually to ensure appropriate scoping"
                echo ""
                PERM_ISSUES=1
            fi
        done
    else
        echo "  ⚠️  SKIPPED: sensitive-path check needs jq to tell allow from deny"
        echo ""
        CHECKS_SKIPPED=$((CHECKS_SKIPPED + 1))
        PERM_SKIPPED=1
    fi

    if [ $PERM_ISSUES -eq 0 ] && [ $PERM_SKIPPED -eq 1 ]; then
        :
    elif [ $PERM_ISSUES -eq 0 ]; then
        echo "  ✅ OK: Permissions appropriately scoped"
    else
        echo "     Remediation:"
        echo "     - Scope Read/Write permissions to project directory only"
        echo "     - Specify individual Bash commands, not wildcards"
        echo "     - Remove access to sensitive directories (~/.ssh, ~/.aws, /etc)"
        echo ""
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
else
    echo "  ℹ️  No settings.json found (OK)"
fi
echo ""

# ============================================================================
# Check 4: Dangerous commands
# ============================================================================
echo "[4/4] Checking for dangerous command auto-approvals..."

if [ -f "${CLAUDE_DIR}/settings.json" ]; then
    DANGEROUS_FOUND=0
    DANGEROUS_SKIPPED=0

    # Define dangerous command patterns
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

    # allow only: the same command in deny is the control, not an auto-approval.
    if [ "${SETTINGS_PARSE_FAILED:-0}" -eq 1 ]; then
        echo "  ⚠️  SKIPPED: dangerous-command check needs a settings.json that parses"
        echo ""
        CHECKS_SKIPPED=$((CHECKS_SKIPPED + 1))
        DANGEROUS_SKIPPED=1
    elif command -v jq >/dev/null 2>&1; then
        for pattern in "${DANGEROUS_PATTERNS[@]}"; do
            if jq -e --arg p "$pattern" \
                '(.permissions.allow // [])[] | select(test($p))' \
                "${CLAUDE_DIR}/settings.json" >/dev/null 2>&1; then
                echo "  ❌ CRITICAL: Dangerous command auto-approved: ${pattern}"
                echo "     File: ${CLAUDE_DIR}/settings.json"
                DANGEROUS_FOUND=1
            fi
        done
    else
        echo "  ⚠️  SKIPPED: dangerous-command check needs jq to tell allow from deny"
        echo ""
        CHECKS_SKIPPED=$((CHECKS_SKIPPED + 1))
        DANGEROUS_SKIPPED=1
    fi

    if [ $DANGEROUS_SKIPPED -eq 1 ]; then
        :
    elif [ $DANGEROUS_FOUND -eq 0 ]; then
        echo "  ✅ OK: No dangerous command auto-approvals"
    else
        echo ""
        echo "     Dangerous commands can cause:"
        echo "     - Data loss (rm -rf, dd, mkfs)"
        echo "     - Security vulnerabilities (chmod 777, curl | sh)"
        echo "     - Repository damage (git push --force)"
        echo ""
        echo "     Remediation:"
        echo "     - Remove dangerous command auto-approvals"
        echo "     - Scope to safe read-only commands (git status, ls, grep)"
        echo "     - Require manual approval for destructive operations"
        echo ""
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
else
    echo "  ℹ️  No settings.json found (OK)"
fi
echo ""

# ============================================================================
# Summary
# ============================================================================
echo "=== Scan Complete ==="
echo ""

if [ $ISSUES_FOUND -eq 0 ] && [ $CHECKS_SKIPPED -ne 0 ]; then
    echo "⚠️  INCOMPLETE: no issues found, but ${CHECKS_SKIPPED} check(s) could not run"
    echo ""
    echo "The skipped checks are listed above and were not verified,"
    echo "so this is not a clean bill of health."
    echo ""
    exit 2
elif [ $ISSUES_FOUND -eq 0 ]; then
    echo "✅ All security checks passed"
    echo ""
    echo "Claude configuration appears secure:"
    echo "  - No committed local settings"
    echo "  - No hardcoded secrets detected"
    echo "  - Permissions appropriately scoped"
    echo "  - No dangerous command auto-approvals"
    echo ""
    exit 0
else
    echo "❌ Found ${ISSUES_FOUND} critical security issue(s)"
    echo ""
    echo "Review the issues above and remediate before approval."
    echo ""
    echo "Common fixes:"
    echo "  - Remove settings.local.json from git: git rm --cached .claude/settings.local.json"
    echo "  - Replace hardcoded secrets with environment variables"
    echo "  - Scope permissions to project directory only"
    echo "  - Remove dangerous command auto-approvals"
    echo ""
    echo "For detailed remediation guidance, see:"
    echo "  ${CLAUDE_DIR}/skills/reviewing-claude-config/reference/security-patterns.md"
    echo ""
    exit 1
fi
