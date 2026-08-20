#!/bin/bash
# security-scan.test.sh
# Regression tests for security-scan.sh.
#
# Usage: ./security-scan.test.sh
#
# Each case builds a throwaway .claude directory, runs the scanner against it, and
# asserts on the output and exit status. The cases exist because every one of them
# reported a pass before the behavior was fixed: a scanner that vouches for a check
# it never ran is worse than one that errors.
#
# Credential fixtures are assembled at run time rather than written literally, so
# this file holds no string that a secret scanner should flag. The scanner's own
# exclusion list stays short as a result.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCAN="${SCRIPT_DIR}/security-scan.sh"

if [ ! -x "${SCAN}" ]; then
    echo "Error: ${SCAN} is missing or not executable"
    exit 1
fi

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "${WORK_DIR}"' EXIT

PASSED=0
FAILED=0

# Assembled so the literal never appears in this file.
OPENAI_KEY="sk-$(printf 'A%.0s' $(seq 1 36))"
GITHUB_TOKEN="ghp_$(printf 'B%.0s' $(seq 1 36))"

# fixture <name> — makes ${WORK_DIR}/<name>/.claude and echoes its path
fixture() {
    local dir="${WORK_DIR}/$1/.claude"
    mkdir -p "${dir}"
    echo "${dir}"
}

# git_fixture <dir> — turns the parent of <dir> into a repository with one commit
git_fixture() {
    (
        cd "$1/.." || exit 1
        git init -q .
        git add -A -f >/dev/null 2>&1
        git -c user.email=t@t -c user.name=t commit -qm fixture >/dev/null 2>&1
    )
}

# assert <case> <expect|reject> <pattern> <output>
assert() {
    local name="$1" mode="$2" pattern="$3" output="$4"
    local hit=0
    grep -qF -- "${pattern}" <<< "${output}" && hit=1

    if { [ "${mode}" = "expect" ] && [ "${hit}" -eq 1 ]; } ||
       { [ "${mode}" = "reject" ] && [ "${hit}" -eq 0 ]; }; then
        echo "  ✅ ${name}"
        PASSED=$((PASSED + 1))
    else
        echo "  ❌ ${name}"
        echo "     ${mode}ed: ${pattern}"
        echo "     got:"
        sed 's/^/       /' <<< "${output}"
        FAILED=$((FAILED + 1))
    fi
}

# assert_status <case> <expected> <actual>
assert_status() {
    if [ "$2" -eq "$3" ]; then
        echo "  ✅ $1"
        PASSED=$((PASSED + 1))
    else
        echo "  ❌ $1 (expected exit $2, got $3)"
        FAILED=$((FAILED + 1))
    fi
}

echo "=== security-scan.sh regression tests ==="
echo ""

# ---------------------------------------------------------------------------
# Check 1 must report a committed settings.local.json even when git's output is
# long enough that grep exits first. Piping git into `grep -q` under `pipefail`
# lost the match: grep exited, git took SIGPIPE with 141, and pipefail surfaced
# that as pipeline failure. The fixture name sorts early on purpose.
# ---------------------------------------------------------------------------
echo "[1] committed settings.local.json, large repository"
CLAUDE_DIR="$(fixture large-repo)"
printf 'x\n' > "${CLAUDE_DIR}/aaa-settings.local.json"
(cd "${CLAUDE_DIR}/.." && seq 1 20000 | sed 's|^|filler-|' | xargs -n1 touch)
git_fixture "${CLAUDE_DIR}"
OUT="$(bash "${SCAN}" "${CLAUDE_DIR}" 2>&1)"
assert "detects the committed file" expect "CRITICAL: settings.local.json is committed to git" "${OUT}"
assert "does not claim it is absent" reject "OK: settings.local.json not in git" "${OUT}"
echo ""

# ---------------------------------------------------------------------------
# Outside a git repository the check cannot run. It used to report a pass,
# because git ran against whatever repository the shell was in and its error
# was discarded.
# ---------------------------------------------------------------------------
echo "[2] target outside any git repository"
CLAUDE_DIR="$(fixture no-repo)"
OUT="$(bash "${SCAN}" "${CLAUDE_DIR}" 2>&1)"
assert "records the check as skipped" expect "SKIPPED: ${CLAUDE_DIR} is not inside a git repository" "${OUT}"
assert "does not vouch for local settings" reject "OK: settings.local.json not in git" "${OUT}"
assert "verdict reports the run as incomplete" expect "INCOMPLETE" "${OUT}"
echo ""

# ---------------------------------------------------------------------------
# An absent settings.json means checks 3 and 4 did not run. They used to print
# "(OK)" and the verdict counted them as passed.
# ---------------------------------------------------------------------------
echo "[3] no settings.json to inspect"
CLAUDE_DIR="$(fixture no-settings)"
git_fixture "${CLAUDE_DIR}"
OUT="$(bash "${SCAN}" "${CLAUDE_DIR}" 2>&1)"
STATUS=$?
assert "records the permission checks as skipped" expect "SKIPPED: no settings.json" "${OUT}"
assert "verdict reports the run as incomplete" expect "INCOMPLETE" "${OUT}"
assert "does not claim the checks passed" reject "The deterministic checks passed" "${OUT}"
echo ""

# ---------------------------------------------------------------------------
# Real credentials are reported wherever they sit in the scanned tree. Earlier
# filters matched bare substrings over grep's path:line output and discarded
# findings by path or by a placeholder fragment inside a real value.
# ---------------------------------------------------------------------------
echo "[4] real credentials in the scanned tree"
CLAUDE_DIR="$(fixture real-secrets)"
mkdir -p "${CLAUDE_DIR}/skills/demo/examples"
printf '%s\n' "${OPENAI_KEY}" > "${CLAUDE_DIR}/skills/demo/examples/config.json"
printf '{"token": "%s"}\n' "${GITHUB_TOKEN}" > "${CLAUDE_DIR}/settings.json"
OUT="$(bash "${SCAN}" "${CLAUDE_DIR}" 2>&1)"
assert "detects a key under an examples/ path" expect "CRITICAL: OpenAI API key pattern detected" "${OUT}"
assert "detects a token in settings.json" expect "CRITICAL: GitHub token pattern detected" "${OUT}"
echo ""

# ---------------------------------------------------------------------------
# The scanner must not report this skill's own labelled-bad fixtures, whether
# the target is given as a relative or an absolute path.
# ---------------------------------------------------------------------------
echo "[5] scanning this skill does not flag its own fixtures"
OUT="$(cd "${SCRIPT_DIR}/.." && bash "${SCAN}" . 2>&1)"
assert "no false positive (relative path)" reject "CRITICAL" "${OUT}"
OUT="$(bash "${SCAN}" "${SCRIPT_DIR}/.." 2>&1)"
assert "no false positive (absolute path)" reject "CRITICAL" "${OUT}"
echo ""

# ---------------------------------------------------------------------------
# A clean configuration reports every check as run, and exits 0.
# ---------------------------------------------------------------------------
echo "[6] clean configuration"
CLAUDE_DIR="$(fixture clean)"
printf '{"permissions": {"allow": ["Read(./src/**)"]}}\n' > "${CLAUDE_DIR}/settings.json"
git_fixture "${CLAUDE_DIR}"
OUT="$(bash "${SCAN}" "${CLAUDE_DIR}" 2>&1)"
STATUS=$?
assert "reports the checks passed" expect "The deterministic checks passed" "${OUT}"
assert "nothing recorded as skipped" reject "SKIPPED" "${OUT}"
assert_status "exits 0" 0 "${STATUS}"
echo ""

echo "=== ${PASSED} passed, ${FAILED} failed ==="
[ "${FAILED}" -eq 0 ]
