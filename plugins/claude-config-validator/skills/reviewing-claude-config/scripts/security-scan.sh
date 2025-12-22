#!/bin/bash
# security-scan.sh
# Comprehensive security scan for Claude configuration files
#
# Usage: ./security-scan.sh [claude-directory]
# Default: Scans parent directory of this script (assumes .claude/skills/reviewing-claude-config/scripts/)

set -eo pipefail

# Determine Claude directory
if [ -n "$1" ]; then
    CLAUDE_DIR="$1"
else
    # Default: Assume script is in .claude/skills/reviewing-claude-config/scripts/
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
if grep -rE "sk-[a-zA-Z0-9]{32,}" "${CLAUDE_DIR}" 2>/dev/null | grep -v "security-scan.sh" | grep -v "security-patterns.md" | grep -v "examples/" > "${TEMP_FILE}"; then
    echo "  ❌ CRITICAL: OpenAI API key pattern detected"
    echo "     Locations:"
    cat "${TEMP_FILE}" | sed 's/^/     /'
    echo ""
    SECRET_FOUND=1
fi

# GitHub tokens (ghp_..., gho_...)
if grep -rE "gh[po]_[a-zA-Z0-9]{36}" "${CLAUDE_DIR}" 2>/dev/null | grep -v "security-scan.sh" | grep -v "security-patterns.md" | grep -v "examples/" > "${TEMP_FILE}"; then
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
   grep -v "examples/" | \
   grep -v "example" | \
   grep -v "EXAMPLE" | \
   grep -v "your-key-here" | \
   grep -v "xxx" > "${TEMP_FILE}"; then
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

    # Check for wildcard permissions
    if grep -q 'Read://\*' "${CLAUDE_DIR}/settings.json" 2>/dev/null; then
        echo "  ❌ CRITICAL: Overly broad Read permissions (Read://*)"
        echo "     File: ${CLAUDE_DIR}/settings.json"
        echo "     Issue: Grants read access to entire filesystem"
        echo ""
        PERM_ISSUES=1
    fi

    if grep -q 'Write://\*' "${CLAUDE_DIR}/settings.json" 2>/dev/null; then
        echo "  ❌ CRITICAL: Overly broad Write permissions (Write://*)"
        echo "     File: ${CLAUDE_DIR}/settings.json"
        echo "     Issue: Grants write access to entire filesystem"
        echo ""
        PERM_ISSUES=1
    fi

    if grep -q '"Bash:\*"' "${CLAUDE_DIR}/settings.json" 2>/dev/null; then
        echo "  ❌ CRITICAL: Auto-approve all Bash commands (Bash:*)"
        echo "     File: ${CLAUDE_DIR}/settings.json"
        echo "     Issue: Allows any bash command without approval"
        echo ""
        PERM_ISSUES=1
    fi

    # Check for sensitive paths
    SENSITIVE_PATHS=(".ssh" ".aws" ".gnupg" "/etc" "id_rsa" "credentials")
    for path in "${SENSITIVE_PATHS[@]}"; do
        if grep -q "$path" "${CLAUDE_DIR}/settings.json" 2>/dev/null; then
            echo "  ⚠️ WARNING: Permissions reference sensitive path: $path"
            echo "     File: ${CLAUDE_DIR}/settings.json"
            echo "     Review manually to ensure appropriate scoping"
            echo ""
            PERM_ISSUES=1
        fi
    done

    if [ $PERM_ISSUES -eq 0 ]; then
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

    # Define dangerous command patterns
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
        "wget.*| bash"
        "dd if="
        "mkfs"
        "> /dev/sd"
    )

    for pattern in "${DANGEROUS_PATTERNS[@]}"; do
        if grep -qE "\".*${pattern}.*\"" "${CLAUDE_DIR}/settings.json" 2>/dev/null; then
            echo "  ❌ CRITICAL: Dangerous command auto-approved: ${pattern}"
            echo "     File: ${CLAUDE_DIR}/settings.json"
            DANGEROUS_FOUND=1
        fi
    done

    if [ $DANGEROUS_FOUND -eq 0 ]; then
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

if [ $ISSUES_FOUND -eq 0 ]; then
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
