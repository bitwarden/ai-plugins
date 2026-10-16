# shellcheck shell=bash
# Portable date helpers shared by the daily-recap scripts. Sourced, not executed.
#
# Each helper tries GNU date syntax first and falls back to BSD date (macOS), so the
# scripts behave the same on Linux, macOS, and macOS with GNU coreutils on PATH.
# Local-time helpers honor the standard TZ environment variable.

# local_to_epoch "YYYY-MM-DD HH:MM:SS" -> epoch seconds, interpreting the input in local time.
# A time inside a spring-forward gap does not exist on the wall clock. BSD date reads it
# with the UTC offset in effect before the gap, so 02:30 becomes 03:30 after the change.
# GNU date rejects it, so the last fallback applies the previous day's offset to match.
local_to_epoch() {
  date -d "$1" +%s 2>/dev/null && return
  date -j -f '%Y-%m-%d %H:%M:%S' "$1" +%s 2>/dev/null && return
  local offset
  offset=$(date -d "${1%% *} 12:00:00 yesterday" +%z 2>/dev/null) || return 1
  date -d "$1 ${offset}" +%s 2>/dev/null
}

# utc_to_epoch "YYYY-MM-DDTHH:MM:SSZ" -> epoch seconds.
utc_to_epoch() {
  date -u -d "$1" +%s 2>/dev/null || date -j -u -f '%Y-%m-%dT%H:%M:%SZ' "$1" +%s 2>/dev/null
}

# epoch_fmt EPOCH FORMAT -> EPOCH formatted in local time.
epoch_fmt() {
  date -d "@$1" "+$2" 2>/dev/null || date -r "$1" "+$2" 2>/dev/null
}

# epoch_fmt_utc EPOCH FORMAT -> EPOCH formatted in UTC.
epoch_fmt_utc() {
  date -u -d "@$1" "+$2" 2>/dev/null || date -u -r "$1" "+$2" 2>/dev/null
}

# add_days YYYY-MM-DD N -> the date N days later (N may be negative).
# Anchors on local noon so DST transitions never shift the result across a date line.
add_days() {
  local epoch
  epoch=$(local_to_epoch "$1 12:00:00") || return 1
  epoch_fmt "$((epoch + $2 * 86400))" '%Y-%m-%d'
}

# is_valid_date YYYY-MM-DD -> success only for a real calendar date in that exact form.
# BSD date silently normalizes impossible dates (2026-02-30 becomes 2026-03-02), so the
# round trip through add_days catches what parsing alone accepts.
is_valid_date() {
  [[ "$1" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] || return 1
  [[ "$(add_days "$1" 0 2>/dev/null)" == "$1" ]]
}
