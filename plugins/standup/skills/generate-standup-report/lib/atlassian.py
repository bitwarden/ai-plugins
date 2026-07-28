"""
atlassian.py -- Shared Atlassian HTTP library

Provides Basic-auth session construction, retrying single-URL fetcher, and
generic paginator for Jira and Confluence REST APIs. Modeled on the auth and
paginator patterns in jira-sync/fetch.py.

All methods are read-only except post_json, which is used only for
POST /rest/api/3/search/jql (a read-only search endpoint in Jira's API).
No PUT, PATCH, or DELETE methods are provided.

Environment variables consumed at __init__ time:
    JIRA_API_TOKEN  (required) Atlassian API token or PAT
    JIRA_EMAIL      (required) Atlassian account email -- no default; must be set explicitly
    JIRA_BASE_URL   (required) Atlassian base URL -- no default; must be set explicitly
"""

import base64
import json
import os
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# Global default socket timeout applied at module import.
# This covers ALL socket operations (connect, read, write) including the TCP
# handshake phase -- which urlopen(timeout=N) alone does NOT cover when the
# remote server accepts the TCP connection but then stalls before sending HTTP
# headers.  Without this, a half-open connection can block indefinitely even
# when individual urlopen calls specify a timeout.
socket.setdefaulttimeout(30)


class AtlassianAPIError(Exception):
    """Raised when an Atlassian API call returns a non-retriable HTTP error."""

    def __init__(self, status: int, url: str, body: str):
        self.status = status
        self.url = url
        self.body = body
        super().__init__(f"HTTP {status} fetching {url}: {body[:200]}")


class AtlassianSession:
    """Authenticated session for Atlassian REST APIs (Jira + Confluence).

    Reads credentials from environment on construction. Raises SystemExit(1)
    if JIRA_API_TOKEN is absent so callers get a clear error message.
    """

    def __init__(self):
        token = os.environ.get("JIRA_API_TOKEN")
        if not token:
            print(
                "Error: required environment variable JIRA_API_TOKEN is not set.",
                file=sys.stderr,
            )
            sys.exit(1)

        email = os.environ.get("JIRA_EMAIL")
        if not email:
            print(
                "Error: JIRA_EMAIL must be set. "
                "Set it to your Atlassian account email (e.g. user@example.com).",
                file=sys.stderr,
            )
            sys.exit(1)

        base_url = os.environ.get("JIRA_BASE_URL")
        if not base_url:
            print(
                "Error: JIRA_BASE_URL must be set. "
                "Set it to your Atlassian base URL (e.g. https://yourorg.atlassian.net).",
                file=sys.stderr,
            )
            sys.exit(1)
        base_url = base_url.rstrip("/")

        _auth_raw = base64.b64encode(f"{email}:{token}".encode()).decode()
        self._headers = {
            "Authorization": f"Basic {_auth_raw}",
            "Accept": "application/json",
        }
        self.base_url = base_url

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, path: str, params: dict = None) -> dict:
        """Issue an authenticated GET and return parsed JSON.

        Prepends base_url when path does not start with 'http'.
        Encodes params dict into query string if provided.
        """
        url = path if path.startswith("http") else self.base_url + path
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        return self._fetch(url)

    def get_text(self, path: str, params: list = None) -> str:
        """Issue an authenticated GET and return the raw response body as str.

        Unlike get(), this method:
        - Accepts params as a list of (key, value) tuples to support repeated
          keys (e.g. multiple 'streams=' filters for the Activity Streams feed).
        - Returns the decoded response body as a plain string (not JSON).
        - Prepends base_url when path does not start with 'http'.
        - Propagates HTTP errors (raises AtlassianAPIError on non-2xx).
        - Respects the global 30s socket timeout set at module load.

        Used by the Atom-feed based CAT7 collector which calls:
            /plugins/servlet/streams
        with repeated 'streams' query parameters -- a pattern urllib.parse.urlencode
        handles correctly when given a list of (key, value) tuples.
        """
        url = path if path.startswith("http") else self.base_url + path
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        headers = {
            **self._headers,
            "Accept": "application/atom+xml, text/xml, */*",
        }
        req = urllib.request.Request(url, headers=headers)
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return resp.read().decode("utf-8", errors="replace")
            except urllib.error.HTTPError as exc:
                body = exc.read().decode(errors="replace")
                raise AtlassianAPIError(exc.code, url, body)
            except (urllib.error.URLError, OSError) as exc:
                if attempt < 2:
                    wait = 2 ** attempt
                    print(
                        f"Warning: transient error fetching {url} ({exc}), retrying in {wait}s...",
                        file=sys.stderr,
                    )
                    time.sleep(wait)
                else:
                    raise

    def post_json(self, path: str, body: dict) -> dict:
        """Issue an authenticated POST with a JSON body and return parsed JSON.

        Used only for read-only search endpoints (e.g. POST /rest/api/3/search/jql).
        Retries on 5xx; raises AtlassianAPIError on 4xx.
        """
        url = path if path.startswith("http") else self.base_url + path
        encoded = json.dumps(body).encode()
        headers = {
            **self._headers,
            "Content-Type": "application/json",
        }
        req = urllib.request.Request(url, data=encoded, headers=headers, method="POST")
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return json.loads(resp.read().decode())
            except urllib.error.HTTPError as exc:
                body_text = exc.read().decode(errors="replace")
                if exc.code >= 500 and attempt < 2:
                    wait = 2 ** attempt
                    print(
                        f"Warning: HTTP {exc.code} POST {url}, retrying in {wait}s...",
                        file=sys.stderr,
                    )
                    time.sleep(wait)
                    continue
                raise AtlassianAPIError(exc.code, url, body_text)
            except (urllib.error.URLError, OSError) as exc:
                if attempt < 2:
                    wait = 2 ** attempt
                    print(
                        f"Warning: transient error POST {url} ({exc}), retrying in {wait}s...",
                        file=sys.stderr,
                    )
                    time.sleep(wait)
                else:
                    raise

    def paginate(
        self,
        path: str,
        page_key: str = "values",
        params: dict = None,
        max_results: int = None,
    ) -> list:
        """Fetch all pages from a paginated endpoint and return aggregated items.

        Auto-detects pagination mode from the first response:
        - Cursor mode (Jira v3): presence of 'nextPageToken' or 'isLast' key
        - Confluence CQL mode: presence of '_links' with 'next'
        - Offset mode: falls back to startAt + total arithmetic

        Args:
            path: API path (prepended with base_url if not absolute).
            page_key: Key in response containing the items list.
            params: Additional query parameters.
            max_results: Stop after this many accumulated items.
        """
        url = path if path.startswith("http") else self.base_url + path
        page_size = 50
        base_params = dict(params or {})
        results = []

        # First page
        first_params = {**base_params, "startAt": 0, "maxResults": page_size}
        first_url = f"{url}?{urllib.parse.urlencode(first_params)}"
        data = self._fetch(first_url)
        page = data.get(page_key, [])
        results.extend(page)

        if "nextPageToken" in data or "isLast" in data:
            # Jira cursor-based mode
            while not data.get("isLast", True) and page:
                if max_results and len(results) >= max_results:
                    break
                token = data.get("nextPageToken", "")
                next_params = {
                    **base_params,
                    "maxResults": page_size,
                    "nextPageToken": token,
                }
                next_url = f"{url}?{urllib.parse.urlencode(next_params)}"
                data = self._fetch(next_url)
                page = data.get(page_key, [])
                results.extend(page)

        elif "_links" in data and "next" in data.get("_links", {}):
            # Confluence CQL link-following mode
            next_href = data["_links"]["next"]
            while next_href and page:
                if max_results and len(results) >= max_results:
                    break
                # next_href is a relative path
                next_url = (
                    next_href
                    if next_href.startswith("http")
                    else self.base_url + next_href
                )
                data = self._fetch(next_url)
                page = data.get(page_key, [])
                results.extend(page)
                next_href = data.get("_links", {}).get("next")

        else:
            # Offset-based mode
            total = data.get("total", 0)
            start_at = len(page)
            while start_at < total and page:
                if max_results and len(results) >= max_results:
                    break
                next_params = {
                    **base_params,
                    "startAt": start_at,
                    "maxResults": page_size,
                }
                next_url = f"{url}?{urllib.parse.urlencode(next_params)}"
                data = self._fetch(next_url)
                page = data.get(page_key, [])
                results.extend(page)
                start_at += len(page)

        if max_results and len(results) > max_results:
            results = results[:max_results]

        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch(self, url: str) -> dict:
        """Fetch a single URL with retry on transient network errors.

        Retries up to 3 times with exponential backoff (1s, 2s, 4s) on
        URLError/OSError. Raises AtlassianAPIError immediately on HTTP 4xx/5xx
        (no retry for HTTP errors -- only transient transport errors are retried).
        """
        req = urllib.request.Request(url, headers=self._headers)
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return json.loads(resp.read().decode())
            except urllib.error.HTTPError as exc:
                body = exc.read().decode(errors="replace")
                raise AtlassianAPIError(exc.code, url, body)
            except (urllib.error.URLError, OSError) as exc:
                if attempt < 2:
                    wait = 2 ** attempt
                    print(
                        f"Warning: transient error fetching {url} ({exc}), retrying in {wait}s...",
                        file=sys.stderr,
                    )
                    time.sleep(wait)
                else:
                    raise
