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

if ! git -C "${CLAUDE_DIR}" rev-parse --git-dir >/dev/null 2>&1; then
    CHECKS_SKIPPED=$((CHECKS_SKIPPED + 1))
    echo "  ⚠️  SKIPPED: ${CLAUDE_DIR} is not inside a git repository"
else
    # Ask git directly. Piping it to `grep -q` loses matches under `pipefail`:
    # grep exits on the first hit, git dies of SIGPIPE, and the pipeline reports
    # failure, so a committed file reads as absent whenever git's output is long
    # enough that grep finishes first.
    LOCAL_SETTINGS=$(git -C "${CLAUDE_DIR}" ls-files -- '*settings.local.json') || LOCAL_SETTINGS=""

    if [ -n "${LOCAL_SETTINGS}" ]; then
        echo "  ❌ CRITICAL: settings.local.json is committed to git"
        echo "     Files found:"
        echo "${LOCAL_SETTINGS}" | sed 's/^/     - /'
        echo ""
        echo "     Remediation:"
        echo "     git rm --cached .claude/settings.local.json"
        echo "     echo '.claude/settings.local.json' >> .gitignore"
        echo ""
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        echo "  ✅ OK: settings.local.json not in git"
    fi
fi
echo ""

# ============================================================================
# Check 2: Hardcoded secrets
# ============================================================================
echo "[2/4] Scanning for hardcoded secrets..."

SECRET_FOUND=0
TEMP_FILE=$(mktemp)

# OpenAI API keys (sk-...)
if grep -roE "sk-[a-zA-Z0-9]{32,}" "${CLAUDE_DIR}" 2>/dev/null | grep -v "security-scan.sh" | grep -v "security-patterns.md" | grep -vE '(^|[:=[:space:]"'\''])sk-EXAMPLE' > "${TEMP_FILE}"; then
    echo "  ❌ CRITICAL: OpenAI API key pattern detected"
    echo "     Locations:"
    cat "${TEMP_FILE}" | sed 's/^/     /'
    echo ""
    SECRET_FOUND=1
fi

# GitHub tokens (ghp_..., gho_...)
if grep -roE "gh[po]_[a-zA-Z0-9]{36}" "${CLAUDE_DIR}" 2>/dev/null | grep -v "security-scan.sh" | grep -v "security-patterns.md" | grep -vE '(^|[:=[:space:]"'\''])ghp_EXAMPLE' > "${TEMP_FILE}"; then
    echo "  ❌ CRITICAL: GitHub token pattern detected"
    echo "     Locations:"
    cat "${TEMP_FILE}" | sed 's/^/     /'
    echo ""
    SECRET_FOUND=1
fi

# Generic credentials (apiKey: "...", password: "...", etc.)
# -o so each output line holds one key/value match. Line-oriented filtering would let a
# placeholder elsewhere on the line suppress a real credential beside it.
if grep -roE '(apiKey|api_key|password|passwd|token|secret)["'\'']?\s*[:=]\s*["'\''][^"'\'']{8,}' "${CLAUDE_DIR}" 2>/dev/null | \
   grep -v "security-scan.sh" | \
   grep -v "security-patterns.md" | \
   grep -vE '[:=][[:space:]]*["'\'']([Ss][Kk]-[Ee][Xx][Aa][Mm][Pp][Ll][Ee]|ghp_[Ee][Xx][Aa][Mm][Pp][Ll][Ee]|[Ee][Xx][Aa][Mm][Pp][Ll][Ee]|your-|changeme|xxx|XXX|<)' > "${TEMP_FILE}"; then
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

SETTINGS_FILE="${CLAUDE_DIR}/settings.json"

# Rules that grant reach. A path here is the whole meaning of the rule, so a match is a fact
# about the configuration rather than a judgement about a command.
GRANT_STRINGS='[ (.permissions? | objects | .allow? | arrays | .[]),
                 (.permissions? | objects | .additionalDirectories? | arrays | .[]) ]
               | .[] | strings'

# Every string the configuration will run or auto-approve, paired with its location. Rules in
# deny and ask are controls rather than grants, so they are deleted by position first. Derived
# from the document rather than an enumerated field list, which is what kept missing fields.
INVENTORY='[ (if type == "object" then del(.permissions?.deny?, .permissions?.ask?) else . end)
             | paths(strings) as $p
             | select(($p | last | tostring) as $k
                      | ($k | IN("type", "matcher", "$schema")) | not)
             | [($p | map(tostring) | join(".")), getpath($p)] ]
           | sort | .[] | @tsv'


if [ -f "${SETTINGS_FILE}" ]; then
    PERM_ISSUES=0
    PERM_SKIPPED=0

    # Whole-file checks. These forms are a defect in any array, or are top-level keys, so
    # they do not need to know which array a rule sits in.
    # Raw-text fallback for the no-jq path. jq repeats both below, where escapes are
    # decoded, so these are gated off to avoid reporting the same key twice.
    if ! command -v jq >/dev/null 2>&1 &&
        grep -qE '"(autoApprovedTools|autoApproved)"' "${SETTINGS_FILE}" 2>/dev/null; then
        echo "  ❌ CRITICAL: Unread permission key"
        echo "     File: ${SETTINGS_FILE}"
        echo "     Issue: Claude Code reads permissions.allow/deny/ask, not autoApprovedTools."
        echo "            The file looks configured but has no effective rules."
        echo ""
        PERM_ISSUES=1
    fi

    if ! command -v jq >/dev/null 2>&1 &&
        grep -qE '"defaultMode"[[:space:]]*:[[:space:]]*"bypassPermissions"' "${SETTINGS_FILE}" 2>/dev/null; then
        echo "  ❌ CRITICAL: permissions.defaultMode is bypassPermissions"
        echo "     File: ${SETTINGS_FILE}"
        echo "     Issue: every tool call runs unprompted, which is broader than any single rule"
        echo ""
        PERM_ISSUES=1
    fi

    # Whole-file keys. They do not depend on the shape of any rule array, so they run
    # outside the allow-scoped gate: a malformed allow must not drop them.
    if command -v jq >/dev/null 2>&1 && jq -e '(.permissions?.defaultMode? // "") == "bypassPermissions"' \
        "${SETTINGS_FILE}" >/dev/null 2>&1; then
        echo "  ❌ CRITICAL: permissions.defaultMode is bypassPermissions"
        echo "     File: ${SETTINGS_FILE}"
        echo "     Issue: every tool call runs unprompted, which is broader than any single rule"
        echo ""
        PERM_ISSUES=1
    fi

    if command -v jq >/dev/null 2>&1 && jq -e '[paths | last | strings] | any(. == "autoApprovedTools" or . == "autoApproved")' \
        "${SETTINGS_FILE}" >/dev/null 2>&1; then
        echo "  ❌ CRITICAL: Unread permission key"
        echo "     File: ${SETTINGS_FILE}"
        echo "     Issue: Claude Code reads permissions.allow/deny/ask, not autoApprovedTools."
        echo ""
        PERM_ISSUES=1
    fi


    # A filesystem-wide, bare, rule-form or sensitive-path grant is a defect only where it
    # grants. Telling that from deny needs the array the rule sits in, so the four share one
    # gate and are skipped together.
    if ! command -v jq >/dev/null 2>&1; then
        echo "  ⚠️  SKIPPED: filesystem-wide, bare-rule, rule-form and sensitive-path checks need jq to tell allow from deny"
        echo ""
        CHECKS_SKIPPED=$((CHECKS_SKIPPED + 4))
        PERM_SKIPPED=1
    elif ! jq -e 'type == "object"' "${SETTINGS_FILE}" >/dev/null 2>&1; then
        echo "  ❌ CRITICAL: jq cannot read settings.json as a JSON object, so these checks could not run"
        echo "     File: ${SETTINGS_FILE}"
        echo "  ⚠️  SKIPPED: filesystem-wide, bare-rule, rule-form and sensitive-path checks need a settings.json that parses"
        echo ""
        PERM_ISSUES=1
        CHECKS_SKIPPED=$((CHECKS_SKIPPED + 4))
        PERM_SKIPPED=1
    elif ! jq -e '[(.permissions.allow // [])[]] | all(type == "string")' \
        "${SETTINGS_FILE}" >/dev/null 2>&1; then
        # A non-string rule also makes every test() below exit with an error that is
        # indistinguishable from no-match once stderr is discarded.
        echo "  ❌ CRITICAL: a permissions.allow rule is not a string, so Claude Code cannot read it"
        echo "     File: ${SETTINGS_FILE}"
        echo "  ⚠️  SKIPPED: filesystem-wide, bare-rule, rule-form and sensitive-path checks need string rules"
        echo ""
        PERM_ISSUES=1
        CHECKS_SKIPPED=$((CHECKS_SKIPPED + 4))
        PERM_SKIPPED=1
    else
        # The colon form fails open in either array: in allow it grants nothing, and in deny it
        # is a restriction that never applies, so it is reported wherever it sits. Scoped to the
        # rule arrays, since a colon inside a command or env value is not a rule.
        if jq -e '(.permissions? | objects | (.allow?, .deny?, .ask?) | arrays | .[] | strings
                   | select(test("^(Bash|Read|Write|Edit|WebFetch|WebSearch|Glob|Grep|Task|NotebookEdit):")))' \
            "${SETTINGS_FILE}" >/dev/null 2>&1; then
            echo "  ❌ CRITICAL: Unread permission rule form"
            echo "     File: ${SETTINGS_FILE}"
            echo "     Issue: a colon-separated \"Tool:specifier\" rule is not read. Use Tool(specifier)."
            echo ""
            PERM_ISSUES=1
        fi

        if jq -e '(.permissions.allow // [])[] | select(test("^(Read|Write|Edit)\\(//\\*\\*\\)$"))' \
            "${SETTINGS_FILE}" >/dev/null 2>&1; then
            echo "  ❌ CRITICAL: Filesystem-wide permission rule in permissions.allow"
            echo "     File: ${SETTINGS_FILE}"
            echo "     Issue: Read(//**), Write(//**), or Edit(//**) covers the whole filesystem"
            echo ""
            PERM_ISSUES=1
        fi

        if jq -e '(.permissions.allow // [])[] | select(test("^(Bash|Read|Write|Edit|WebFetch|WebSearch|Glob|Grep|Task|NotebookEdit)$"))' \
            "${SETTINGS_FILE}" >/dev/null 2>&1; then
            echo "  ❌ CRITICAL: Bare tool rule in permissions.allow"
            echo "     File: ${SETTINGS_FILE}"
            echo "     Issue: a bare rule such as \"Bash\" matches every use of the tool"
            echo ""
            PERM_ISSUES=1
        fi

        # Grant arrays only. A command that merely mentions a path is a judgement call, and
        # Check 4 lists it for a reviewer rather than guessing.
        SENSITIVE_PATHS=(".ssh" ".aws" ".gnupg" "/etc" "id_rsa" "credentials")
        for path in "${SENSITIVE_PATHS[@]}"; do
            if jq -e --arg p "$path" "${GRANT_STRINGS} | select(contains(\$p))" \
                "${SETTINGS_FILE}" >/dev/null 2>&1; then
                echo "  ❌ CRITICAL: a grant references a sensitive path: $path"
                echo "     File: ${SETTINGS_FILE}"
                echo "     Review manually to ensure appropriate scoping"
                echo ""
                PERM_ISSUES=1
            fi
        done
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
    # A determinate answer, not a check that could not run: no file means no rules in force
    # from this directory. Rules from elsewhere are outside what this scan sees.
    echo "  ℹ️  No settings.json at ${CLAUDE_DIR}, so no rules are set here"
fi
echo ""

# ============================================================================
# Check 4: What this configuration runs
# ============================================================================
echo "[4/4] Listing strings this configuration runs or auto-approves..."

# This check does not classify. Nine rounds of pattern-matching on shell strings traded a
# false negative for a false positive every time, so it reports what will run and leaves the
# judgement to the reviewer, who has the context a regex does not.
if [ -f "${SETTINGS_FILE}" ]; then
    if ! command -v jq >/dev/null 2>&1; then
        echo "  ⚠️  SKIPPED: the inventory needs jq to read the file"
        echo ""
        CHECKS_SKIPPED=$((CHECKS_SKIPPED + 1))
    elif ! jq -e 'type == "object"' "${SETTINGS_FILE}" >/dev/null 2>&1; then
        echo "  ⚠️  SKIPPED: the inventory needs a settings.json that parses"
        echo ""
        CHECKS_SKIPPED=$((CHECKS_SKIPPED + 1))
    else
        INVENTORY_OUT=$(jq -r "${INVENTORY}" "${SETTINGS_FILE}" 2>/dev/null || true)
        if [ -z "${INVENTORY_OUT}" ]; then
            echo "  ℹ️  Nothing is granted or executed by this file"
        else
            echo "  Review each of these. Nothing below is a finding on its own:"
            echo ""
            printf '%s\n' "${INVENTORY_OUT}" | while IFS=$'\t' read -r loc val; do
                printf '     %s\n       %s\n' "$loc" "$val"
            done
            echo ""
            echo "     Worth a closer look:"
            echo "     - a fetch whose output reaches an interpreter (curl or wget into sh, eval,"
            echo "       or sh -c around a substitution)"
            echo "     - a destructive command with no guard (rm -rf, dd, mkfs, git push --force)"
            echo "     - a read of credentials (~/.ssh, ~/.aws, .env, printenv, the keychain)"
            echo "     - anything widening permissions (chmod 777, chmod 666)"
            echo "     - egress carrying repository, prompt, or environment content"
            echo ""
        fi
    fi
else
    # A determinate answer, not a check that could not run: no file means no rules in force
    # from this directory. Rules from elsewhere are outside what this scan sees.
    echo "  ℹ️  No settings.json at ${CLAUDE_DIR}, so no rules are set here"
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
    echo "✅ The deterministic checks passed"
    echo ""
    echo "  - No committed local settings"
    echo "  - No hardcoded secrets detected"
    echo "  - Permissions appropriately scoped"
    echo ""
    echo "This is not a verdict on what the configuration runs. Check 4 lists those"
    echo "strings; reading them is the reviewer's job, not this script's."
    echo ""
    exit 0
else
    echo "❌ Found ${ISSUES_FOUND} critical security issue(s)"
    if [ $CHECKS_SKIPPED -ne 0 ]; then
        echo "   ${CHECKS_SKIPPED} further check(s) could not run, so this list is not complete."
    fi
    echo ""
    echo "Review the issues above and remediate before approval."
    echo ""
    echo "Common fixes:"
    echo "  - Remove settings.local.json from git: git rm --cached .claude/settings.local.json"
    echo "  - Replace hardcoded secrets with environment variables"
    echo "  - Scope permissions to project directory only"
    echo "  - Replace an unread rule form with Tool(specifier) under permissions.allow"
    echo ""
    echo "For detailed remediation guidance, see:"
    echo "  ${CLAUDE_DIR}/skills/reviewing-claude-config/reference/security-patterns.md"
    echo ""
    exit 1
fi
