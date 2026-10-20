#!/usr/bin/env bash
# Pull the authenticated user's GitHub events for one workday and emit a compact JSON summary.
#
# A workday runs from the cutoff hour on the given date to the cutoff hour on the next
# date, in local time, so work done after midnight counts toward the day it continues.
#
# Usage:
#   gather-gh-events.sh [YYYY-MM-DD]
#     The workday to collect, named by the local date it starts on. Defaults to the most
#     recently completed workday (yesterday once today's cutoff has passed, otherwise
#     the day before).
#
# Environment:
#   DAILY_RECAP_CUTOFF_HOUR  Local hour (0-23) at which a workday begins. Default: 7.
#   TZ                       Standard timezone override, e.g. America/Los_Angeles.
#
# Output (stdout): a JSON object with "login", "window", "feed_complete", "event_count",
# and "events". The window line and any coverage warning also go to stderr.
#
# Requires: gh (authenticated), jq, and GNU or BSD date.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=SCRIPTDIR/date-utils.sh
source "${SCRIPT_DIR}/date-utils.sh"

die() {
  echo "gather-gh-events: $*" >&2
  exit 1
}

for cmd in gh jq; do
  command -v "$cmd" >/dev/null 2>&1 || die "'$cmd' is required but not installed"
done

# GitHub's user events feed holds at most 300 events (3 pages of 100) from the last 30 days.
readonly PER_PAGE=100
readonly MAX_PAGES=3
readonly FEED_MAX_AGE_DAYS=30

cutoff_raw="${DAILY_RECAP_CUTOFF_HOUR:-7}"
if ! [[ "$cutoff_raw" =~ ^[0-9]{1,2}$ ]] || ((10#$cutoff_raw > 23)); then
  die "DAILY_RECAP_CUTOFF_HOUR must be a whole hour from 0 to 23 (got '${cutoff_raw}')"
fi
CUTOFF_HOUR=$((10#$cutoff_raw))
CUTOFF_HH="$(printf '%02d' "$CUTOFF_HOUR")"

TODAY="$(date +%Y-%m-%d)"
if [[ $# -ge 1 ]]; then
  DATE="$1"
  is_valid_date "$DATE" || die "date must be a real calendar date in YYYY-MM-DD form (got '${DATE}')"
elif ((10#$(date +%H) >= CUTOFF_HOUR)); then
  DATE="$(add_days "$TODAY" -1)"
else
  DATE="$(add_days "$TODAY" -2)"
fi

NEXT_DATE="$(add_days "$DATE" 1)"
START_EPOCH="$(local_to_epoch "${DATE} ${CUTOFF_HH}:00:00")" \
  || die "could not compute the window start for ${DATE} ${CUTOFF_HH}:00 local time"
END_EPOCH="$(local_to_epoch "${NEXT_DATE} ${CUTOFF_HH}:00:00")" \
  || die "could not compute the window end for ${NEXT_DATE} ${CUTOFF_HH}:00 local time"

START_UTC="$(epoch_fmt_utc "$START_EPOCH" '%Y-%m-%dT%H:%M:%SZ')"
END_UTC="$(epoch_fmt_utc "$END_EPOCH" '%Y-%m-%dT%H:%M:%SZ')"
START_LOCAL="$(epoch_fmt "$START_EPOCH" '%Y-%m-%dT%H:%M:%S%z')"
END_LOCAL="$(epoch_fmt "$END_EPOCH" '%Y-%m-%dT%H:%M:%S%z')"
TZ_LABEL="$(epoch_fmt "$START_EPOCH" '%Z')"

echo "# Window: ${START_UTC} -> ${END_UTC} (${CUTOFF_HH}:00 ${TZ_LABEL} boundary)" >&2

LOGIN="$(gh api user --jq .login 2>/dev/null)" \
  || die "could not read your GitHub login; run 'gh auth login' and try again"

WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/daily-recap.XXXXXX")"
trap 'rm -rf "$WORK_DIR"' EXIT

# The feed is in delivery order, not created_at order: events from private repositories
# often arrive late carrying their original, older timestamps. An old timestamp on a page
# says nothing about how far back the feed reaches, and a page can come back a few events
# short mid-feed, so only an empty page marks the end.
feed_exhausted=false
page=1
while ((page <= MAX_PAGES)); do
  page_file="${WORK_DIR}/page-${page}.json"
  gh api "users/${LOGIN}/events?per_page=${PER_PAGE}&page=${page}" >"$page_file" \
    || die "GitHub events request failed on page ${page}"
  if (($(jq 'length' "$page_file") == 0)); then
    feed_exhausted=true
    break
  fi
  page=$((page + 1))
done

RAW="${WORK_DIR}/events.json"
jq -s 'add // []' "$WORK_DIR"/page-*.json >"$RAW"

# How far back the feed reaches is read from its tail, taking the newest of the last few
# events so one late arrival there cannot overstate the reach. The window is fully covered
# when that point is before its start, or when the feed ended naturally and the window is
# recent enough to fall inside the feed's retention.
reach_back="$(jq -r '.[-10:] | map(.created_at) | max // ""' "$RAW")"
retention_floor=$(($(date +%s) - FEED_MAX_AGE_DAYS * 86400))
feed_complete=false
if [[ -n "$reach_back" && "$reach_back" < "$START_UTC" ]]; then
  feed_complete=true
elif [[ "$feed_exhausted" == true ]] && ((START_EPOCH >= retention_floor)); then
  feed_complete=true
fi
if [[ "$feed_complete" != true ]]; then
  echo "# Warning: GitHub's events feed only reaches back to about ${reach_back:-nothing} (300 events or ${FEED_MAX_AGE_DAYS} days at most), so events early in this window may be missing." >&2
fi

jq \
  --arg login "$LOGIN" \
  --arg date "$DATE" \
  --argjson cutoff "$CUTOFF_HOUR" \
  --arg tz "$TZ_LABEL" \
  --arg start "$START_UTC" \
  --arg end "$END_UTC" \
  --arg start_local "$START_LOCAL" \
  --arg end_local "$END_LOCAL" \
  --argjson complete "$feed_complete" '
  [ .[]
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
        url: (.payload.comment.html_url // .payload.review.html_url // .payload.pull_request.html_url // .payload.issue.html_url // null),
        review_state: (.payload.review.state // null),
        comment_body: (.payload.comment.body // .payload.review.body // null | if . then .[0:300] else null end),
        comment_path: (.payload.comment.path // null),
        ref: (.payload.ref // null),
        ref_type: (.payload.ref_type // null),
        head_sha: (.payload.head // null | if . then .[0:9] else null end),
        commit_msgs: [.payload.commits[]? | .message | split("\n")[0]]
      }
  ] | sort_by(.time) as $events
  | {
      login: $login,
      window: {
        date: $date,
        cutoff_hour: $cutoff,
        timezone: $tz,
        start_utc: $start,
        end_utc: $end,
        start_local: $start_local,
        end_local: $end_local
      },
      feed_complete: $complete,
      event_count: ($events | length),
      events: $events
    }
' "$RAW"
