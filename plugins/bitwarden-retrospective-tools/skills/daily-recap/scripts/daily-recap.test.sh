#!/usr/bin/env bash
# daily-recap.test.sh
# Tests for date-utils.sh, gather-gh-events.sh, gather-atlassian.sh, gather-gh-search.sh,
# find-sessions.sh, and the template's CSP script hash.
#
# Usage: ./daily-recap.test.sh
#
# Plain bash with no test framework, and it runs on both GNU and BSD date. Every case
# works in a throwaway directory: session logs are fixtures written under a temporary
# config directory, and `gh` and `curl` are stubs on PATH, so no real session data is
# read and neither the GitHub nor the Atlassian API is ever called. Requires jq, like
# the scripts themselves.

# cspell:ignore Kolkata fromdate todate serverinfo issuekey nflu creds

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATHER="${SCRIPT_DIR}/gather-gh-events.sh"
GATHER_ATLASSIAN="${SCRIPT_DIR}/gather-atlassian.sh"
GATHER_SEARCH="${SCRIPT_DIR}/gather-gh-search.sh"
FIND="${SCRIPT_DIR}/find-sessions.sh"
TEMPLATE="${SCRIPT_DIR}/../assets/template.html"

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
# and the events feed, which is empty unless GH_STUB_FEED names a directory of
# page-<n>.json files. Each call is logged so cases can assert that input validation
# fails before anything would reach GitHub. GH_STUB_FAIL makes every call fail, as an
# unauthenticated `gh` does.
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
  users/*)
    page_file="${GH_STUB_FEED:-/nonexistent}/page-${2##*page=}.json"
    if [ -f "$page_file" ]; then cat "$page_file"; else echo "[]"; fi
    ;;
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
# A PATH holding only the tools the script needs to compute the window, so no installed
# gh can be found.
NO_GH_BIN="${WORK_DIR}/no-gh-bin"
mkdir -p "${NO_GH_BIN}"
for tool in jq dirname date; do
  ln -s "$(command -v "${tool}")" "${NO_GH_BIN}/${tool}"
done
OUT="$(env PATH="${NO_GH_BIN}" TZ=America/New_York "${BASH}" "${GATHER}" 2026-10-13 2>"${WORK_DIR}/stderr")"
STATUS=$?
ERR="$(cat "${WORK_DIR}/stderr")"
assert_eq "without gh: exits 1" 1 "${STATUS}"
assert_contains "without gh: names the missing tool" "'gh' is required but not installed" "${ERR}"
assert_eq "without gh: nothing on stdout" "" "${OUT}"
assert_contains "without gh: still prints the window" "# Window: 2026-10-13T11:00:00Z -> 2026-10-14T11:00:00Z" "${ERR}"
gather TZ=America/New_York GH_STUB_FAIL=1 -- 2026-10-13
assert_eq "signed out: exits 1" 1 "${STATUS}"
assert_contains "signed out: points at gh auth login" "run 'gh auth login' and try again" "${ERR}"
assert_contains "signed out: still prints the window" "# Window: 2026-10-13T11:00:00Z -> 2026-10-14T11:00:00Z" "${ERR}"
assert_eq "signed out: stops after the login lookup" "api user --jq .login" "$(cat "${GH_LOG}")"
echo ""

# ---------------------------------------------------------------------------
# Events feed paging. GitHub returns the feed in delivery order rather than by
# created_at, so an event with a long-past timestamp can sit anywhere in it, and a page
# can come back short mid-feed. The window under test is 2026-10-13T11:00:00Z to
# 2026-10-14T11:00:00Z.
# ---------------------------------------------------------------------------
FEED="${WORK_DIR}/feed"
mkdir -p "${FEED}"

# feed <events> <oldest-utc> [stray-utc]
# Writes <events> events an hour apart, newest first and ending at <oldest-utc>, as pages
# of 100. A stray timestamp replaces the 51st event, in the middle of page 1.
feed() {
  rm -f "${FEED}"/page-*.json
  jq -n --argjson n "$1" --arg oldest "$2" --arg stray "${3:-}" '
    [range(0; $n) as $i
      | {type: "PushEvent", repo: {name: "bitwarden/x"}, payload: {},
         created_at: ($oldest | fromdate + ($n - 1 - $i) * 3600 | todate)}]
    | if $stray != "" then .[50].created_at = $stray else . end' >"${FEED}/all.json"
  local p
  for p in 1 2 3; do
    jq ".[$(((p - 1) * 100)):$((p * 100))]" "${FEED}/all.json" >"${FEED}/page-${p}.json"
  done
}

echo "[10] events feed paging"
feed 300 2026-10-12T13:00:00Z 2026-09-23T13:09:38Z
jq 'del(.[0])' "${FEED}/page-2.json" >"${FEED}/short.json" && mv "${FEED}/short.json" "${FEED}/page-2.json"
gather TZ=America/New_York "GH_STUB_FEED=${FEED}" -- 2026-10-13
assert_eq "stray old event and short page 2: still reads all three pages" 3 "$(grep -c '/events' "${GH_LOG}")"
assert_eq "stray old event and short page 2: keeps every in-window event" 24 "$(jq .event_count <<<"${OUT}")"
assert_eq "stray old event and short page 2: feed reaching past the window is complete" true "$(jq .feed_complete <<<"${OUT}")"
feed 300 2026-10-14T00:00:00Z 2026-09-23T13:09:38Z
gather TZ=America/New_York "GH_STUB_FEED=${FEED}" -- 2026-10-13
assert_eq "feed ends inside the window: incomplete despite the stray" false "$(jq .feed_complete <<<"${OUT}")"
assert_contains "feed ends inside the window: warns" "events early in this window may be missing" "${ERR}"
feed 40 2026-10-13T00:00:00Z
gather TZ=America/New_York "GH_STUB_FEED=${FEED}" -- 2026-10-13
assert_eq "short feed: stops at the first empty page" 2 "$(grep -c '/events' "${GH_LOG}")"
assert_eq "short feed: keeps every in-window event" 24 "$(jq .event_count <<<"${OUT}")"
echo ""

# ---------------------------------------------------------------------------
# gather-atlassian.sh. A stub `curl` answers /myself, /serverInfo, /search/jql, and
# per-issue /comment requests (Jira) plus /rest/api/user/current, /rest/api/search,
# /api/v2/spaces, and /api/v2/pages/<id>/versions (Confluence) by matching the URL, the
# same way `gh` is stubbed above. Every call is logged (args only, never response
# bodies) so cases can assert the token value never reaches the log, and that
# credentials-unset/failed-identity cases never call curl at all beyond what the case
# expects.
# ---------------------------------------------------------------------------
ATLASSIAN_STUB_BIN="${WORK_DIR}/atlassian-stub-bin"
CURL_LOG="${WORK_DIR}/curl-calls.log"
REQUEST_BODY_LOG="${WORK_DIR}/curl-request-bodies.log"
ATLASSIAN_FIXTURES="${WORK_DIR}/atlassian-fixtures"
mkdir -p "${ATLASSIAN_STUB_BIN}" "${ATLASSIAN_FIXTURES}"
cat >"${ATLASSIAN_STUB_BIN}/curl" <<'EOF'
#!/bin/sh
# Logs every call (args only) and answers by matching the request URL against fixture
# files under CURL_FIXTURES. CURL_STUB_FAIL makes every call a transport failure.
# Also logs each --data-binary request body's content (not the argv, the file content)
# to REQUEST_BODY_LOG, one JSON line per call, so tests can assert on request shape
# (e.g. that "expand" is sent as the string form Jira's gateway requires, not an array).
printf '%s\n' "$*" >>"${CURL_LOG}"
[ -n "${CURL_STUB_FAIL:-}" ] && exit 7

out_file=""
url=""
prev=""
data_file=""
for arg in "$@"; do
  if [ "$prev" = "-o" ]; then
    out_file="$arg"
  fi
  if [ "$prev" = "--data-binary" ]; then
    data_file="${arg#@}"
  fi
  case "$arg" in
    http*) url="$arg" ;;
  esac
  prev="$arg"
done
if [ -n "${data_file}" ] && [ -f "${data_file}" ]; then
  cat "${data_file}" >>"${REQUEST_BODY_LOG}"
  printf '\n' >>"${REQUEST_BODY_LOG}"
fi

FIX="${ATLASSIAN_FIXTURES}"
case "$url" in
  *"/myself"*)
    status=200
    [ -f "${FIX}/myself_status" ] && status="$(cat "${FIX}/myself_status")"
    if [ -f "${FIX}/myself.json" ]; then cat "${FIX}/myself.json" >"$out_file"; else echo '{}' >"$out_file"; fi
    printf '%s' "$status"
    ;;
  *"/serverInfo"*)
    if [ -f "${FIX}/serverinfo.json" ]; then
      cat "${FIX}/serverinfo.json" >"$out_file"
      printf '200'
    else
      echo '{}' >"$out_file"
      printf '404'
    fi
    ;;
  *"/search/jql"*)
    # If the request body carries a nextPageToken, this is a follow-up page request --
    # serve search-page2.json when present (falls back to search.json otherwise, which
    # keeps every single-page fixture above working unchanged).
    if [ -n "${data_file}" ] && [ -f "${data_file}" ] && grep -q '"nextPageToken"' "${data_file}" && [ -f "${FIX}/search-page2.json" ]; then
      cat "${FIX}/search-page2.json" >"$out_file"
    elif [ -f "${FIX}/search-page1.json" ]; then
      cat "${FIX}/search-page1.json" >"$out_file"
    elif [ -f "${FIX}/search.json" ]; then
      cat "${FIX}/search.json" >"$out_file"
    else
      echo '{"issues":[],"isLast":true}' >"$out_file"
    fi
    printf '200'
    ;;
  *"/comment"*)
    key=$(echo "$url" | sed -n 's#.*/issue/\([^/]*\)/comment.*#\1#p')
    if [ -f "${FIX}/comments-${key}.json" ]; then
      cat "${FIX}/comments-${key}.json" >"$out_file"
    else
      echo '{"comments": []}' >"$out_file"
    fi
    printf '200'
    ;;
  *"/rest/api/user/current"*)
    status=200
    [ -f "${FIX}/confluence_myself_status" ] && status="$(cat "${FIX}/confluence_myself_status")"
    if [ -f "${FIX}/confluence_myself.json" ]; then cat "${FIX}/confluence_myself.json" >"$out_file"; else echo '{}' >"$out_file"; fi
    printf '%s' "$status"
    ;;
  *"/rest/api/search"*)
    if [ -f "${FIX}/confluence_search.json" ]; then cat "${FIX}/confluence_search.json" >"$out_file"; else echo '{"results":[]}' >"$out_file"; fi
    printf '200'
    ;;
  *"/api/v2/spaces"*)
    key=$(echo "$url" | sed -n 's#.*[?&]keys=\([^&]*\).*#\1#p')
    if [ -f "${FIX}/confluence_space-${key}.json" ]; then
      cat "${FIX}/confluence_space-${key}.json" >"$out_file"
    else
      echo '{"results":[]}' >"$out_file"
    fi
    printf '200'
    ;;
  *"/api/v2/pages/"*"/versions"*)
    page_id=$(echo "$url" | sed -n 's#.*/api/v2/pages/\([^/]*\)/versions.*#\1#p')
    if [ -f "${FIX}/confluence_versions-${page_id}.json" ]; then
      cat "${FIX}/confluence_versions-${page_id}.json" >"$out_file"
    else
      echo '{"results":[]}' >"$out_file"
    fi
    printf '200'
    ;;
  *)
    echo '{}' >"$out_file"
    printf '404'
    ;;
esac
EOF
chmod +x "${ATLASSIAN_STUB_BIN}/curl"

# gather_atlassian [VAR=value ...] -- [args...]
# Runs gather-atlassian.sh with the stub curl first on PATH. Sets OUT, ERR, and STATUS.
# Starts from all four Atlassian env vars unset (-u) regardless of what the ambient
# shell exports (a dev machine configured for bitwarden-atlassian-tools has real
# credentials in its environment), then layers the case's explicit env_args on top, so
# a case that omits a var is testing "unset", never an accidental leak of a real token.
gather_atlassian() {
  local env_args=()
  while [[ $# -gt 0 && "$1" != "--" ]]; do
    env_args+=("$1")
    shift
  done
  shift
  : >"${CURL_LOG}"
  : >"${REQUEST_BODY_LOG}"
  OUT="$(env -u ATLASSIAN_CLOUD_ID -u ATLASSIAN_EMAIL -u ATLASSIAN_JIRA_READ_ONLY_TOKEN -u ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN \
    PATH="${ATLASSIAN_STUB_BIN}:${PATH}" CURL_LOG="${CURL_LOG}" REQUEST_BODY_LOG="${REQUEST_BODY_LOG}" \
    ATLASSIAN_FIXTURES="${ATLASSIAN_FIXTURES}" \
    ${env_args[@]+"${env_args[@]}"} bash "${GATHER_ATLASSIAN}" "$@" 2>"${WORK_DIR}/stderr")"
  STATUS=$?
  ERR="$(cat "${WORK_DIR}/stderr")"
}

TOKEN_VALUE="sh0uldNeverLeak-tok3n"

echo "[A1] gather-atlassian.sh: credentials unset"
rm -f "${ATLASSIAN_FIXTURES}"/*
: >"${CURL_LOG}"
OUT="$(env -u ATLASSIAN_CLOUD_ID -u ATLASSIAN_EMAIL -u ATLASSIAN_JIRA_READ_ONLY_TOKEN -u ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN \
  PATH="${ATLASSIAN_STUB_BIN}:${PATH}" CURL_LOG="${CURL_LOG}" ATLASSIAN_FIXTURES="${ATLASSIAN_FIXTURES}" \
  TZ=America/New_York bash "${GATHER_ATLASSIAN}" 2026-10-13 2>"${WORK_DIR}/stderr")"
STATUS=$?
ERR="$(cat "${WORK_DIR}/stderr")"
assert_eq "credentials unset: exits 0" 0 "${STATUS}"
assert_eq "credentials unset: emits jira and confluence null" '{"jira":null,"confluence":null}' "${OUT}"
assert_contains "credentials unset: Jira stderr notice" "Jira credentials not set; skipping Jira" "${ERR}"
assert_contains "credentials unset: Confluence stderr notice" "Confluence credentials not set; skipping Confluence" "${ERR}"
assert_eq "credentials unset: curl never called" "" "$(cat "${CURL_LOG}")"
echo ""

echo "[A2] gather-atlassian.sh: /myself returns 401"
cat >"${ATLASSIAN_FIXTURES}/myself.json" <<'EOF'
{"errorMessages": ["Unauthorized"]}
EOF
echo 401 >"${ATLASSIAN_FIXTURES}/myself_status"
gather_atlassian TZ=America/New_York ATLASSIAN_CLOUD_ID=cloud1 ATLASSIAN_EMAIL=me@example.com \
  "ATLASSIAN_JIRA_READ_ONLY_TOKEN=${TOKEN_VALUE}" -- 2026-10-13
assert_eq "401 identity: exits 0" 0 "${STATUS}"
assert_eq "401 identity: emits jira null, confluence null (no Confluence token given)" '{"jira":null,"confluence":null}' "${OUT}"
assert_contains "401 identity: stderr notice" "Jira identity check failed (HTTP 401); skipping Jira" "${ERR}"
assert_contains "401 identity: Confluence independently skipped for missing credentials" "Confluence credentials not set; skipping Confluence" "${ERR}"
assert_eq "401 identity: stops after the identity check (one curl call)" 1 "$(wc -l <"${CURL_LOG}")"
assert_contains "401 identity: that call is /myself" "/myself" "$(cat "${CURL_LOG}")"
echo ""

echo "[A3] gather-atlassian.sh: happy path"
rm -f "${ATLASSIAN_FIXTURES}/myself_status"
cat >"${ATLASSIAN_FIXTURES}/myself.json" <<'EOF'
{"accountId": "acct-123", "displayName": "Recap Tester"}
EOF
cat >"${ATLASSIAN_FIXTURES}/serverinfo.json" <<'EOF'
{"baseUrl": "https://example.atlassian.net"}
EOF
# Window under test (TZ=America/New_York, date 2026-10-13) is
# 2026-10-13T11:00:00Z -> 2026-10-14T11:00:00Z.
cat >"${ATLASSIAN_FIXTURES}/search.json" <<'EOF'
{
  "isLast": true,
  "issues": [
    {
      "key": "PM-1",
      "fields": {
        "summary": "In window issue",
        "status": {"name": "In Progress", "statusCategory": {"name": "In Progress"}},
        "created": "2026-10-10T09:00:00.000+0000",
        "updated": "2026-10-13T12:00:00.000+0000",
        "reporter": {"accountId": "acct-123"},
        "assignee": {"accountId": "acct-123"}
      },
      "changelog": {
        "histories": [
          {
            "author": {"accountId": "acct-123"},
            "created": "2026-10-13T12:30:00.000+0000",
            "items": [{"field": "status", "fromString": "In Review", "toString": "In Progress"}]
          },
          {
            "author": {"accountId": "acct-123"},
            "created": "2026-10-15T12:30:00.000+0000",
            "items": [{"field": "status", "fromString": "To Do", "toString": "In Progress"}]
          }
        ]
      }
    },
    {
      "key": "PM-2",
      "fields": {
        "summary": "Blocked issue",
        "status": {"name": "Blocked", "statusCategory": {"name": "To Do"}},
        "created": "2026-10-01T09:00:00.000+0000",
        "updated": "2026-10-13T13:00:00.000+0000",
        "reporter": {"accountId": "other"},
        "assignee": {"accountId": "acct-123"}
      },
      "changelog": {"histories": []}
    }
  ]
}
EOF
cat >"${ATLASSIAN_FIXTURES}/comments-PM-1.json" <<'EOF'
{"comments": [
  {"author": {"accountId": "acct-123"}, "created": "2026-10-13T14:00:00.000+0000"},
  {"author": {"accountId": "other"}, "created": "2026-10-13T14:30:00.000+0000"}
]}
EOF
gather_atlassian TZ=America/New_York ATLASSIAN_CLOUD_ID=cloud1 ATLASSIAN_EMAIL=me@example.com \
  "ATLASSIAN_JIRA_READ_ONLY_TOKEN=${TOKEN_VALUE}" -- 2026-10-13
assert_eq "happy path: exits 0" 0 "${STATUS}"
assert_eq "happy path: account_id" acct-123 "$(jq -r .jira.account_id <<<"${OUT}")"
assert_eq "happy path: site_url" https://example.atlassian.net "$(jq -r .jira.site_url <<<"${OUT}")"
assert_eq "happy path: window start_utc" 2026-10-13T11:00:00Z "$(jq -r .jira.window.start_utc <<<"${OUT}")"
assert_eq "happy path: window end_utc" 2026-10-14T11:00:00Z "$(jq -r .jira.window.end_utc <<<"${OUT}")"
assert_eq "happy path: two issues carry involvement" 2 "$(jq '.jira.issues | length' <<<"${OUT}")"
assert_eq "happy path: PM-1 involvement" "transitioned,commented,assigned" \
  "$(jq -r '.jira.issues[] | select(.key == "PM-1") | .involvement | join(",")' <<<"${OUT}")"
assert_eq "happy path: in-window transition captured" 1 \
  "$(jq -r '.jira.issues[] | select(.key == "PM-1") | .transitions | length' <<<"${OUT}")"
assert_eq "happy path: out-of-window transition excluded" "In Review" \
  "$(jq -r '.jira.issues[] | select(.key == "PM-1") | .transitions[0].from' <<<"${OUT}")"
assert_eq "happy path: user-only comment count" 1 \
  "$(jq -r '.jira.issues[] | select(.key == "PM-1") | .comment_count' <<<"${OUT}")"
assert_eq "happy path: jira.complete is true when pagination is exhausted" true "$(jq -r .jira.complete <<<"${OUT}")"
assert_eq "happy path: PM-1's in-window backward transition sets returned:true" true \
  "$(jq -r '.jira.issues[] | select(.key == "PM-1") | .returned' <<<"${OUT}")"
assert_eq "happy path: PM-2 has no transitions so returned:false" false \
  "$(jq -r '.jira.issues[] | select(.key == "PM-2") | .returned' <<<"${OUT}")"
assert_eq "happy path: token not in stdout" "" "$(grep -F -- "${TOKEN_VALUE}" <<<"${OUT}" || true)"
assert_eq "happy path: token not in stderr" "" "$(grep -F -- "${TOKEN_VALUE}" <<<"${ERR}" || true)"
assert_eq "happy path: token not in curl argv log" "" "$(grep -F -- "${TOKEN_VALUE}" "${CURL_LOG}" || true)"
assert_eq "happy path: token not in request bodies" "" "$(grep -F -- "${TOKEN_VALUE}" "${REQUEST_BODY_LOG}" || true)"
# Regression check for the "oldest comments" bug: the comment-fetch request must ask
# for newest-first ordering, otherwise an issue with >100 comments would return its
# first page ever (oldest), silently missing the user's in-window comments. The stub
# always serves the whole comments-<key>.json fixture regardless of query params, so
# we can't simulate truncation at >100 comments through the fixture pipeline; asserting
# the request URL itself is the meaningful check here.
assert_contains "happy path: comment fetch requests newest-first ordering" \
  "orderBy=-created" "$(grep '/comment' "${CURL_LOG}")"
assert_eq "happy path: search request sends expand as a string, not an array" "\"changelog\"" \
  "$(jq -c 'select(.expand != null) | .expand' "${REQUEST_BODY_LOG}")"
assert_contains "happy path: JQL covers transitions the user made without being assignee/reporter" \
  "status CHANGED BY" "$(jq -r '.jql' "${REQUEST_BODY_LOG}")"
assert_contains "happy path: JQL covers other activity (e.g. comments) via updatedBy()" \
  "issuekey IN updatedBy(" "$(jq -r '.jql' "${REQUEST_BODY_LOG}")"
assert_eq "happy path: Confluence independently null (no Confluence token given)" null "$(jq -r '.confluence' <<<"${OUT}")"
assert_contains "happy path: Confluence stderr notice despite Jira succeeding" "Confluence credentials not set; skipping Confluence" "${ERR}"
assert_eq "happy path: no Confluence endpoints called" "" "$(grep -E '/wiki|user/current|api/v2' "${CURL_LOG}" || true)"
echo ""

echo "[A3b] gather-atlassian.sh: large per-issue comment payload (regression for jq argv E2BIG overflow)"
# Regression check for the argv-overflow bug: the per-issue comment merge used to pass
# the comment blob through a single argv string via `jq --argjson comments "$comments"`.
# Linux caps a single argv string at MAX_ARG_STRLEN (131072 bytes); macOS has no
# per-string cap but caps the whole exec (argv + environ combined) at ARG_MAX
# (getconf ARG_MAX, typically 1048576 bytes). A real issue's comment history (with body
# text, unlike this script's slimmed-down view of it) can exceed either easily. The
# fixture below is sized past both -- 6000 bulk comments by a different author (pure
# padding, ~300 bytes of body each, ~2MB total) plus the one comment that actually
# matters: acct-123's own, inside the window -- so this test fails loudly (exec
# "Argument list too long") on both platforms under the old --argjson approach, not just
# in theory on Linux. Reuses the search fixtures A3 left in place (PM-1, PM-2) and
# only replaces comments-PM-1.json. Under the old code this would have failed execve
# with E2BIG inside collect_jira's $(...) subshell (where errexit is disabled), silently
# dropping PM-1 from the output with no warning. The fix slims comments down to
# {created, author.accountId} and passes them via --slurpfile, so the payload never
# touches argv at all.
jq -n '
  { comments: (
      [range(0; 6000) | {
        author: {accountId: "other"},
        created: "2026-10-13T14:30:00.000+0000",
        body: ("x" * 300)
      }]
      + [{author: {accountId: "acct-123"}, created: "2026-10-13T14:00:00.000+0000", body: "short"}]
    )
  }
' >"${ATLASSIAN_FIXTURES}/comments-PM-1.json"
assert_eq "large comment payload: fixture exceeds the host's ARG_MAX (sanity check on the test itself)" "over" \
  "$(if [ "$(wc -c <"${ATLASSIAN_FIXTURES}/comments-PM-1.json")" -gt "$(getconf ARG_MAX)" ]; then echo over; else echo under; fi)"
gather_atlassian TZ=America/New_York ATLASSIAN_CLOUD_ID=cloud1 ATLASSIAN_EMAIL=me@example.com \
  "ATLASSIAN_JIRA_READ_ONLY_TOKEN=${TOKEN_VALUE}" -- 2026-10-13
assert_eq "large comment payload: exits 0" 0 "${STATUS}"
assert_eq "large comment payload: PM-1 is still present in the output" 1 \
  "$(jq '[.jira.issues[] | select(.key == "PM-1")] | length' <<<"${OUT}")"
assert_eq "large comment payload: PM-1 still reflects only its own in-window comment" 1 \
  "$(jq -r '.jira.issues[] | select(.key == "PM-1") | .comment_count' <<<"${OUT}")"
assert_eq "large comment payload: PM-1 involvement still includes commented" "transitioned,commented,assigned" \
  "$(jq -r '.jira.issues[] | select(.key == "PM-1") | .involvement | join(",")' <<<"${OUT}")"
echo ""

echo "[A3c] gather-atlassian.sh: In Progress -> Blocked transition does not set returned:true"
# Regression check: rank("Blocked") used to equal rank("To Do"), so a transition from
# In Progress into Blocked looked "backward" and set returned:true. Blocking your own
# ticket isn't the same as a reviewer bouncing it back, so this must stay false.
cat >"${ATLASSIAN_FIXTURES}/search.json" <<'EOF'
{
  "isLast": true,
  "issues": [
    {
      "key": "PM-3",
      "fields": {
        "summary": "Self-blocked issue",
        "status": {"name": "Blocked", "statusCategory": {"name": "To Do"}},
        "created": "2026-10-01T09:00:00.000+0000",
        "updated": "2026-10-13T12:00:00.000+0000",
        "reporter": {"accountId": "other"},
        "assignee": {"accountId": "acct-123"}
      },
      "changelog": {
        "histories": [
          {
            "author": {"accountId": "acct-123"},
            "created": "2026-10-13T12:30:00.000+0000",
            "items": [{"field": "status", "fromString": "In Progress", "toString": "Blocked"}]
          }
        ]
      }
    }
  ]
}
EOF
gather_atlassian TZ=America/New_York ATLASSIAN_CLOUD_ID=cloud1 ATLASSIAN_EMAIL=me@example.com \
  "ATLASSIAN_JIRA_READ_ONLY_TOKEN=${TOKEN_VALUE}" -- 2026-10-13
assert_eq "In Progress -> Blocked: exits 0" 0 "${STATUS}"
assert_eq "In Progress -> Blocked: transition captured" 1 \
  "$(jq -r '.jira.issues[] | select(.key == "PM-3") | .transitions | length' <<<"${OUT}")"
assert_eq "In Progress -> Blocked: does not set returned:true" false \
  "$(jq -r '.jira.issues[] | select(.key == "PM-3") | .returned' <<<"${OUT}")"
echo ""

# ---------------------------------------------------------------------------
# gather-atlassian.sh Confluence collection. Same stub curl, same window
# (2026-10-13T11:00:00Z -> 2026-10-14T11:00:00Z for TZ=America/New_York, date
# 2026-10-13). Confluence credentials are independent of Jira's: these cases omit the
# Jira token so Confluence behavior can be tested without Jira also running.
# ---------------------------------------------------------------------------
CONFLUENCE_TOKEN_VALUE="c0nflu3nce-sh0uldNeverLeak"

echo "[A4] gather-atlassian.sh: Confluence credentials unset (Jira present)"
rm -f "${ATLASSIAN_FIXTURES}"/*
cat >"${ATLASSIAN_FIXTURES}/myself.json" <<'EOF'
{"accountId": "acct-123", "displayName": "Recap Tester"}
EOF
cat >"${ATLASSIAN_FIXTURES}/search.json" <<'EOF'
{"isLast": true, "issues": []}
EOF
gather_atlassian TZ=America/New_York ATLASSIAN_CLOUD_ID=cloud1 ATLASSIAN_EMAIL=me@example.com \
  "ATLASSIAN_JIRA_READ_ONLY_TOKEN=${TOKEN_VALUE}" -- 2026-10-13
assert_eq "Confluence creds unset: exits 0" 0 "${STATUS}"
assert_eq "Confluence creds unset: confluence null despite Jira succeeding" null "$(jq -r '.confluence' <<<"${OUT}")"
assert_eq "Confluence creds unset: jira still present" acct-123 "$(jq -r '.jira.account_id' <<<"${OUT}")"
assert_contains "Confluence creds unset: stderr notice" "Confluence credentials not set; skipping Confluence" "${ERR}"
echo ""

echo "[A5] gather-atlassian.sh: Confluence identity check returns 401"
rm -f "${ATLASSIAN_FIXTURES}"/*
cat >"${ATLASSIAN_FIXTURES}/confluence_myself.json" <<'EOF'
{"message": "Unauthorized"}
EOF
echo 401 >"${ATLASSIAN_FIXTURES}/confluence_myself_status"
gather_atlassian TZ=America/New_York ATLASSIAN_CLOUD_ID=cloud1 ATLASSIAN_EMAIL=me@example.com \
  "ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN=${CONFLUENCE_TOKEN_VALUE}" -- 2026-10-13
assert_eq "Confluence 401 identity: exits 0" 0 "${STATUS}"
assert_eq "Confluence 401 identity: emits jira null (no Jira token given), confluence null" \
  '{"jira":null,"confluence":null}' "${OUT}"
assert_contains "Confluence 401 identity: stderr notice" "Confluence identity check failed (HTTP 401); skipping Confluence" "${ERR}"
assert_contains "Confluence 401 identity: calls /rest/api/user/current" "/rest/api/user/current" "$(cat "${CURL_LOG}")"
echo ""

echo "[A6] gather-atlassian.sh: Confluence happy path"
rm -f "${ATLASSIAN_FIXTURES}"/*
cat >"${ATLASSIAN_FIXTURES}/confluence_myself.json" <<'EOF'
{"accountId": "acct-123", "displayName": "Recap Tester"}
EOF
# Window under test is 2026-10-13T11:00:00Z -> 2026-10-14T11:00:00Z.
cat >"${ATLASSIAN_FIXTURES}/confluence_search.json" <<'EOF'
{
  "_links": {"base": "https://example.atlassian.net/wiki"},
  "results": [
    {
      "content": {
        "id": "111",
        "title": "Edited page",
        "space": {"key": "ENG"},
        "version": {"number": 3},
        "_links": {"webui": "/spaces/ENG/pages/111/Edited+page"}
      }
    },
    {
      "content": {
        "id": "222",
        "title": "Created page",
        "space": {"key": "ENG"},
        "version": {"number": 1},
        "_links": {"webui": "/spaces/ENG/pages/222/Created+page"}
      }
    },
    {
      "content": {
        "id": "333",
        "title": "Stale contributor match (out of window)",
        "space": {"key": "DOCS"},
        "version": {"number": 5},
        "_links": {"webui": "/spaces/DOCS/pages/333/Stale"}
      }
    }
  ]
}
EOF
cat >"${ATLASSIAN_FIXTURES}/confluence_space-ENG.json" <<'EOF'
{"results": [{"id": "900100", "key": "ENG"}]}
EOF
cat >"${ATLASSIAN_FIXTURES}/confluence_space-DOCS.json" <<'EOF'
{"results": [{"id": "900200", "key": "DOCS"}]}
EOF
cat >"${ATLASSIAN_FIXTURES}/confluence_versions-111.json" <<'EOF'
{"results": [
  {"number": 1, "authorId": "other", "createdAt": "2026-10-01T09:00:00.000Z"},
  {"number": 2, "authorId": "acct-123", "createdAt": "2026-10-05T09:00:00.000Z"},
  {"number": 3, "authorId": "acct-123", "createdAt": "2026-10-13T12:00:00.000Z"}
]}
EOF
cat >"${ATLASSIAN_FIXTURES}/confluence_versions-222.json" <<'EOF'
{"results": [
  {"number": 1, "authorId": "acct-123", "createdAt": "2026-10-13T13:00:00.000Z"}
]}
EOF
cat >"${ATLASSIAN_FIXTURES}/confluence_versions-333.json" <<'EOF'
{"results": [
  {"number": 5, "authorId": "acct-123", "createdAt": "2026-09-01T09:00:00.000Z"}
]}
EOF
gather_atlassian TZ=America/New_York ATLASSIAN_CLOUD_ID=cloud1 ATLASSIAN_EMAIL=me@example.com \
  "ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN=${CONFLUENCE_TOKEN_VALUE}" -- 2026-10-13
assert_eq "Confluence happy path: exits 0" 0 "${STATUS}"
assert_eq "Confluence happy path: account_id" acct-123 "$(jq -r .confluence.account_id <<<"${OUT}")"
assert_eq "Confluence happy path: site_url" https://example.atlassian.net/wiki "$(jq -r .confluence.site_url <<<"${OUT}")"
assert_eq "Confluence happy path: window start_utc" 2026-10-13T11:00:00Z "$(jq -r .confluence.window.start_utc <<<"${OUT}")"
assert_eq "Confluence happy path: window end_utc" 2026-10-14T11:00:00Z "$(jq -r .confluence.window.end_utc <<<"${OUT}")"
assert_eq "Confluence happy path: confluence.complete is true when pagination is exhausted" true "$(jq -r .confluence.complete <<<"${OUT}")"
assert_eq "Confluence happy path: stale contributor match (out of window) excluded" 2 "$(jq '.confluence.pages | length' <<<"${OUT}")"
assert_eq "Confluence happy path: edited page flagged as edited, not created" false \
  "$(jq -r '.confluence.pages[] | select(.title == "Edited page") | .created' <<<"${OUT}")"
assert_eq "Confluence happy path: edited page version count within window" 1 \
  "$(jq -r '.confluence.pages[] | select(.title == "Edited page") | .version_count' <<<"${OUT}")"
assert_eq "Confluence happy path: created page flagged as created" true \
  "$(jq -r '.confluence.pages[] | select(.title == "Created page") | .created' <<<"${OUT}")"
assert_eq "Confluence happy path: space key carried through" ENG \
  "$(jq -r '.confluence.pages[] | select(.title == "Edited page") | .space_key' <<<"${OUT}")"
assert_eq "Confluence happy path: space key resolved to spaceId via /api/v2/spaces" 900100 \
  "$(jq -r '.confluence.pages[] | select(.title == "Edited page") | .space_id' <<<"${OUT}")"
assert_eq "Confluence happy path: URL built from site base + webui" \
  "https://example.atlassian.net/wiki/spaces/ENG/pages/111/Edited+page" \
  "$(jq -r '.confluence.pages[] | select(.title == "Edited page") | .url' <<<"${OUT}")"
assert_eq "Confluence happy path: token not in stdout" "" "$(grep -F -- "${CONFLUENCE_TOKEN_VALUE}" <<<"${OUT}" || true)"
assert_eq "Confluence happy path: token not in stderr" "" "$(grep -F -- "${CONFLUENCE_TOKEN_VALUE}" <<<"${ERR}" || true)"
assert_eq "Confluence happy path: token not in curl argv log" "" "$(grep -F -- "${CONFLUENCE_TOKEN_VALUE}" "${CURL_LOG}" || true)"
assert_eq "Confluence happy path: space lookup is resolved once per key (cached)" 1 \
  "$(grep -c 'keys=ENG' "${CURL_LOG}")"
echo ""

echo "[A7] gather-atlassian.sh: Jira search pagination follows isLast:false and keeps both pages' issues"
rm -f "${ATLASSIAN_FIXTURES}"/*
cat >"${ATLASSIAN_FIXTURES}/myself.json" <<'EOF'
{"accountId": "acct-123", "displayName": "Recap Tester"}
EOF
cat >"${ATLASSIAN_FIXTURES}/serverinfo.json" <<'EOF'
{"baseUrl": "https://example.atlassian.net"}
EOF
# Window under test (TZ=America/New_York, date 2026-10-13) is
# 2026-10-13T11:00:00Z -> 2026-10-14T11:00:00Z.
# Page 1 reports isLast:false with a nextPageToken -- the regression this guards against is
# jq's `.isLast // true`, which turns an explicit `false` into `true` and stops the loop here.
cat >"${ATLASSIAN_FIXTURES}/search-page1.json" <<'EOF'
{
  "isLast": false,
  "nextPageToken": "TOKEN-PAGE-2",
  "issues": [
    {
      "key": "PM-10",
      "fields": {
        "summary": "Page 1 issue",
        "status": {"name": "In Progress", "statusCategory": {"name": "In Progress"}},
        "created": "2026-10-10T09:00:00.000+0000",
        "updated": "2026-10-13T12:00:00.000+0000",
        "reporter": {"accountId": "acct-123"},
        "assignee": {"accountId": "acct-123"}
      },
      "changelog": {"histories": []}
    }
  ]
}
EOF
cat >"${ATLASSIAN_FIXTURES}/search-page2.json" <<'EOF'
{
  "isLast": true,
  "issues": [
    {
      "key": "PM-11",
      "fields": {
        "summary": "Page 2 issue",
        "status": {"name": "In Progress", "statusCategory": {"name": "In Progress"}},
        "created": "2026-10-10T09:00:00.000+0000",
        "updated": "2026-10-13T13:00:00.000+0000",
        "reporter": {"accountId": "acct-123"},
        "assignee": {"accountId": "acct-123"}
      },
      "changelog": {"histories": []}
    }
  ]
}
EOF
gather_atlassian TZ=America/New_York ATLASSIAN_CLOUD_ID=cloud1 ATLASSIAN_EMAIL=me@example.com \
  "ATLASSIAN_JIRA_READ_ONLY_TOKEN=${TOKEN_VALUE}" -- 2026-10-13
assert_eq "pagination: exits 0" 0 "${STATUS}"
assert_eq "pagination: second page is requested with the token from the first" 1 \
  "$(grep -c '"nextPageToken"' "${REQUEST_BODY_LOG}")"
assert_eq "pagination: both pages' issues appear" "PM-10,PM-11" \
  "$(jq -r '[.jira.issues[].key] | sort | join(",")' <<<"${OUT}")"
echo ""

echo "[A7b] gather-atlassian.sh: Jira search hitting the page cap warns and flags complete:false"
# Reuses the A7 fixtures: page 1 reports isLast:false with a nextPageToken, i.e. more
# pages remain. DAILY_RECAP_MAX_SEARCH_PAGES=1 forces the loop to stop after page 1
# without ever requesting page 2, simulating the cap being hit on a busy window without
# needing ten-plus pages of fixture data.
gather_atlassian TZ=America/New_York ATLASSIAN_CLOUD_ID=cloud1 ATLASSIAN_EMAIL=me@example.com \
  "ATLASSIAN_JIRA_READ_ONLY_TOKEN=${TOKEN_VALUE}" DAILY_RECAP_MAX_SEARCH_PAGES=1 -- 2026-10-13
assert_eq "cap hit: exits 0" 0 "${STATUS}"
assert_eq "cap hit: page 2 is never requested" 0 \
  "$(grep -c '"nextPageToken"' "${REQUEST_BODY_LOG}")"
assert_eq "cap hit: jira.complete is false" false "$(jq -r .jira.complete <<<"${OUT}")"
assert_contains "cap hit: stderr warns about the Jira page cap" \
  "Jira search hit the 1-page safety cap with more results remaining" "${ERR}"
echo ""

echo "[A8] gather-atlassian.sh: Confluence search hitting the page cap warns and flags complete:false"
rm -f "${ATLASSIAN_FIXTURES}"/*
cat >"${ATLASSIAN_FIXTURES}/confluence_myself.json" <<'EOF'
{"accountId": "acct-123", "displayName": "Recap Tester"}
EOF
# "_links.next" present means more results remain beyond this page. The stub curl always
# serves this same fixture regardless of which page URL is requested, but
# DAILY_RECAP_MAX_SEARCH_PAGES=1 forces the loop to stop after page 1 without ever
# requesting the next page, so that is not exercised here.
cat >"${ATLASSIAN_FIXTURES}/confluence_search.json" <<'EOF'
{
  "_links": {"base": "https://example.atlassian.net/wiki", "next": "/rest/api/search?cql=...&start=25"},
  "results": []
}
EOF
gather_atlassian TZ=America/New_York ATLASSIAN_CLOUD_ID=cloud1 ATLASSIAN_EMAIL=me@example.com \
  "ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN=${CONFLUENCE_TOKEN_VALUE}" DAILY_RECAP_MAX_SEARCH_PAGES=1 -- 2026-10-13
assert_eq "Confluence cap hit: exits 0" 0 "${STATUS}"
assert_eq "Confluence cap hit: confluence.complete is false" false "$(jq -r .confluence.complete <<<"${OUT}")"
assert_contains "Confluence cap hit: stderr warns about the Confluence page cap" \
  "Confluence search hit the 1-page safety cap with more results remaining" "${ERR}"
echo ""

# ---------------------------------------------------------------------------
# gather-gh-search.sh. A stub `gh` answers `api user` and `api graphql`, choosing a
# fixture by which search string the `q` GraphQL variable carries (author:.../
# reviewed-by:.../commenter:...) and by whether a `cursor` variable was also sent
# (page1 vs page2 fixture). GH_SEARCH_STUB_FAIL makes every call a transport failure,
# matching an unauthenticated `gh`; GH_SEARCH_LOGIN_FAIL fails only the login lookup.
# ---------------------------------------------------------------------------
GH_SEARCH_STUB_BIN="${WORK_DIR}/gh-search-stub-bin"
GH_SEARCH_LOG="${WORK_DIR}/gh-search-calls.log"
GH_SEARCH_FIXTURES="${WORK_DIR}/gh-search-fixtures"
mkdir -p "${GH_SEARCH_STUB_BIN}" "${GH_SEARCH_FIXTURES}"
cat >"${GH_SEARCH_STUB_BIN}/gh" <<'EOF'
#!/bin/sh
echo "$*" >>"${GH_SEARCH_LOG}"
[ -n "${GH_SEARCH_STUB_FAIL:-}" ] && exit 1

if [ "$1" = "api" ] && [ "$2" = "user" ]; then
  [ -n "${GH_SEARCH_LOGIN_FAIL:-}" ] && exit 1
  echo "recap-tester"
  exit 0
fi

q=""
cursor=""
prev=""
for arg in "$@"; do
  if [ "$prev" = "-f" ]; then
    case "$arg" in
      q=*) q="${arg#q=}" ;;
      cursor=*) cursor="${arg#cursor=}" ;;
    esac
  fi
  prev="$arg"
done

label=""
case "$q" in
  author:*) label="authored" ;;
  reviewed-by:*) label="reviewed" ;;
  commenter:*) label="commented" ;;
esac

if [ -n "$cursor" ]; then
  fixture="${GH_SEARCH_FIXTURES}/${label}-page2.json"
else
  fixture="${GH_SEARCH_FIXTURES}/${label}-page1.json"
fi
if [ -f "$fixture" ]; then
  cat "$fixture"
else
  echo '{"data":{"search":{"pageInfo":{"hasNextPage":false,"endCursor":null},"nodes":[]}}}'
fi
EOF
chmod +x "${GH_SEARCH_STUB_BIN}/gh"

# gather_search [VAR=value ...] -- [args...]
# Runs gather-gh-search.sh with the stub gh first on PATH. Sets OUT, ERR, and STATUS.
gather_search() {
  local env_args=()
  while [[ $# -gt 0 && "$1" != "--" ]]; do
    env_args+=("$1")
    shift
  done
  shift
  : >"${GH_SEARCH_LOG}"
  OUT="$(env PATH="${GH_SEARCH_STUB_BIN}:${PATH}" GH_SEARCH_LOG="${GH_SEARCH_LOG}" \
    GH_SEARCH_FIXTURES="${GH_SEARCH_FIXTURES}" ${env_args[@]+"${env_args[@]}"} \
    bash "${GATHER_SEARCH}" "$@" 2>"${WORK_DIR}/stderr")"
  STATUS=$?
  ERR="$(cat "${WORK_DIR}/stderr")"
}

echo "[S1] gather-gh-search.sh: client-side window filtering (the updated:>= caveat)"
rm -f "${GH_SEARCH_FIXTURES}"/*
cat >"${GH_SEARCH_FIXTURES}/authored-page1.json" <<'EOF'
{"data":{"search":{"pageInfo":{"hasNextPage":false,"endCursor":null},"nodes":[
  {
    "__typename": "PullRequest",
    "number": 100,
    "title": "Old activity PR",
    "url": "https://github.com/o/r/pull/100",
    "state": "OPEN",
    "isDraft": false,
    "createdAt": "2026-09-01T00:00:00Z",
    "mergedAt": null,
    "author": {"login": "recap-tester"},
    "repository": {"nameWithOwner": "o/r"},
    "timelineItems": {"nodes": [
      {"__typename": "PullRequestCommit", "commit": {"committedDate": "2026-09-02T00:00:00Z", "author": {"user": {"login": "recap-tester"}}}},
      {"__typename": "IssueComment", "createdAt": "2026-10-13T12:00:00Z", "author": {"login": "someone-else"}},
      {"__typename": "PullRequestReview", "submittedAt": "2026-10-13T13:00:00Z", "author": {"login": "someone-else"}}
    ]}
  },
  {
    "__typename": "PullRequest",
    "number": 101,
    "title": "Boundary PR",
    "url": "https://github.com/o/r/pull/101",
    "state": "OPEN",
    "isDraft": false,
    "createdAt": "2026-10-01T00:00:00Z",
    "mergedAt": null,
    "author": {"login": "recap-tester"},
    "repository": {"nameWithOwner": "o/r"},
    "timelineItems": {"nodes": [
      {"__typename": "IssueComment", "createdAt": "2026-10-13T11:00:00Z", "author": {"login": "recap-tester"}},
      {"__typename": "IssueComment", "createdAt": "2026-10-14T11:00:00Z", "author": {"login": "recap-tester"}}
    ]}
  }
]}}}
EOF
gather_search TZ=America/New_York -- 2026-10-13
assert_eq "exits 0" 0 "${STATUS}"
assert_eq "PR with only out-of-window and other-users' activity is dropped" "" \
  "$(jq -r '.prs[] | select(.number == 100) | .number' <<<"${OUT}")"
assert_eq "PR with in-window activity by the user survives" 101 \
  "$(jq -r '.prs[] | select(.number == 101) | .number' <<<"${OUT}")"
echo ""

echo "[S2] gather-gh-search.sh: half-open window boundary"
assert_eq "activity exactly at start_utc is included" 1 \
  "$(jq -r '[.prs[] | select(.number == 101) | .activity[] | select(.time == "2026-10-13T11:00:00Z")] | length' <<<"${OUT}")"
assert_eq "activity exactly at end_utc is excluded" 0 \
  "$(jq -r '[.prs[] | select(.number == 101) | .activity[] | select(.time == "2026-10-14T11:00:00Z")] | length' <<<"${OUT}")"
assert_eq "boundary PR carries exactly its one in-window comment" 1 \
  "$(jq -r '.prs[] | select(.number == 101) | .activity | length' <<<"${OUT}")"
echo ""

echo "[S3] gather-gh-search.sh: a PR found by both the reviewed and commented searches merges to one entry"
rm -f "${GH_SEARCH_FIXTURES}"/*
cat >"${GH_SEARCH_FIXTURES}/reviewed-page1.json" <<'EOF'
{"data":{"search":{"pageInfo":{"hasNextPage":false,"endCursor":null},"nodes":[
  {
    "__typename": "PullRequest",
    "number": 200,
    "title": "Reviewed and commented PR",
    "url": "https://github.com/o/r/pull/200",
    "state": "OPEN",
    "isDraft": false,
    "createdAt": "2026-10-01T00:00:00Z",
    "mergedAt": null,
    "author": {"login": "someone-else"},
    "repository": {"nameWithOwner": "o/r"},
    "reviews": {"nodes": [
      {"state": "APPROVED", "submittedAt": "2026-10-13T12:00:00Z", "author": {"login": "recap-tester"}}
    ]}
  }
]}}}
EOF
cat >"${GH_SEARCH_FIXTURES}/commented-page1.json" <<'EOF'
{"data":{"search":{"pageInfo":{"hasNextPage":false,"endCursor":null},"nodes":[
  {
    "__typename": "PullRequest",
    "number": 200,
    "title": "Reviewed and commented PR",
    "url": "https://github.com/o/r/pull/200",
    "state": "OPEN",
    "isDraft": false,
    "createdAt": "2026-10-01T00:00:00Z",
    "mergedAt": null,
    "author": {"login": "someone-else"},
    "repository": {"nameWithOwner": "o/r"},
    "comments": {"nodes": [
      {"createdAt": "2026-10-13T13:00:00Z", "author": {"login": "recap-tester"}}
    ]}
  }
]}}}
EOF
gather_search TZ=America/New_York -- 2026-10-13
assert_eq "exits 0" 0 "${STATUS}"
assert_eq "one PR entry, not two" 1 "$(jq -r '[.prs[] | select(.number == 200)] | length' <<<"${OUT}")"
assert_eq "roles are reviewed and commented, in that order" "reviewed,commented" \
  "$(jq -r '.prs[] | select(.number == 200) | .roles | join(",")' <<<"${OUT}")"
assert_eq "both role's activity are present" 2 \
  "$(jq -r '.prs[] | select(.number == 200) | .activity | length' <<<"${OUT}")"
echo ""

echo "[S4] gather-gh-search.sh: pagination follows the cursor and keeps both pages' PRs"
rm -f "${GH_SEARCH_FIXTURES}"/*
cat >"${GH_SEARCH_FIXTURES}/authored-page1.json" <<'EOF'
{"data":{"search":{"pageInfo":{"hasNextPage":true,"endCursor":"CURSOR1"},"nodes":[
  {
    "__typename": "PullRequest",
    "number": 300,
    "title": "Page 1 PR",
    "url": "https://github.com/o/r/pull/300",
    "state": "OPEN",
    "isDraft": false,
    "createdAt": "2026-10-13T12:00:00Z",
    "mergedAt": null,
    "author": {"login": "recap-tester"},
    "repository": {"nameWithOwner": "o/r"},
    "timelineItems": {"nodes": []}
  }
]}}}
EOF
cat >"${GH_SEARCH_FIXTURES}/authored-page2.json" <<'EOF'
{"data":{"search":{"pageInfo":{"hasNextPage":false,"endCursor":null},"nodes":[
  {
    "__typename": "PullRequest",
    "number": 301,
    "title": "Page 2 PR",
    "url": "https://github.com/o/r/pull/301",
    "state": "OPEN",
    "isDraft": false,
    "createdAt": "2026-10-13T13:00:00Z",
    "mergedAt": null,
    "author": {"login": "recap-tester"},
    "repository": {"nameWithOwner": "o/r"},
    "timelineItems": {"nodes": []}
  }
]}}}
EOF
gather_search TZ=America/New_York -- 2026-10-13
assert_eq "exits 0" 0 "${STATUS}"
assert_eq "second page is requested with the cursor from the first" 1 \
  "$(grep -c 'cursor=CURSOR1' "${GH_SEARCH_LOG}")"
assert_eq "both pages' PRs appear" "300,301" \
  "$(jq -r '[.prs[].number] | sort | join(",")' <<<"${OUT}")"
assert_eq "search_complete is true once pagination is exhausted" true "$(jq -r .search_complete <<<"${OUT}")"
echo ""

echo "[S5] gather-gh-search.sh: a two-date window runs from START's cutoff to the day after END's"
rm -f "${GH_SEARCH_FIXTURES}"/*
gather_search TZ=America/New_York -- 2026-10-13 2026-10-14
assert_eq "exits 0" 0 "${STATUS}"
assert_eq "window.start_date is START-DATE" 2026-10-13 "$(jq -r .window.start_date <<<"${OUT}")"
assert_eq "window.end_date is END-DATE" 2026-10-14 "$(jq -r .window.end_date <<<"${OUT}")"
assert_eq "window.start_utc is START-DATE at the cutoff" 2026-10-13T11:00:00Z "$(jq -r .window.start_utc <<<"${OUT}")"
assert_eq "window.end_utc is the day after END-DATE at the cutoff" 2026-10-15T11:00:00Z "$(jq -r .window.end_utc <<<"${OUT}")"
echo ""

echo "[S6] gather-gh-search.sh: a GraphQL errors response fails, naming the query"
rm -f "${GH_SEARCH_FIXTURES}"/*
cat >"${GH_SEARCH_FIXTURES}/authored-page1.json" <<'EOF'
{"errors":[{"message":"Something went wrong executing your query"}]}
EOF
gather_search TZ=America/New_York -- 2026-10-13
assert_eq "exits non-zero" 1 "${STATUS}"
assert_contains "names the failing query" "authored" "${ERR}"
echo ""

echo "[S7] gather-gh-search.sh: END-DATE before START-DATE is rejected"
rm -f "${GH_SEARCH_FIXTURES}"/*
gather_search TZ=America/New_York -- 2026-10-14 2026-10-13
assert_eq "exits non-zero" 1 "${STATUS}"
assert_eq "never calls gh" "" "$(cat "${GH_SEARCH_LOG}")"
echo ""

echo "[S8] gather-gh-search.sh: a missing login fails after the window is still printed"
rm -f "${GH_SEARCH_FIXTURES}"/*
gather_search TZ=America/New_York GH_SEARCH_LOGIN_FAIL=1 -- 2026-10-13
assert_eq "exits non-zero" 1 "${STATUS}"
assert_contains "window line is still printed to stderr" "# Window:" "${ERR}"
echo ""

echo "[S9] gather-gh-search.sh: search queries have no updated: upper bound (regression guard)"
rm -f "${GH_SEARCH_FIXTURES}"/*
gather_search TZ=America/New_York -- 2026-10-13
assert_eq "exits 0" 0 "${STATUS}"
assert_eq "no query carries a .. range" "" "$(grep -o 'updated:[^ ]*\.\.[^ ]*' "${GH_SEARCH_LOG}")"
assert_eq "authored query uses a floor-only updated:>= filter" 1 \
  "$(grep -c -- "-f q=author:recap-tester type:pr updated:>=2026-10-13" "${GH_SEARCH_LOG}")"
assert_eq "reviewed query uses a floor-only updated:>= filter" 1 \
  "$(grep -c -- "-f q=reviewed-by:recap-tester type:pr -author:recap-tester updated:>=2026-10-13" "${GH_SEARCH_LOG}")"
assert_eq "commented query uses a floor-only updated:>= filter" 1 \
  "$(grep -c -- "-f q=commenter:recap-tester type:pr -author:recap-tester updated:>=2026-10-13" "${GH_SEARCH_LOG}")"
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

echo "[11] find-sessions.sh session selection"
find_sessions "${START}" "${END}"
assert_eq "exits 0" 0 "${STATUS}"
assert_eq "keeps only the project session with in-window activity" s-window "$(sessions_found)"
assert_eq "no session reported unreadable" "" "${ERR}"
find_sessions "${START}" "${END}" --include-home
assert_eq "--include-home adds the home session, ordered by first activity" s-window,s-home "$(sessions_found)"
assert_eq "home digest names its project" -Users-recap-tester "$(jq -r '.[1].project' <<<"${OUT}")"
echo ""

echo "[12] find-sessions.sh window boundaries and the half-written line"
find_sessions "${START}" "${END}"
DIGEST="$(jq '.[0]' <<<"${OUT}")"
assert_eq "first activity is the entry 250 ms into the window" 2026-01-05T11:00:00.250Z "$(jq -r .first_activity <<<"${DIGEST}")"
assert_eq "last activity is the final in-window entry" 2026-01-06T10:59:59.900Z "$(jq -r .last_activity <<<"${DIGEST}")"
assert_eq "counts in-window entries only, without the cut-off line" 15 "$(jq -r .entries_in_window <<<"${DIGEST}")"
assert_eq "cwd comes from the first in-window entry" /Users/recap-tester/dev/app "$(jq -r .cwd <<<"${DIGEST}")"
assert_eq "branches skip HEAD and out-of-window entries" feature/sync,main "$(jq -r '.branches | join(",")' <<<"${DIGEST}")"
assert_eq "path points at the session log" "${APP}/s-window.jsonl" "$(jq -r .path <<<"${DIGEST}")"
echo ""

echo "[13] find-sessions.sh prompt filter"
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

echo "[14] find-sessions.sh default log location"
DEFAULT_HOME="${WORK_DIR}/home"
session_file "${DEFAULT_HOME}/.claude/projects/-Users-someone-dev-api" s-default 2026-01-05T15:00:00.000Z
OUT="$(env -u CLAUDE_CONFIG_DIR HOME="${DEFAULT_HOME}" bash "${FIND}" "${START}" "${END}" 2>/dev/null)"
assert_eq "reads ~/.claude/projects when CLAUDE_CONFIG_DIR is unset" s-default "$(sessions_found)"
echo ""

echo "[15] find-sessions.sh argument checks"
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

# ---------------------------------------------------------------------------
# template.html CSP script hash. The Content-Security-Policy pins the inline
# <script> by its SHA-256 hash; if the script is edited without recomputing the
# hash, the page still renders but filtering and Copy silently stop working.
# ---------------------------------------------------------------------------
echo "[16] template.html CSP script hash"
if ! command -v perl >/dev/null 2>&1 || ! command -v openssl >/dev/null 2>&1; then
  echo "  (skipped: perl and openssl are required for this case)"
else
  SCRIPT_HASH="$(perl -0777 -ne 'print $1 if /<script>(.*?)<\/script>/s' "${TEMPLATE}" | openssl dgst -sha256 -binary | openssl base64)"
  CSP_HASH="$(grep -o "sha256-[^']*" "${TEMPLATE}" | head -1 | sed 's/^sha256-//')"
  if [[ "${SCRIPT_HASH}" == "${CSP_HASH}" ]]; then
    pass "CSP sha256 hash matches the <script> block"
  else
    fail "CSP sha256 hash matches the <script> block"
    echo "     expected (from <script>): ${SCRIPT_HASH}"
    echo "     got (from CSP meta):      ${CSP_HASH}"
    echo "     see README.md 'Maintaining the Template' to regenerate the hash"
  fi
fi
echo ""

echo "=== ${PASSED} passed, ${FAILED} failed ==="
[[ "${FAILED}" -eq 0 ]]
