"""
collect_jira.py -- Jira activity collector (CAT3 + CAT4 + CAT5 + CAT7 + CAT8 + CAT9)

Collects six categories of Jira activity for a given user:
  - CAT3: Tickets resolved/done in window (time-windowed)
  - CAT4: Tickets created by user in window (time-windowed)
  - CAT5: Comments left by user in window (two-step: JQL prefilter + per-issue comment scan)
  - CAT7: Grooming edits by user in window (Activity Streams feed, comprehensive)
  - CAT8: Current in-progress tickets (NOT time-windowed -- current snapshot)
  - CAT9: Current blocked tickets (NOT time-windowed -- current snapshot)

All JQL uses assignee = "<accountId>" (quoted) rather than currentUser() so
the token holder and the searched user can differ.

All categories degrade gracefully: on exception, returns
{status:"error", count:0, items:[], error:<message>} for that category.

fetch_all_comments() is a reusable helper usable by both this module and
collect_github.py (for linked_ticket comment enrichment).  A module-level
_comment_cache dict deduplicates fetches within a single gather.py run.
"""

import json
import re
import sys
import time
import xml.etree.ElementTree as ET

# CAT5 maximum candidate issues to scan for comments (prevents unbounded N+1)
CAT5_N_BUDGET = 100

# ---------------------------------------------------------------------------
# Module-level comment cache: shared across all callers within a single run.
# Key: issue_key (str) -> list[comment_dict] | None
# None means a fetch was attempted but failed (so we don't retry).
# ---------------------------------------------------------------------------
_comment_cache: dict = {}

# Maximum comments to return per ticket (newest N)
_COMMENTS_MAX = 50

# Activity Streams Atom namespace
_ATOM_NS = "http://www.w3.org/2005/Atom"

# Maximum pages to fetch during date-cursor pagination (safety net)
_CAT7_MAX_PAGES = 25


# Secondary cache: stores the API-reported total comment count per issue key
# so attach_comments can set comments_truncated without an extra GET.
_comment_total_cache: dict = {}


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def fetch_all_comments(session, issue_key: str) -> list:
    """Fetch the full comment thread for a Jira issue, using the module-level cache.

    Returns a list of comment dicts (oldest -> newest), each with:
        {
            "author": "<displayName>",
            "created": "<ISO-8601>",
            "excerpt": "<plain text, ADF-flattened, <=500 chars, '...' if truncated>"
        }

    Caps at the 50 most-recent comments (newest 50 when total > 50, sorted
    oldest -> newest within that set). Populates _comment_total_cache[issue_key]
    with the raw API total so attach_comments can set comments_truncated.

    Returns [] on any fetch failure (graceful degradation). Uses _comment_cache
    to avoid duplicate GETs for the same key within a run.
    """
    if issue_key in _comment_cache:
        cached = _comment_cache[issue_key]
        return cached if cached is not None else []

    try:
        # Step 1: probe total with a minimal first request (maxResults=1).
        first_resp = session.get(
            f"/rest/api/3/issue/{issue_key}/comment",
            params={"startAt": 0, "maxResults": 1},
        )
        total = first_resp.get("total", 0)
        _comment_total_cache[issue_key] = total

        if total == 0:
            _comment_cache[issue_key] = []
            return []

        # Step 2: fetch the newest _COMMENTS_MAX comments.
        # If total > _COMMENTS_MAX, start from (total - _COMMENTS_MAX).
        fetch_start = max(0, total - _COMMENTS_MAX)
        comments_raw = []
        start_at = fetch_start
        page_size = 100
        while True:
            resp = session.get(
                f"/rest/api/3/issue/{issue_key}/comment",
                params={"startAt": start_at, "maxResults": page_size},
            )
            page = resp.get("comments", [])
            comments_raw.extend(page)
            start_at += len(page)
            page_total = resp.get("total", total)
            if start_at >= page_total or not page:
                break

        # Build output list (oldest -> newest within the fetched window)
        result = []
        for c in comments_raw:
            author_name = (c.get("author") or {}).get("displayName", "")
            created = c.get("created", "")
            body_raw = c.get("body", "")
            text = _adf_to_text(body_raw)
            text = re.sub(r"\s+", " ", text).strip()
            if len(text) > 500:
                excerpt = text[:500] + "..."
            else:
                excerpt = text
            result.append({
                "author": author_name,
                "created": created,
                "excerpt": excerpt,
            })

        _comment_cache[issue_key] = result
        return result

    except Exception as exc:
        print(f"[collect_jira] comment fetch failed for {issue_key}: {exc}", file=sys.stderr)
        # Cache the failure as None so we don't retry in the same run.
        _comment_cache[issue_key] = None
        return []


def attach_comments(session, issue_key: str, item: dict) -> None:
    """Fetch comments for issue_key and attach them to item in-place.

    Sets item['comments'] to the comment list ([] on failure or empty).
    Sets item['comments_truncated'] = True only when total > _COMMENTS_MAX;
    the field is absent otherwise (per spec, not set to False).

    Degrades gracefully: a fetch failure sets comments=[] and never raises.
    """
    comments = fetch_all_comments(session, issue_key)
    item["comments"] = comments
    total = _comment_total_cache.get(issue_key)
    if total is not None and total > _COMMENTS_MAX:
        item["comments_truncated"] = True


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def collect_jira(session, identity, window) -> dict:
    """Run all Jira collectors and return combined result dict.

    Args:
        session: AtlassianSession instance.
        identity: AtlassianIdentity with account_id, display_name, email.
        window: TimeWindow from lib.dates.

    Returns:
        dict with keys cat3_jira_done, cat4_jira_created,
        cat5_jira_comments, cat7_jira_grooming, cat8_in_progress,
        cat9_blocked.
    """
    result = {}
    result.update(_collect_cat3(session, identity, window))
    result.update(_collect_cat4(session, identity, window))
    result.update(_collect_cat5(session, identity, window))
    result.update(_collect_cat7(session, identity, window))
    result.update(_collect_cat8(session, identity))
    result.update(_collect_cat9(session, identity))
    return result


# ---------------------------------------------------------------------------
# CAT3: Tickets done / resolved
# ---------------------------------------------------------------------------

def _collect_cat3(session, identity, window) -> dict:
    """Fetch tickets resolved by the user in the time window.

    Tries two JQL strategies:
      1. Primary: resolutiondate in window AND assignee = accountId
      2. Fallback: status CHANGED TO done states DURING window AND assignee = accountId

    Returns merged deduplicated results.
    """
    try:
        account_id = identity.account_id
        start = window.jql_start
        end = window.jql_end

        primary_jql = (
            f'assignee = "{account_id}" '
            f'AND resolutiondate >= "{start}" '
            f'AND resolutiondate <= "{end}" '
            f'ORDER BY resolutiondate DESC'
        )
        fallback_jql = (
            f'assignee = "{account_id}" '
            f'AND status CHANGED TO (Done, Closed, Resolved) '
            f'DURING ("{start}", "{end}") '
            f'ORDER BY updated DESC'
        )
        fields = ["key", "summary", "status", "resolutiondate", "assignee",
                  "issuetype", "priority", "description"]

        primary_issues = _jql_search(session, primary_jql, fields)
        fallback_issues = _jql_search(session, fallback_jql, fields)

        # Merge, deduplicate by key
        seen = {}
        for issue in primary_issues + fallback_issues:
            key = issue.get("key", "")
            if key and key not in seen:
                seen[key] = issue

        items = []
        base_url = session.base_url
        for key, issue in seen.items():
            f = issue.get("fields") or {}
            item = {
                "key": key,
                "summary": f.get("summary", ""),
                "status": (f.get("status") or {}).get("name", ""),
                "issuetype": (f.get("issuetype") or {}).get("name", ""),
                "resolution_date": f.get("resolutiondate"),
                "priority": (f.get("priority") or {}).get("name", ""),
                "description_excerpt": _description_excerpt(f.get("description")),
                "url": _jira_url(base_url, key),
            }
            attach_comments(session, key, item)
            items.append(item)

        return {"cat3_jira_done": {"status": "ok", "count": len(items), "items": items, "error": None}}

    except Exception as exc:
        print(f"[collect_jira] CAT3 error: {exc}", file=sys.stderr)
        return {"cat3_jira_done": {"status": "error", "count": 0, "items": [], "error": str(exc)}}


# ---------------------------------------------------------------------------
# CAT4: Tickets created by user
# ---------------------------------------------------------------------------

def _collect_cat4(session, identity, window) -> dict:
    """Fetch tickets created/reported by the user in the time window."""
    try:
        account_id = identity.account_id
        start = window.jql_start
        end = window.jql_end

        jql = (
            f'reporter = "{account_id}" '
            f'AND created >= "{start}" '
            f'AND created <= "{end}" '
            f'ORDER BY created DESC'
        )
        fields = ["key", "summary", "status", "reporter", "creator", "created", "issuetype", "description"]
        issues = _jql_search(session, jql, fields)

        base_url = session.base_url
        items = []
        for issue in issues:
            key = issue.get("key", "")
            f = issue.get("fields") or {}
            item = {
                "key": key,
                "summary": f.get("summary", ""),
                "status": (f.get("status") or {}).get("name", ""),
                "issuetype": (f.get("issuetype") or {}).get("name", ""),
                "created": f.get("created"),
                "reporter": (f.get("reporter") or {}).get("displayName", ""),
                "creator": (f.get("creator") or {}).get("displayName", ""),
                "description_excerpt": _description_excerpt(f.get("description")),
                "url": _jira_url(base_url, key),
            }
            attach_comments(session, key, item)
            items.append(item)

        return {"cat4_jira_created": {"status": "ok", "count": len(items), "items": items, "error": None}}

    except Exception as exc:
        print(f"[collect_jira] CAT4 error: {exc}", file=sys.stderr)
        return {"cat4_jira_created": {"status": "error", "count": 0, "items": [], "error": str(exc)}}


# ---------------------------------------------------------------------------
# CAT5: Comments left by user
# ---------------------------------------------------------------------------

def _collect_cat5(session, identity, window) -> dict:
    """Find comments left by the user in the time window (two-step approach).

    Step 1: JQL prefilter to find candidate issues (assignee or reporter AND
            updated in window -- broad net to avoid missing comments on issues
            where the user is neither assignee nor reporter).
    Step 2: Per-issue comment fetch with pagination; filter by author accountId
            AND created in window.
    """
    try:
        account_id = identity.account_id
        start = window.jql_start

        # Step 1: broad JQL prefilter -- capped at CAT5_N_BUDGET to prevent
        # unbounded N+1 comment fetches on wide windows.
        prefilter_jql = (
            f'(assignee = "{account_id}" OR reporter = "{account_id}") '
            f'AND updated >= "{start}" '
            f'ORDER BY updated DESC'
        )
        candidate_fields = ["key", "summary", "updated"]
        candidates = _jql_search(session, prefilter_jql, candidate_fields,
                                 max_results=CAT5_N_BUDGET)
        candidate_issues_scanned = len(candidates)

        base_url = session.base_url
        items = []

        # Step 2: per-issue comment scan
        for issue in candidates:
            key = issue.get("key", "")
            f = issue.get("fields") or {}
            summary = f.get("summary", "")
            try:
                # Paginate comments
                start_at = 0
                max_results = 100
                while True:
                    resp = session.get(
                        f"/rest/api/3/issue/{key}/comment",
                        params={"startAt": start_at, "maxResults": max_results},
                    )
                    comments = resp.get("comments", [])
                    for comment in comments:
                        author_id = (comment.get("author") or {}).get("accountId", "")
                        created = comment.get("created")
                        if author_id == account_id and _in_window_str(created, window):
                            body_raw = comment.get("body", "")
                            items.append({
                                "issue_key": key,
                                "issue_summary": summary,
                                "issue_url": _jira_url(base_url, key),
                                "comment_created": created,
                                "comment_body_text": _adf_to_text(body_raw),
                            })
                    total = resp.get("total", 0)
                    start_at += len(comments)
                    if start_at >= total or not comments:
                        break
            except Exception as exc:
                print(f"[collect_jira] CAT5 comment fetch error for {key}: {exc}", file=sys.stderr)
                continue

        return {
            "cat5_jira_comments": {
                "status": "ok",
                "count": len(items),
                "items": items,
                "candidate_issues_scanned": candidate_issues_scanned,
                "error": None,
            }
        }

    except Exception as exc:
        print(f"[collect_jira] CAT5 error: {exc}", file=sys.stderr)
        return {
            "cat5_jira_comments": {
                "status": "error",
                "count": 0,
                "items": [],
                "candidate_issues_scanned": 0,
                "error": str(exc),
            }
        }


# ---------------------------------------------------------------------------
# CAT7: Grooming edits (Activity Streams feed)
# ---------------------------------------------------------------------------

def _collect_cat7(session, identity, window) -> dict:
    """Find field edits (grooming) made by the user in the time window.

    Uses the Atlassian Activity Streams Atom feed at /plugins/servlet/streams.
    This endpoint is comprehensive -- it covers ALL issues the user touched,
    not just those they own or report. One feed call typically covers a full
    week; pagination uses date-cursor windowing (not rel="next" links).

    Feed response is Atom XML. Each <entry> names the actor, the verb, and
    the target issue in its <title>. The feed already filters by user (via
    the 'user IS <accountId>' streams parameter) so only the user's activity
    appears.

    Limitations accepted per spec:
    - The feed names WHICH field changed but not old->new values.
    - Multiple edits in quick succession may collapse to "updated N fields".
    - This is fine: CAT7 summarises grooming breadth, not value deltas.
    """
    try:
        account_id = identity.account_id

        # Epoch milliseconds for the Activity Streams date filter.
        start_ms = int(window.start.timestamp() * 1000)
        end_ms   = int(window.end.timestamp() * 1000)

        base_url = session.base_url
        items = []
        seen_ids: set = set()
        pages_fetched = 0
        window_start_ms = start_ms

        # Date-cursor pagination: if a page is full (maxResults entries) and
        # the oldest entry is still after the window start, re-request with
        # the window end clamped to oldest - 1ms.  Cap at _CAT7_MAX_PAGES.
        current_end_ms = end_ms
        max_results = 1000

        while pages_fetched < _CAT7_MAX_PAGES:
            params = [
                ("streams", f"user IS {account_id}"),
                ("streams", f"update-date BETWEEN {window_start_ms} {current_end_ms}"),
                ("maxResults", str(max_results)),
            ]
            print(
                f"[collect_jira] CAT7 feed page {pages_fetched + 1}: "
                f"BETWEEN {window_start_ms} {current_end_ms}",
                file=sys.stderr,
            )
            raw = session.get_text("/plugins/servlet/streams", params)
            pages_fetched += 1

            entries = _parse_atom_entries(raw, account_id, window, seen_ids)
            items.extend(entries["items"])
            seen_ids.update(entries["entry_ids"])

            # Pagination: if we got a full page and the oldest is still inside
            # the window, cursor back from the oldest timestamp.
            if entries["count"] >= max_results and entries["oldest_ms"] is not None:
                oldest_ms = entries["oldest_ms"]
                if oldest_ms > window_start_ms:
                    # Move the end back to just before the oldest entry.
                    current_end_ms = oldest_ms - 1
                    continue
            # Not a full page, or oldest is at/before window start -- done.
            break

        if pages_fetched >= _CAT7_MAX_PAGES:
            print(
                f"[collect_jira] CAT7 hit page cap ({_CAT7_MAX_PAGES}); result may be incomplete.",
                file=sys.stderr,
            )

        # Build qualitative summary: field kinds by frequency (no counts emitted)
        # and the most-groomed issues by identity (no counts emitted).
        field_counts_internal: dict = {}
        issue_event_counts: dict = {}
        for item in items:
            field = item.get("field", "")
            if field:
                field_counts_internal[field] = field_counts_internal.get(field, 0) + 1
            key = item.get("issue_key", "")
            if key:
                issue_event_counts[key] = issue_event_counts.get(key, 0) + 1

        # fields_by_frequency: field kinds ordered most-frequent → least-frequent.
        # Counts are used only for ordering; they are NOT emitted.
        fields_by_frequency = [
            field for field, _ in sorted(
                field_counts_internal.items(), key=lambda kv: kv[1], reverse=True
            )
        ]

        # top_areas: up to 6 most-groomed issues by event count, identity only.
        top_keys = sorted(
            issue_event_counts, key=lambda k: issue_event_counts[k], reverse=True
        )[:6]

        # Build a key→(summary, parent) index from items (first occurrence wins).
        key_meta: dict = {}
        for item in items:
            k = item.get("issue_key", "")
            if k and k not in key_meta:
                # items carry title/action but not summary/parent; parent info
                # is not available from the Activity Streams feed, so we carry
                # what we have (title as a proxy summary) and leave parent null.
                key_meta[k] = {
                    "key": k,
                    "summary": item.get("title", ""),
                    "parent": None,
                }

        top_areas = [key_meta[k] for k in top_keys if k in key_meta]

        return {
            "cat7_jira_grooming": {
                "status": "ok",
                "count": len(items),
                "items": items,
                "summary": {
                    "fields_by_frequency": fields_by_frequency,
                    "top_areas": top_areas,
                },
                "error": None,
            }
        }

    except Exception as exc:
        print(f"[collect_jira] CAT7 error: {exc}", file=sys.stderr)
        return {
            "cat7_jira_grooming": {
                "status": "error",
                "count": 0,
                "items": [],
                "summary": {"fields_by_frequency": [], "top_areas": []},
                "error": str(exc),
            }
        }


# ---------------------------------------------------------------------------
# CAT8: Current in-progress tickets (NOT time-windowed)
# ---------------------------------------------------------------------------

def _collect_cat8(session, identity) -> dict:
    """Fetch tickets currently in progress for the user (current snapshot).

    Uses statusCategory = "In Progress" to capture all issue types whose
    status maps to the In Progress category (e.g. In Development, In Scoping,
    In Validation, In Implementation). Does NOT filter by time window.

    Returns:
        dict with key cat8_in_progress.
    """
    try:
        account_id = identity.account_id
        jql = (
            f'assignee = "{account_id}" '
            f'AND statusCategory = "In Progress" '
            f'ORDER BY updated DESC'
        )
        fields = ["key", "summary", "status", "statusCategory", "issuetype",
                  "priority", "updated", "parent"]
        issues = _jql_search(session, jql, fields, max_results=200)

        base_url = session.base_url
        items = []
        for issue in issues:
            key = issue.get("key", "")
            f = issue.get("fields") or {}
            parent_field = f.get("parent")
            parent = None
            if parent_field:
                parent = {
                    "key": parent_field.get("key", ""),
                    "summary": (parent_field.get("fields") or {}).get("summary", ""),
                }
            item = {
                "key": key,
                "summary": f.get("summary", ""),
                "status": (f.get("status") or {}).get("name", ""),
                "status_category": ((f.get("status") or {}).get("statusCategory") or {}).get("name", ""),
                "issuetype": (f.get("issuetype") or {}).get("name", ""),
                "priority": (f.get("priority") or {}).get("name", ""),
                "updated": f.get("updated"),
                "parent": parent,
                "url": _jira_url(base_url, key),
            }
            attach_comments(session, key, item)
            items.append(item)

        return {"cat8_in_progress": {"status": "ok", "count": len(items), "items": items, "error": None}}

    except Exception as exc:
        print(f"[collect_jira] CAT8 error: {exc}", file=sys.stderr)
        return {"cat8_in_progress": {"status": "error", "count": 0, "items": [], "error": str(exc)}}


# ---------------------------------------------------------------------------
# CAT9: Current blocked tickets (NOT time-windowed)
# ---------------------------------------------------------------------------

def _collect_cat9(session, identity) -> dict:
    """Fetch tickets currently blocked for the user (current snapshot).

    Uses status = "Blocked" directly. "Blocked" has statusCategory "To Do"
    so it is correctly NOT included in cat8_in_progress. Does NOT filter
    by time window.

    Returns:
        dict with key cat9_blocked.
    """
    try:
        account_id = identity.account_id
        jql = (
            f'assignee = "{account_id}" '
            f'AND status = "Blocked" '
            f'ORDER BY updated DESC'
        )
        fields = ["key", "summary", "status", "statusCategory", "issuetype",
                  "priority", "updated", "parent"]
        issues = _jql_search(session, jql, fields, max_results=200)

        base_url = session.base_url
        items = []
        for issue in issues:
            key = issue.get("key", "")
            f = issue.get("fields") or {}
            parent_field = f.get("parent")
            parent = None
            if parent_field:
                parent = {
                    "key": parent_field.get("key", ""),
                    "summary": (parent_field.get("fields") or {}).get("summary", ""),
                }
            item = {
                "key": key,
                "summary": f.get("summary", ""),
                "status": (f.get("status") or {}).get("name", ""),
                "status_category": ((f.get("status") or {}).get("statusCategory") or {}).get("name", ""),
                "issuetype": (f.get("issuetype") or {}).get("name", ""),
                "priority": (f.get("priority") or {}).get("name", ""),
                "updated": f.get("updated"),
                "parent": parent,
                "url": _jira_url(base_url, key),
            }
            attach_comments(session, key, item)
            items.append(item)

        return {"cat9_blocked": {"status": "ok", "count": len(items), "items": items, "error": None}}

    except Exception as exc:
        print(f"[collect_jira] CAT9 error: {exc}", file=sys.stderr)
        return {"cat9_blocked": {"status": "error", "count": 0, "items": [], "error": str(exc)}}


def _parse_atom_entries(xml_text: str, account_id: str, window, seen_ids: set) -> dict:
    """Parse an Atom feed page and extract grooming-relevant entries.

    Returns a dict with:
      - items: list of {issue_key, timestamp, field, action, title}
      - entry_ids: set of entry <id> values seen on this page (for dedup)
      - count: total entries on this page (before filtering/dedup)
      - oldest_ms: oldest entry timestamp in epoch ms (for cursor pagination)
    """
    from datetime import datetime, timezone

    ns = {"atom": _ATOM_NS}
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        print(f"[collect_jira] CAT7 Atom parse error: {exc}", file=sys.stderr)
        return {"items": [], "entry_ids": set(), "count": 0, "oldest_ms": None}

    # ElementTree tag format with namespace: {http://...}tag
    entry_tag = f"{{{_ATOM_NS}}}entry"
    entries_on_page = root.findall(entry_tag)

    items = []
    entry_ids: set = set()
    oldest_ms = None
    count = len(entries_on_page)

    for entry in entries_on_page:
        # Entry <id> for deduplication
        id_el = entry.find(f"{{{_ATOM_NS}}}id")
        entry_id = id_el.text if id_el is not None else ""
        if entry_id in seen_ids:
            continue

        # Published timestamp
        published_el = entry.find(f"{{{_ATOM_NS}}}published")
        ts_str = (published_el.text or "").strip() if published_el is not None else ""
        ts = _parse_iso(ts_str)
        if ts is None:
            # Fall back to <updated>
            updated_el = entry.find(f"{{{_ATOM_NS}}}updated")
            ts_str = (updated_el.text or "").strip() if updated_el is not None else ""
            ts = _parse_iso(ts_str)

        # Client-side window filter (feed's date filter is coarse-safe)
        if ts is None or not (window.start <= ts <= window.end):
            if entry_id:
                entry_ids.add(entry_id)
            # Track oldest for cursor even if outside window
            if ts is not None:
                ts_ms = int(ts.timestamp() * 1000)
                if oldest_ms is None or ts_ms < oldest_ms:
                    oldest_ms = ts_ms
            continue

        ts_ms = int(ts.timestamp() * 1000)
        if oldest_ms is None or ts_ms < oldest_ms:
            oldest_ms = ts_ms

        if entry_id:
            entry_ids.add(entry_id)

        # Prefer the browse/ href for issue key extraction
        issue_key = ""
        link_el = entry.find(f"{{{_ATOM_NS}}}link[@rel='alternate']")
        if link_el is not None:
            href = link_el.get("href", "")
            m = re.search(r"/browse/([A-Z][A-Z0-9]+-\d+)", href)
            if m:
                issue_key = m.group(1)

        # Title: strip HTML tags/entities to clean phrase
        title_el = entry.find(f"{{{_ATOM_NS}}}title")
        raw_title = (title_el.text or "").strip() if title_el is not None else ""
        clean_title = _strip_html(raw_title)

        # Fall back to title for issue key if not found in href
        if not issue_key:
            m = re.search(r"\b([A-Z][A-Z0-9]+-\d+)\b", clean_title)
            if m:
                issue_key = m.group(1)

        # Parse field/action from title
        field, action = _parse_title_field(clean_title)

        items.append({
            "issue_key": issue_key,
            "timestamp": ts.isoformat(),
            "field": field,
            "action": action,
            "title": clean_title,
        })

    return {
        "items": items,
        "entry_ids": entry_ids,
        "count": count,
        "oldest_ms": oldest_ms,
    }


def _parse_iso(ts_str: str):
    """Parse an ISO-8601 timestamp string to an aware datetime, or None on failure."""
    if not ts_str:
        return None
    try:
        from datetime import datetime, timezone
        normalized = ts_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def _strip_html(text: str) -> str:
    """Remove HTML tags, decode common HTML entities, and normalise whitespace."""
    # Remove tags
    text = re.sub(r"<[^>]+>", "", text)
    # Decode common entities
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&quot;", '"').replace("&#39;", "'").replace("&nbsp;", " ")
    # Collapse runs of whitespace (including newlines) to a single space
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _parse_title_field(title: str) -> tuple:
    """Extract a (field, action) pair from a cleaned Activity Streams entry title.

    Handles patterns like:
      "Ada Lovelace updated the Description of PM-40994 - ..."
      "Ada Lovelace changed the status to In refinement on PM-40985"
      "Ada Lovelace updated the Goals of PM-8014"
      "Ada Lovelace updated 2 fields of PM-41001"
      "Ada Lovelace changed the Parent to 'PM-27719' on PM-41001"

    Returns (field, action) where field is the field name (lowercase) or ""
    if not confidently parsed, and action is a short descriptive phrase.
    Falls back to the cleaned title as the action.
    """
    # "changed the <Field> to <value> on KEY"
    # Covers: status, parent, Labels, Priority, Assignee, Fix Version, etc.
    m = re.search(
        r"changed the ([A-Za-z][A-Za-z ]+?) to (.+?)(?:\s+on\s+[A-Z][A-Z0-9]+-\d+|$)",
        title,
    )
    if m:
        field = m.group(1).strip().lower()
        value = m.group(2).strip()
        return (field, f"{field} changed to {value}")

    # "updated the <Field> of KEY" or "updated the <Field> of KEY - ..."
    m = re.search(r"updated the ([A-Za-z ]+?) of [A-Z][A-Z0-9]+-\d+", title)
    if m:
        field = m.group(1).strip().lower()
        return (field, f"{field} updated")

    # "updated N fields of KEY"
    m = re.search(r"updated (\d+) fields? of [A-Z][A-Z0-9]+-\d+", title)
    if m:
        return ("multiple", f"updated {m.group(1)} fields")

    # "commented on KEY"
    if re.search(r"commented on\s+[A-Z][A-Z0-9]+-\d+", title):
        return ("comment", "commented")

    # Fallback: return empty field and the full cleaned title as action
    return ("", title)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _jql_search(session, jql: str, fields: list, max_results: int = None) -> list:
    """Execute a JQL search via POST /rest/api/3/search/jql and return issues.

    Uses POST (not GET) as required by the Jira REST API v3 search endpoint.
    """
    body = {
        "jql": jql,
        "fields": fields,
        "maxResults": max_results or 200,
    }
    print(f"[collect_jira] JQL: {jql[:120]}...", file=sys.stderr)
    data = session.post_json("/rest/api/3/search/jql", body)
    return data.get("issues", [])


def _in_window_str(dt_str: str | None, window) -> bool:
    """Check whether an ISO-8601 datetime string falls in the window.

    Inline version of event_in_window from dates.py (avoids cross-import).
    Handles both Z-suffix and +HH:MM offset strings. Returns False on None
    or parse failure.
    """
    if not dt_str:
        return False
    try:
        from datetime import datetime, timezone
        normalized = dt_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return window.start <= dt <= window.end
    except (ValueError, TypeError):
        return False


def _adf_to_text(adf) -> str:
    """Recursively flatten an Atlassian Document Format (ADF) node to plain text.

    Handles:
    - str passthrough (plain text body, not ADF)
    - dict with type="text": returns .get("text", "")
    - dict with "content" list: recurse and join
    - Other types: empty string
    """
    if isinstance(adf, str):
        return adf
    if isinstance(adf, dict):
        if adf.get("type") == "text":
            return adf.get("text", "")
        content = adf.get("content")
        if content and isinstance(content, list):
            return " ".join(_adf_to_text(child) for child in content)
    return ""


def _description_excerpt(description) -> str | None:
    """Flatten a Jira issue description (ADF or plain text) to a <=500-char excerpt.

    Returns None if the description is absent or yields only whitespace after
    flattening. Appends "…" if the text was truncated.
    """
    if description is None:
        return None
    text = _adf_to_text(description)
    # Collapse whitespace runs (newlines, tabs, multiple spaces → single space)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return None
    if len(text) <= 500:
        return text
    return text[:500] + "…"


def _jira_url(base_url: str, key: str) -> str:
    """Construct a Jira browse URL for an issue key."""
    return f"{base_url}/browse/{key}"
