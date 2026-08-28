#!/usr/bin/env python3
"""Fetch a Bitwarden Mailcatcher message matching a recipient + subject, and
print the first matching URL from its body on stdout.

Exit 0 on success (prints the extracted URL on stdout).
Exit 1: no matching message found, or a matched message had no local-host URL
        (diagnostic on stderr).
Exit 2: usage error.
Exit 3: Mailcatcher unreachable or returned invalid JSON.

Usage:
  read_mailcatcher.py --recipient <email> [--pattern <subject-keyword>]
                      [--link-filter <regex>]

--pattern is optional. Omit (or pass empty) to match any subject and just take
the most recent message for the recipient.

The Mailcatcher endpoint is the same across Bitwarden dev environments, so the
base URL is fixed at http://localhost:1080 and cannot be overridden. Extracted
URLs are still restricted to a local dev allowlist; extend it (never replace it)
for a custom local hostname with the comma-separated PLAYWRIGHT_TESTING_ALLOWED_HOSTS
env var.

Defaults:
  --link-filter: verify|confirm|signup|token|trial|login|finish-signup

Designed to be called via the Bash tool. ../references/manual-api-walkthrough.md
documents the underlying Mailcatcher REST API this wraps.
"""
import argparse
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_MAILCATCHER_URL = "http://localhost:1080"
DEFAULT_LINK_FILTER = "verify|confirm|signup|token|trial|login|finish-signup"
# Local dev hosts allowed for extracted URLs. Extend (never replace) via the
# comma-separated env var PLAYWRIGHT_TESTING_ALLOWED_HOSTS.
DEFAULT_ALLOWED_HOSTS = ("localhost", "127.0.0.1", "::1", "bitwarden.test")
# Whitespace terminates a URL. grep is line-based, so the bash original could
# never match across a newline; excluding all whitespace preserves that.
URL_PATTERN = re.compile(r'https?://[^\s>")]+')
REQUEST_TIMEOUT = 5
RETRY_DELAY = 3

EXIT_OK = 0
EXIT_NO_MATCH = 1
EXIT_USAGE = 2
EXIT_UNREACHABLE = 3


class Unreachable(Exception):
    """Mailcatcher could not be reached or returned something unparseable."""


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Never follow 3xx redirects, matching curl's default (no -L).

    The stdlib's default opener installs a HTTPRedirectHandler that follows a
    301/302/303/307 Location header with no second check, which would let a
    redirect return content from a host that was never validated. Returning
    None from redirect_request tells the base handler not to redirect; it
    then falls through to HTTPDefaultErrorHandler, which raises HTTPError for
    the halted 3xx status. _http_get catches that HTTPError and returns the
    3xx response's own body without ever requesting the Location target,
    matching curl -fsS with no -L: -f only fails on status >= 400, so a
    halted redirect is a success that yields the redirect response's body.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def allowed_hosts(env):
    """Local dev hosts allowed for extracted URLs.

    The defaults are extended (never replaced) by the comma-separated
    PLAYWRIGHT_TESTING_ALLOWED_HOSTS env var. That var is operator-supplied
    (a real environment assignment, not model-constructed argv), so it stays
    outside the auto-approved `script:*` Bash grant and is a safe way to widen
    the allowlist for a custom local hostname.
    """
    hosts = [host.lower() for host in DEFAULT_ALLOWED_HOSTS]
    for entry in env.get("PLAYWRIGHT_TESTING_ALLOWED_HOSTS", "").split(","):
        entry = entry.strip().lower()
        if entry:
            hosts.append(entry)
    return tuple(hosts)


def _http_get(url):
    """GET url and return the body as text. Raises Unreachable on failure.

    Mirrors curl -fsS with no -L: -f fails only on an HTTP status >= 400.
    A halted 3xx (see _NoRedirectHandler) is not a failure under -f, so it
    is treated the same as any other success and its own body is returned;
    the Location target is never requested. Status >= 400 raises
    Unreachable, as does any transport failure.

    No TLS bypass here: the bash original used plain `curl -fsS` with no
    `-k`, so an https base gets normal certificate verification. The base is
    the fixed local http://localhost:1080 endpoint, not a caller-supplied
    value, so there is no untrusted host to validate before the request.
    """
    opener = urllib.request.build_opener(_NoRedirectHandler)
    try:
        with opener.open(url, timeout=REQUEST_TIMEOUT) as response:
            return response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as err:
        if 300 <= err.code < 400:
            return err.read().decode("utf-8", errors="replace")
        raise Unreachable(str(err))
    except (urllib.error.URLError, OSError) as err:
        raise Unreachable(str(err))


def _http_get_or_empty(url):
    """curl -fsS ... || true: a failed body fetch yields empty, not an error."""
    try:
        return _http_get(url)
    except Unreachable:
        return ""


def fetch_messages(base):
    body = _http_get(f"{base}/messages")
    try:
        messages = json.loads(body)
    except ValueError as err:
        raise Unreachable(f"invalid JSON from {base}/messages: {err}")
    if not isinstance(messages, list):
        raise Unreachable(f"expected a JSON array from {base}/messages")
    return messages


def select_message(messages, recipient, pattern):
    """Id of the newest message matching the recipient and optional pattern.

    A message with no `id` is dropped rather than indexed into. Mailcatcher
    always sends one, but keying `max` on `msg["id"]` turned a malformed entry
    into a KeyError that escaped this script's documented exit codes; an
    unusable entry is simply not a candidate.
    """
    recipient = recipient.lower()
    pattern = (pattern or "").lower()
    matches = [
        msg
        for msg in messages
        if isinstance(msg, dict)
        and msg.get("id") is not None
        and any(recipient in str(entry).lower() for entry in msg.get("recipients", []))
        and (not pattern or pattern in str(msg.get("subject", "")).lower())
    ]
    if not matches:
        return None
    return max(matches, key=lambda msg: msg["id"])["id"]


def fetch_body(base, message_id):
    body = _http_get_or_empty(f"{base}/messages/{message_id}.plain")
    if not body:
        print(
            f"WARNING: plain body empty for message {message_id}; "
            "using HTML body for URL extraction",
            file=sys.stderr,
        )
        # HTML href attributes carry entity-encoded ampersands (`&amp;`)
        # between query params. Unescaping here, on the HTML branch only, keeps
        # the plain path byte-exact while making the extracted link usable
        # rather than corrupt from the first `&` onward. Whitespace-terminated
        # URL matching is unaffected: `&amp;`/`%40` are not whitespace either way.
        body = html.unescape(_http_get_or_empty(f"{base}/messages/{message_id}.html"))
    return body


def matching_urls(body, link_filter):
    """Every URL in body matching link_filter, in document order.

    The caller (attempt) applies the local-host preference on top of this: an
    earlier non-local link that happens to match the filter (a marketing or
    help footer link, say) must not mask a later local action link, so the
    caller walks the full ordered list rather than taking the first match here.
    """
    try:
        return [
            candidate
            for candidate in URL_PATTERN.findall(body or "")
            if re.search(link_filter, candidate, re.IGNORECASE)
        ]
    except re.error:
        # Mirrors grep -iE with a malformed ERE: it errors out and yields no
        # match rather than a stack trace, so this falls through to the
        # caller's existing no-URL-found NO_MATCH branch.
        return []


def is_local(url, allowed):
    try:
        host = (urllib.parse.urlparse(url).hostname or "").lower()
    except ValueError:
        return False
    return host in allowed


def attempt(base, recipient, pattern, link_filter, allowed):
    """One pass. Returns (code, url_or_None).

    code 0 with a URL on success; 1 when no message matched (retryable);
    2 when a message matched but yielded no usable URL (not retryable);
    3 when Mailcatcher is unreachable (not retryable).
    """
    try:
        messages = fetch_messages(base)
    except Unreachable as err:
        print(f"ERROR: Mailcatcher unreachable at {base}: {err}", file=sys.stderr)
        return 3, None
    message_id = select_message(messages, recipient, pattern)
    if message_id is None:
        return 1, None
    candidates = matching_urls(fetch_body(base, message_id), link_filter)
    if not candidates:
        print(
            f"NO_MATCH: message {message_id} matched but contained no URL "
            f"filtered by '{link_filter}'",
            file=sys.stderr,
        )
        return 2, None
    url = next((c for c in candidates if is_local(c, allowed)), None)
    if url is None:
        print(
            f"NO_MATCH: extracted URL '{candidates[0]}' is not a local dev host",
            file=sys.stderr,
        )
        return 2, None
    return 0, url


def main(argv, env):
    parser = argparse.ArgumentParser(
        prog="read_mailcatcher.py",
        description="Print the first matching URL from a Mailcatcher message.",
    )
    parser.add_argument("--recipient", required=True)
    parser.add_argument("--pattern", default="")
    parser.add_argument("--link-filter", default=DEFAULT_LINK_FILTER)
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else EXIT_USAGE

    if not args.recipient.strip():
        print("ERROR: --recipient is required", file=sys.stderr)
        return EXIT_USAGE

    # The Mailcatcher endpoint is identical across Bitwarden dev environments,
    # so the base URL is fixed here rather than taken from argv or the
    # environment. Keeping it out of the auto-approved `script:*` argv shape
    # means a granted call can never point the fetch at an arbitrary host.
    base = DEFAULT_MAILCATCHER_URL
    allowed = allowed_hosts(env)
    settled = {3: EXIT_UNREACHABLE, 2: EXIT_NO_MATCH}

    code, url = attempt(base, args.recipient, args.pattern, args.link_filter, allowed)
    if code == 0:
        print(url)
        return EXIT_OK
    if code in settled:
        return settled[code]

    # code was 1: Mailcatcher may not have received the message yet. Retry once.
    time.sleep(RETRY_DELAY)
    code, url = attempt(base, args.recipient, args.pattern, args.link_filter, allowed)
    if code == 0:
        print(url)
        return EXIT_OK
    if code in settled:
        return settled[code]

    if args.pattern:
        print(
            f"NO_MATCH: no email for recipient '{args.recipient}' "
            f"with subject containing '{args.pattern}'",
            file=sys.stderr,
        )
    else:
        print(f"NO_MATCH: no email for recipient '{args.recipient}'", file=sys.stderr)
    return EXIT_NO_MATCH


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], os.environ))
