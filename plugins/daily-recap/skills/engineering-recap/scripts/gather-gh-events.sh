#!/usr/bin/env bash
# Pull GitHub events and filter to the user's workday window.
#
# Day boundary: defaults to 07:00 in the user's local timezone (DST-safe via the
# system date utility). Override the cutoff hour with DAILY_RECAP_CUTOFF_HOUR
# (e.g. 6 for 6am-local). Override the timezone with the standard TZ env var
# (e.g. TZ=America/Los_Angeles) — useful when scripting recaps for someone else.
#
# Usage:
#   gather-gh-events.sh [date]
#     date: target day in YYYY-MM-DD form, in the user's local timezone.
#           Defaults to yesterday.
#
# Output: JSON array of events with summary fields on stdout.
# Side effects: caches raw events at /tmp/gh-events-raw-${date}.json
#
# Requires: gh, jq, GNU or BSD date

set -euo pipefail

CUTOFF_HOUR="${DAILY_RECAP_CUTOFF_HOUR:-7}"
DATE="${1:-$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d 'yesterday' +%Y-%m-%d)}"
LOGIN="$(gh api user --jq .login)"

# Convert "YYYY-MM-DD HH:00:00" interpreted in local TZ to a UTC ISO-8601
# timestamp. Works with both BSD date (macOS) and GNU date (Linux).
local_to_utc() {
  local local_dt="$1"
  if date -u -d "$local_dt" "+%Y-%m-%dT%H:%M:%SZ" 2>/dev/null; then
    return 0
  fi
  local epoch
  epoch=$(date -j -f "%Y-%m-%d %H:%M:%S" "$local_dt" "+%s" 2>/dev/null) || return 1
  date -u -r "$epoch" "+%Y-%m-%dT%H:%M:%SZ"
}

# Add one day to a YYYY-MM-DD string. Portable across BSD/GNU date.
next_day() {
  local d="$1"
  date -j -v+1d -f "%Y-%m-%d" "$d" "+%Y-%m-%d" 2>/dev/null \
    || date -d "$d + 1 day" "+%Y-%m-%d"
}

NEXT_DATE=$(next_day "$DATE")
START=$(local_to_utc "${DATE} $(printf '%02d' "$CUTOFF_HOUR"):00:00")
END=$(local_to_utc "${NEXT_DATE} $(printf '%02d' "$CUTOFF_HOUR"):00:00")
TZ_LABEL=$(date "+%Z")

echo "# Window: $START → $END  (${CUTOFF_HOUR}am $TZ_LABEL boundary)" >&2

CACHE="/tmp/gh-events-raw-${DATE}.json"
gh api "users/${LOGIN}/events?per_page=100" > "$CACHE"

# Filter to window and emit a compact summary
jq --arg start "$START" --arg end "$END" '
  [.[]
    | select(.created_at >= $start and .created_at < $end)
    | {
        time: .created_at,
        type,
        repo: .repo.name,
        action: (.payload.action // null),
        pr: (.payload.pull_request.number // .payload.issue.number // null),
        pr_title: (.payload.pull_request.title // .payload.issue.title // null),
        pr_author: (.payload.pull_request.user.login // .payload.issue.user.login // null),
        pr_state: (.payload.pull_request.state // null),
        pr_merged: (.payload.pull_request.merged // null),
        pr_draft: (.payload.pull_request.draft // null),
        review_state: (.payload.review.state // null),
        comment_body: (.payload.comment.body // null) | (if . then .[0:300] else null end),
        comment_path: (.payload.comment.path // null),
        ref: (.payload.ref // null),
        ref_type: (.payload.ref_type // null),
        head_sha: (.payload.head[0:9] // null),
        commit_msgs: ([.payload.commits[]? | .message | split("\n")[0]])
      }
  ]
' "$CACHE"
