#!/usr/bin/env bash
# daily-recap.test.sh
# Tests for date-utils.sh, gather-gh-events.sh, and find-sessions.sh.
#
# Usage: ./daily-recap.test.sh
#
# Plain bash with no test framework, and it runs on both GNU and BSD date. Every case
# works in a throwaway directory: session logs are fixtures written under a temporary
# config directory, and `gh` is a stub on PATH, so no real session data is read and the
# GitHub API is never called. Requires jq, like the scripts themselves.

# cspell:ignore Kolkata

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATHER="${SCRIPT_DIR}/gather-gh-events.sh"
FIND="${SCRIPT_DIR}/find-sessions.sh"

command -v jq >/dev/null 2>&1 || {
  echo "Error: jq is required to run these tests"
  exit 1
}

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "${WORK_DIR}"' EXIT

PASSED=0
FAILED=0

pass() {
  echo "  ✅ $1"
  PASSED=$((PASSED + 1))
}

fail() {
  echo "  ❌ $1"
  FAILED=$((FAILED + 1))
}

# assert_eq <case> <expected> <actual>
assert_eq() {
  if [[ "$2" == "$3" ]]; then
    pass "$1"
  else
    fail "$1"
    echo "     expected: $2"
    echo "     got:      $3"
  fi
}

# assert_contains <case> <needle> <haystack>
assert_contains() {
  if grep -qF -- "$2" <<<"$3"; then
    pass "$1"
  else
    fail "$1"
    echo "     expected to contain: $2"
    echo "     got:"
    while IFS= read -r line; do echo "       ${line}"; done <<<"$3"
  fi
}

# Runs a helper from date-utils.sh in a subshell, since the file is sourced, not executed.
date_utils() {
  (
    # shellcheck source=SCRIPTDIR/date-utils.sh
    source "${SCRIPT_DIR}/date-utils.sh"
    "$@"
  )
}

# ---------------------------------------------------------------------------
# A stub `gh` that answers the two calls gather-gh-events.sh makes: the login lookup
# and an empty events feed. Each call is logged so cases can assert that input
# validation fails before anything would reach GitHub. GH_STUB_FAIL makes every call
# fail, as an unauthenticated `gh` does.
# ---------------------------------------------------------------------------
STUB_BIN="${WORK_DIR}/stub-bin"
GH_LOG="${WORK_DIR}/gh-calls.log"
mkdir -p "${STUB_BIN}"
cat >"${STUB_BIN}/gh" <<'EOF'
#!/bin/sh
echo "$*" >>"${GH_LOG}"
[ -n "${GH_STUB_FAIL:-}" ] && exit 1
case "$2" in
  user) echo "recap-tester" ;;
  users/*) echo "[]" ;;
  *) exit 1 ;;
esac
EOF
chmod +x "${STUB_BIN}/gh"

OUT=""
ERR=""
STATUS=0

# gather [VAR=value ...] -- [args...]
# Runs gather-gh-events.sh with the stub gh first on PATH and the given environment.
# Sets OUT, ERR, and STATUS.
gather() {
  local env_args=()
  while [[ $# -gt 0 && "$1" != "--" ]]; do
    env_args+=("$1")
    shift
  done
  shift
  : >"${GH_LOG}"
  OUT="$(env PATH="${STUB_BIN}:${PATH}" GH_LOG="${GH_LOG}" ${env_args[@]+"${env_args[@]}"} \
    bash "${GATHER}" "$@" 2>"${WORK_DIR}/stderr")"
  STATUS=$?
  ERR="$(cat "${WORK_DIR}/stderr")"
}

# window_of <case-prefix> <expected-start-utc> <expected-end-utc>
window_of() {
  assert_eq "$1: exits 0" 0 "${STATUS}"
  assert_eq "$1: start_utc" "$2" "$(jq -r .window.start_utc <<<"${OUT}")"
  assert_eq "$1: end_utc" "$3" "$(jq -r .window.end_utc <<<"${OUT}")"
}

echo "=== daily-recap script tests ==="
echo ""

# ---------------------------------------------------------------------------
# date-utils.sh helpers
# ---------------------------------------------------------------------------
echo "[1] date-utils.sh conversions"
assert_eq "utc_to_epoch parses an ISO timestamp" 1791889200 "$(date_utils utc_to_epoch 2026-10-13T11:00:00Z)"
assert_eq "epoch_fmt_utc formats it back" 2026-10-13T11:00:00Z "$(date_utils epoch_fmt_utc 1791889200 '%Y-%m-%dT%H:%M:%SZ')"
assert_eq "local_to_epoch honors TZ" 1791889200 "$(TZ=America/New_York date_utils local_to_epoch '2026-10-13 07:00:00')"
assert_eq "epoch_fmt honors TZ" "2026-10-13 07:00 -0400" "$(TZ=America/New_York date_utils epoch_fmt 1791889200 '%Y-%m-%d %H:%M %z')"
# 02:00 on 2026-03-08 is skipped in New York. Both date flavors read it as 03:00 EDT.
assert_eq "local_to_epoch reads a skipped time forward" 1772953200 "$(TZ=America/New_York date_utils local_to_epoch '2026-03-08 02:00:00')"
echo ""

echo "[2] date-utils.sh add_days"
assert_eq "next day" 2026-10-14 "$(date_utils add_days 2026-10-13 1)"
assert_eq "across a month end" 2026-02-28 "$(date_utils add_days 2026-03-01 -1)"
assert_eq "into a leap day" 2028-02-29 "$(date_utils add_days 2028-03-01 -1)"
assert_eq "across a year end" 2027-01-01 "$(date_utils add_days 2026-12-31 1)"
assert_eq "into spring forward" 2026-03-08 "$(TZ=America/New_York date_utils add_days 2026-03-07 1)"
assert_eq "out of spring forward" 2026-03-09 "$(TZ=America/New_York date_utils add_days 2026-03-08 1)"
assert_eq "back across fall back" 2026-10-31 "$(TZ=America/New_York date_utils add_days 2026-11-01 -1)"
assert_eq "two days over fall back" 2026-11-02 "$(TZ=America/New_York date_utils add_days 2026-10-31 2)"
echo ""

echo "[3] date-utils.sh is_valid_date"
for d in 2026-10-13 2028-02-29 2026-12-31; do
  if date_utils is_valid_date "$d"; then pass "accepts ${d}"; else fail "accepts ${d}"; fi
done
for d in 2026-02-29 2026-02-30 2026-04-31 2026-13-01 10/13/2026 2026-1-5 "2026-10-13 " "" yesterday; do
  if date_utils is_valid_date "$d"; then fail "rejects '${d}'"; else pass "rejects '${d}'"; fi
done
echo ""

# ---------------------------------------------------------------------------
# gather-gh-events.sh window computation. The window runs from the cutoff hour on the
# given date to the cutoff hour on the next date, in local time.
# ---------------------------------------------------------------------------
echo "[4] window for an ordinary date"
gather TZ=America/New_York -- 2026-10-13
window_of "2026-10-13 New York" 2026-10-13T11:00:00Z 2026-10-14T11:00:00Z
assert_eq "local start keeps the offset" 2026-10-13T07:00:00-0400 "$(jq -r .window.start_local <<<"${OUT}")"
assert_eq "timezone label" EDT "$(jq -r .window.timezone <<<"${OUT}")"
assert_eq "default cutoff hour is 7" 7 "$(jq -r .window.cutoff_hour <<<"${OUT}")"
assert_eq "login comes from gh" recap-tester "$(jq -r .login <<<"${OUT}")"
assert_eq "empty feed gives no events" 0 "$(jq -r .event_count <<<"${OUT}")"
assert_contains "window line goes to stderr" "# Window: 2026-10-13T11:00:00Z -> 2026-10-14T11:00:00Z (07:00 EDT boundary)" "${ERR}"
echo ""

echo "[5] windows around DST transitions in New York"
gather TZ=America/New_York -- 2026-03-08
window_of "2026-03-08 (spring forward day)" 2026-03-08T11:00:00Z 2026-03-09T11:00:00Z
gather TZ=America/New_York -- 2026-03-07
window_of "2026-03-07 (23-hour window)" 2026-03-07T12:00:00Z 2026-03-08T11:00:00Z
gather TZ=America/New_York -- 2026-11-01
window_of "2026-11-01 (fall back day)" 2026-11-01T12:00:00Z 2026-11-02T12:00:00Z
gather TZ=America/New_York -- 2026-10-31
window_of "2026-10-31 (25-hour window)" 2026-10-31T11:00:00Z 2026-11-01T12:00:00Z
# A 02:00 cutoff falls in the skipped hour on 2026-03-08 and moves to 03:00 EDT.
gather TZ=America/New_York DAILY_RECAP_CUTOFF_HOUR=2 -- 2026-03-08
window_of "cutoff in the skipped hour, start" 2026-03-08T07:00:00Z 2026-03-09T06:00:00Z
gather TZ=America/New_York DAILY_RECAP_CUTOFF_HOUR=2 -- 2026-03-07
window_of "cutoff in the skipped hour, end" 2026-03-07T07:00:00Z 2026-03-08T07:00:00Z
echo ""

echo "[6] non-default DAILY_RECAP_CUTOFF_HOUR"
gather TZ=America/New_York DAILY_RECAP_CUTOFF_HOUR=0 -- 2026-10-13
window_of "midnight cutoff" 2026-10-13T04:00:00Z 2026-10-14T04:00:00Z
gather TZ=America/New_York DAILY_RECAP_CUTOFF_HOUR=09 -- 2026-10-13
window_of "leading zero is decimal, not octal" 2026-10-13T13:00:00Z 2026-10-14T13:00:00Z
assert_eq "cutoff hour reported as a number" 9 "$(jq -r .window.cutoff_hour <<<"${OUT}")"
gather TZ=America/New_York DAILY_RECAP_CUTOFF_HOUR=23 -- 2026-10-13
window_of "late cutoff" 2026-10-14T03:00:00Z 2026-10-15T03:00:00Z
echo ""

echo "[7] other timezones"
gather TZ=UTC -- 2026-10-13
window_of "UTC" 2026-10-13T07:00:00Z 2026-10-14T07:00:00Z
gather TZ=Asia/Kolkata -- 2026-10-13
window_of "half-hour offset" 2026-10-13T01:30:00Z 2026-10-14T01:30:00Z
gather TZ=Australia/Sydney -- 2026-10-13
window_of "southern hemisphere summer time" 2026-10-12T20:00:00Z 2026-10-13T20:00:00Z
echo ""

echo "[8] rejected inputs fail before calling GitHub"
for cutoff in 7am 24 -1 " 7"; do
  gather TZ=America/New_York "DAILY_RECAP_CUTOFF_HOUR=${cutoff}" -- 2026-10-13
  assert_eq "cutoff '${cutoff}': exits 1" 1 "${STATUS}"
  assert_contains "cutoff '${cutoff}': explains the range" "DAILY_RECAP_CUTOFF_HOUR must be a whole hour from 0 to 23 (got '${cutoff}')" "${ERR}"
  assert_eq "cutoff '${cutoff}': no gh call" "" "$(cat "${GH_LOG}")"
done
for d in 2026-02-30 10/13/2026 2026-13-01 2026-10-1; do
  gather TZ=America/New_York -- "$d"
  assert_eq "date '${d}': exits 1" 1 "${STATUS}"
  assert_contains "date '${d}': explains the form" "date must be a real calendar date in YYYY-MM-DD form (got '${d}')" "${ERR}"
  assert_eq "date '${d}': nothing on stdout" "" "${OUT}"
  assert_eq "date '${d}': no gh call" "" "$(cat "${GH_LOG}")"
done
echo ""

echo "[9] gh missing or signed out"
# A PATH holding only the tools the script needs before its dependency check, so no
# installed gh can be found.
NO_GH_BIN="${WORK_DIR}/no-gh-bin"
mkdir -p "${NO_GH_BIN}"
for tool in jq dirname date; do
  ln -s "$(command -v "${tool}")" "${NO_GH_BIN}/${tool}"
done
OUT="$(env PATH="${NO_GH_BIN}" "${BASH}" "${GATHER}" 2026-10-13 2>"${WORK_DIR}/stderr")"
STATUS=$?
ERR="$(cat "${WORK_DIR}/stderr")"
assert_eq "without gh: exits 1" 1 "${STATUS}"
assert_contains "without gh: names the missing tool" "'gh' is required but not installed" "${ERR}"
assert_eq "without gh: nothing on stdout" "" "${OUT}"
gather TZ=America/New_York GH_STUB_FAIL=1 -- 2026-10-13
assert_eq "signed out: exits 1" 1 "${STATUS}"
assert_contains "signed out: points at gh auth login" "run 'gh auth login' and try again" "${ERR}"
assert_eq "signed out: stops after the login lookup" "api user --jq .login" "$(cat "${GH_LOG}")"
echo ""

# ---------------------------------------------------------------------------
# find-sessions.sh. The window under test is 2026-01-05T11:00:00Z to
# 2026-01-06T11:00:00Z. HOME is a path that does not exist, so its project slug is not
# mistaken for a temp directory; the logs live under CLAUDE_CONFIG_DIR.
# ---------------------------------------------------------------------------
START=2026-01-05T11:00:00Z
END=2026-01-06T11:00:00Z
FAKE_HOME=/Users/recap-tester
CONFIG_DIR="${WORK_DIR}/claude"
PROJECTS="${CONFIG_DIR}/projects"
APP="${PROJECTS}/-Users-recap-tester-dev-app"
mkdir -p "${APP}"

# session_file <project-dir> <session> <first-timestamp>
# Writes a minimal in-window session so the skip rules have something to skip.
session_file() {
  mkdir -p "$1"
  printf '{"type":"user","timestamp":"%s","cwd":"/x","message":{"role":"user","content":"hello"}}\n' "$3" >"$1/$2.jsonl"
}

# The main fixture: out-of-window entries on both sides, boundary entries with
# milliseconds, harness-injected user entries mixed with real prompts, a tool call, and
# a half-written final line.
cat >"${APP}/s-window.jsonl" <<'EOF'
{"type":"user","timestamp":"2026-01-05T10:59:59.999Z","cwd":"/Users/recap-tester/dev/app","gitBranch":"old-branch","message":{"role":"user","content":"Prompt from before the window"}}
{"type":"user","timestamp":"2026-01-05T11:00:00.250Z","cwd":"/Users/recap-tester/dev/app","gitBranch":"main","message":{"role":"user","content":"Fix the flaky login test"}}
{"type":"user","timestamp":"2026-01-05T12:00:00.000Z","gitBranch":"main","message":{"role":"user","content":"<command-name>/clear</command-name>"}}
{"type":"user","timestamp":"2026-01-05T12:01:00.000Z","gitBranch":"main","message":{"role":"user","content":"<local-command-stdout>cleared</local-command-stdout>"}}
{"type":"user","timestamp":"2026-01-05T12:02:00.000Z","gitBranch":"main","message":{"role":"user","content":"<system-reminder>Background note</system-reminder>"}}
{"type":"user","timestamp":"2026-01-05T12:03:00.000Z","gitBranch":"main","message":{"role":"user","content":"  <task-notification>Task finished</task-notification>"}}
{"type":"user","timestamp":"2026-01-05T12:04:00.000Z","gitBranch":"main","message":{"role":"user","content":"<agent-message from=\"helper\">status update</agent-message>"}}
{"type":"user","timestamp":"2026-01-05T12:05:00.000Z","gitBranch":"main","message":{"role":"user","content":"Another Claude session sent a message: ping"}}
{"type":"user","timestamp":"2026-01-05T12:06:00.000Z","gitBranch":"main","isMeta":true,"message":{"role":"user","content":"Caveat: injected meta entry"}}
{"type":"user","timestamp":"2026-01-05T12:07:00.000Z","gitBranch":"main","isSidechain":true,"message":{"role":"user","content":"Subagent task prompt"}}
{"type":"user","timestamp":"2026-01-05T12:08:00.000Z","gitBranch":"main","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":"ok"}]}}
{"type":"user","timestamp":"2026-01-05T12:09:00.000Z","gitBranch":"main","message":{"role":"user","content":"   "}}
{"type":"user","timestamp":"2026-01-05T13:00:00.000Z","gitBranch":"feature/sync","message":{"role":"user","content":[{"type":"text","text":"Refactor the sync service"},{"type":"image"}]}}
{"type":"assistant","timestamp":"2026-01-05T13:01:00.000Z","gitBranch":"feature/sync","message":{"role":"assistant","content":[{"type":"text","text":"On it."},{"type":"tool_use","id":"t2","name":"Edit","input":{"file_path":"/Users/recap-tester/dev/app/sync.ts"}},{"type":"tool_use","id":"t3","name":"Bash","input":{"command":"npm test"}}]}}
{"type":"user","timestamp":"2026-01-05T14:00:00.000Z","gitBranch":"HEAD","message":{"role":"user","content":"Explain what a <system-reminder> tag is"}}
{"type":"user","timestamp":"2026-01-06T10:59:59.900Z","gitBranch":"main","message":{"role":"user","content":"Last prompt of the workday"}}
{"type":"user","timestamp":"2026-01-06T11:00:00.000Z","gitBranch":"main","message":{"role":"user","content":"Prompt at the window end"}}
{"type":"user","timestamp":"2026-01-06T11:00:00.500Z","gitBranch":"main","message":{"role":"user","content":"Prompt just after the window end"}}
{"type":"user","timestamp":"2026-01-06T12:00:00.000Z","gitBranch":"main","message":{"role":"user","content":"Prompt from the next day"}}
EOF
# A last line cut off mid-string with no newline, as a live session can leave it.
printf '%s' '{"type":"user","timestamp":"2026-01-06T10:30:00.000Z","message":{"role":"user","content":"half-writ' >>"${APP}/s-window.jsonl"

cat >"${APP}/s-outside.jsonl" <<'EOF'
{"type":"user","timestamp":"2026-01-04T09:00:00.000Z","message":{"role":"user","content":"Two days early"}}
{"type":"user","timestamp":"2026-01-07T09:00:00.000Z","message":{"role":"user","content":"A day late"}}
EOF

session_file "${PROJECTS}/-Users-recap-tester" s-home 2026-01-05T15:00:00.000Z
session_file "${PROJECTS}/-tmp-scratch" s-tmp 2026-01-05T15:00:00.000Z
session_file "${PROJECTS}/-private-tmp-scratch" s-private-tmp 2026-01-05T15:00:00.000Z
session_file "${PROJECTS}/-var-folders-ab-cd1234-T-tmp-x" s-var-folders 2026-01-05T15:00:00.000Z
session_file "${PROJECTS}/-private-var-folders-ab-cd1234-T-tmp-x" s-private-var-folders 2026-01-05T15:00:00.000Z

# find_sessions [args...] with the fixture environment. Sets OUT, ERR, and STATUS.
find_sessions() {
  OUT="$(env HOME="${FAKE_HOME}" CLAUDE_CONFIG_DIR="${CONFIG_DIR}" \
    bash "${FIND}" "$@" 2>"${WORK_DIR}/stderr")"
  STATUS=$?
  ERR="$(cat "${WORK_DIR}/stderr")"
}

sessions_found() {
  jq -r '[.[].session] | join(",")' <<<"${OUT}"
}

echo "[10] find-sessions.sh session selection"
find_sessions "${START}" "${END}"
assert_eq "exits 0" 0 "${STATUS}"
assert_eq "keeps only the project session with in-window activity" s-window "$(sessions_found)"
assert_eq "no session reported unreadable" "" "${ERR}"
find_sessions "${START}" "${END}" --include-home
assert_eq "--include-home adds the home session, ordered by first activity" s-window,s-home "$(sessions_found)"
assert_eq "home digest names its project" -Users-recap-tester "$(jq -r '.[1].project' <<<"${OUT}")"
echo ""

echo "[11] find-sessions.sh window boundaries and the half-written line"
find_sessions "${START}" "${END}"
DIGEST="$(jq '.[0]' <<<"${OUT}")"
assert_eq "first activity is the entry 250 ms into the window" 2026-01-05T11:00:00.250Z "$(jq -r .first_activity <<<"${DIGEST}")"
assert_eq "last activity is the final in-window entry" 2026-01-06T10:59:59.900Z "$(jq -r .last_activity <<<"${DIGEST}")"
assert_eq "counts in-window entries only, without the cut-off line" 15 "$(jq -r .entries_in_window <<<"${DIGEST}")"
assert_eq "cwd comes from the first in-window entry" /Users/recap-tester/dev/app "$(jq -r .cwd <<<"${DIGEST}")"
assert_eq "branches skip HEAD and out-of-window entries" feature/sync,main "$(jq -r '.branches | join(",")' <<<"${DIGEST}")"
assert_eq "path points at the session log" "${APP}/s-window.jsonl" "$(jq -r .path <<<"${DIGEST}")"
echo ""

echo "[12] find-sessions.sh prompt filter"
assert_eq "keeps only real prompts" 4 "$(jq -r .prompt_count <<<"${DIGEST}")"
assert_eq "real prompts in order" \
  "Fix the flaky login test|Refactor the sync service|Explain what a <system-reminder> tag is|Last prompt of the workday" \
  "$(jq -r '.prompts | join("|")' <<<"${DIGEST}")"
for injected in "<command-name>" "<local-command-stdout>" "<system-reminder>Background" "<task-notification>" "<agent-message" "Another Claude session" "Caveat:" "Subagent task"; do
  if grep -qF -- "${injected}" <<<"$(jq -r '.prompts[]' <<<"${DIGEST}")"; then
    fail "drops '${injected}' entries"
  else
    pass "drops '${injected}' entries"
  fi
done
assert_eq "counts tool calls" 2 "$(jq -r .tool_calls <<<"${DIGEST}")"
assert_eq "lists edited files" /Users/recap-tester/dev/app/sync.ts "$(jq -r '.files_edited | join(",")' <<<"${DIGEST}")"
echo ""

echo "[13] find-sessions.sh default log location"
DEFAULT_HOME="${WORK_DIR}/home"
session_file "${DEFAULT_HOME}/.claude/projects/-Users-someone-dev-api" s-default 2026-01-05T15:00:00.000Z
OUT="$(env -u CLAUDE_CONFIG_DIR HOME="${DEFAULT_HOME}" bash "${FIND}" "${START}" "${END}" 2>/dev/null)"
assert_eq "reads ~/.claude/projects when CLAUDE_CONFIG_DIR is unset" s-default "$(sessions_found)"
echo ""

echo "[14] find-sessions.sh argument checks"
find_sessions "${START}"
assert_eq "one timestamp: exits 2" 2 "${STATUS}"
assert_contains "one timestamp: prints usage" "Usage: find-sessions.sh" "${ERR}"
find_sessions "${START}" "${END}" --everything
assert_eq "unknown flag: exits 2" 2 "${STATUS}"
find_sessions 2026-01-05 "${END}"
assert_eq "date without time: exits 1" 1 "${STATUS}"
assert_contains "date without time: shows the expected form" "timestamps must look like 2026-10-13T11:00:00Z" "${ERR}"
find_sessions "${END}" "${START}"
assert_eq "reversed window: exits 1" 1 "${STATUS}"
OUT="$(env HOME="${FAKE_HOME}" CLAUDE_CONFIG_DIR="${WORK_DIR}/missing" bash "${FIND}" "${START}" "${END}" 2>&1)"
assert_contains "missing log directory: says where it looked" "no Claude Code session logs found at ${WORK_DIR}/missing/projects" "${OUT}"
echo ""

echo "=== ${PASSED} passed, ${FAILED} failed ==="
[[ "${FAILED}" -eq 0 ]]
