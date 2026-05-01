#!/usr/bin/env bash
# Pull GitHub events for the user and filter to the 7am-Eastern workday window.
#
# Usage:
#   gather-gh-events.sh [date]
#     date: yesterday's date in YYYY-MM-DD form (Eastern). Defaults to yesterday.
#
# Output: JSON array of events with summary fields, written to stdout.
# Side effects: caches raw events at /tmp/gh-events-raw-${date}.json
#
# Requires: gh, jq, GNU or BSD date

set -euo pipefail

DATE="${1:-$(date -u -v-1d +%Y-%m-%d 2>/dev/null || date -u -d 'yesterday' +%Y-%m-%d)}"
LOGIN="$(gh api user --jq .login)"

# Determine if the target date is during EDT (March–November) or EST (November–March).
# Approximation: months 3–11 EDT (UTC-4), months 12,1,2 EST (UTC-5).
# This is good enough for daily-recap purposes; refine if DST exact dates matter.
MONTH=$(echo "$DATE" | cut -d- -f2)
if [[ "$MONTH" -ge 3 && "$MONTH" -le 11 ]]; then
  OFFSET_HOURS=11   # 7am EDT = 11:00Z
  TZ_LABEL="EDT"
else
  OFFSET_HOURS=12   # 7am EST = 12:00Z
  TZ_LABEL="EST"
fi

START="${DATE}T$(printf '%02d' $OFFSET_HOURS):00:00Z"
# End = next day at the same offset
NEXT_DATE=$(date -u -j -v+1d -f "%Y-%m-%d" "$DATE" +%Y-%m-%d 2>/dev/null \
            || date -u -d "$DATE + 1 day" +%Y-%m-%d)
END="${NEXT_DATE}T$(printf '%02d' $OFFSET_HOURS):00:00Z"

echo "# Window: $START → $END  (7am $TZ_LABEL boundary)" >&2

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
