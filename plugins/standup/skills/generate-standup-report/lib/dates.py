"""
dates.py -- Timeline parsing and per-service date literals

Translates --timeline strings into per-service date literals used by the
various API collectors:
  - JQL date strings (YYYY-MM-DD)
  - GitHub updated: floor (YYYY-MM-DD, coarse -- client-side filtering required)
  - Confluence CQL date strings (YYYY-MM-DD)
  - ISO-8601 datetime strings for Python datetime comparisons

All datetimes are tz-aware, anchored to the timezone specified by the
STANDUP_TZ environment variable (defaults to "UTC" if unset).

Accepted timeline formats:
  Relative: "last 1 day", "last 1 week", "last 2 weeks"
  Absolute: "2026-04-14 - 2026-06-20"
"""

import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

_tz_name = os.environ.get("STANDUP_TZ", "UTC")
USER_TZ = ZoneInfo(_tz_name)


@dataclass
class TimeWindow:
    """A resolved time window with per-service date accessors."""

    start: datetime  # tz-aware, anchored to STANDUP_TZ (default UTC)
    end: datetime    # tz-aware, anchored to STANDUP_TZ (default UTC)
    input_timeline: str

    @property
    def jql_start(self) -> str:
        """JQL date literal: YYYY-MM-DD (Jira interprets in project TZ)."""
        return self.start.strftime("%Y-%m-%d")

    @property
    def jql_end(self) -> str:
        """JQL date literal: YYYY-MM-DD."""
        return self.end.strftime("%Y-%m-%d")

    @property
    def gh_floor(self) -> str:
        """GitHub updated: coarse floor (YYYY-MM-DD).

        Note: GitHub's 'updated:>=' filter matches the last-updated timestamp of
        the PR, NOT per-event activity timestamps. Client-side filtering against
        individual event dates is mandatory for all GitHub collectors.
        """
        return self.start.strftime("%Y-%m-%d")

    @property
    def cql_start(self) -> str:
        """Confluence CQL date literal: YYYY-MM-DD."""
        return self.start.strftime("%Y-%m-%d")

    @property
    def cql_end(self) -> str:
        """Confluence CQL date literal: YYYY-MM-DD."""
        return self.end.strftime("%Y-%m-%d")

    @property
    def iso_start(self) -> str:
        """Full ISO-8601 datetime string for the window start."""
        return self.start.isoformat()

    @property
    def iso_end(self) -> str:
        """Full ISO-8601 datetime string for the window end."""
        return self.end.isoformat()


_RELATIVE_RE = re.compile(
    r"^last\s+(\d+)\s+(day|days|week|weeks)$", re.IGNORECASE
)
_ABSOLUTE_RE = re.compile(
    r"^(\d{4}-\d{2}-\d{2})\s*-\s*(\d{4}-\d{2}-\d{2})$"
)


def parse_timeline(timeline: str) -> TimeWindow:
    """Parse a timeline string into a TimeWindow with tz-aware datetimes.

    Accepted formats:
      "last N day[s]"   -- relative; N must be a positive integer
      "last N week[s]"  -- relative
      "YYYY-MM-DD - YYYY-MM-DD"  -- absolute (inclusive on both ends)

    Raises ValueError for any other format.
    """
    timeline = timeline.strip()

    # Try relative pattern
    m = _RELATIVE_RE.match(timeline)
    if m:
        n = int(m.group(1))
        unit = m.group(2).lower()
        if unit.startswith("week"):
            delta = timedelta(weeks=n)
        else:
            delta = timedelta(days=n)

        now = datetime.now(tz=USER_TZ)
        end = now.replace(hour=23, minute=59, second=59, microsecond=0)
        start_day = now - delta
        start = start_day.replace(hour=0, minute=0, second=0, microsecond=0)
        return TimeWindow(start=start, end=end, input_timeline=timeline)

    # Try absolute pattern
    m = _ABSOLUTE_RE.match(timeline)
    if m:
        start = datetime.fromisoformat(m.group(1)).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=USER_TZ
        )
        end = datetime.fromisoformat(m.group(2)).replace(
            hour=23, minute=59, second=59, microsecond=0, tzinfo=USER_TZ
        )
        return TimeWindow(start=start, end=end, input_timeline=timeline)

    raise ValueError(
        f"Unrecognized timeline format: {timeline!r}\n"
        "Accepted formats:\n"
        "  Relative: 'last 1 day', 'last 1 week', 'last 2 weeks'\n"
        "  Absolute: 'YYYY-MM-DD - YYYY-MM-DD'"
    )


def event_in_window(event_iso: str | None, window: TimeWindow) -> bool:
    """Return True if an ISO-8601 event timestamp falls within the window.

    Handles both Z-suffix and +HH:MM offset strings. Returns False for None
    or unparseable input rather than raising.
    """
    if not event_iso:
        return False
    try:
        # Normalize Z suffix to +00:00 for fromisoformat compatibility
        normalized = event_iso.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return window.start <= dt <= window.end
    except (ValueError, TypeError):
        return False


# ---------------------------------------------------------------------------
# Self-test (__main__ block)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import traceback

    failures = []

    def check(label: str, condition: bool):
        if not condition:
            failures.append(label)
            print(f"  FAIL: {label}", file=sys.stderr)
        else:
            print(f"  ok:   {label}")

    print("--- test: last 1 day ---")
    w = parse_timeline("last 1 day")
    print(f"  start={w.iso_start}  end={w.iso_end}")
    check("start < end", w.start < w.end)
    check("jql_start is YYYY-MM-DD", len(w.jql_start) == 10 and w.jql_start[4] == "-")
    check("gh_floor is YYYY-MM-DD", len(w.gh_floor) == 10)
    check("cql_start is YYYY-MM-DD", len(w.cql_start) == 10)
    check("iso_start is full ISO", "T" in w.iso_start)

    print("--- test: last 1 week ---")
    w = parse_timeline("last 1 week")
    print(f"  start={w.iso_start}  end={w.iso_end}")
    check("start < end", w.start < w.end)
    check("delta >= 7 days", (w.end - w.start).days >= 6)

    print("--- test: last 2 weeks ---")
    w = parse_timeline("last 2 weeks")
    print(f"  start={w.iso_start}  end={w.iso_end}")
    check("delta >= 14 days", (w.end - w.start).days >= 13)

    print("--- test: absolute 2026-04-14 - 2026-06-20 ---")
    w = parse_timeline("2026-04-14 - 2026-06-20")
    print(f"  start={w.iso_start}  end={w.iso_end}")
    check("start year 2026", w.start.year == 2026)
    check("start month 4", w.start.month == 4)
    check("start day 14", w.start.day == 14)
    check("end month 6", w.end.month == 6)
    check("end day 20", w.end.day == 20)
    check("start hour 0", w.start.hour == 0)
    check("end hour 23", w.end.hour == 23)
    check("tz-aware start", w.start.tzinfo is not None)

    print("--- test: bad input raises ValueError ---")
    try:
        parse_timeline("yesterday")
        failures.append("should have raised ValueError for 'yesterday'")
        print("  FAIL: no ValueError raised")
    except ValueError as e:
        print(f"  ok:   ValueError raised: {e!r}")

    print("--- test: event_in_window ---")
    w = parse_timeline("2026-04-14 - 2026-06-20")
    check(
        "Z-suffix in window",
        event_in_window("2026-05-01T12:00:00Z", w),
    )
    check(
        "+00:00 offset in window",
        event_in_window("2026-05-01T12:00:00+00:00", w),
    )
    check(
        "before window",
        not event_in_window("2026-01-01T00:00:00Z", w),
    )
    check(
        "after window",
        not event_in_window("2026-12-31T00:00:00Z", w),
    )
    check(
        "None returns False",
        not event_in_window(None, w),
    )
    check(
        "garbage returns False",
        not event_in_window("not-a-date", w),
    )

    if failures:
        print(f"\nSelf-test FAIL ({len(failures)} failure(s)): {failures}", file=sys.stderr)
        sys.exit(1)
    else:
        print("\nSelf-test PASS")
