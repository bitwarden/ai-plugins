#!/usr/bin/env python3
"""Fetch a Bitwarden Mailcatcher message matching a recipient + subject, and
print the first matching URL from its body on stdout.

Exit 0 on success (prints the extracted URL on stdout).
Exit 1: no matching message found, or a matched message had no local-host URL
        (diagnostic on stderr).
Exit 2: usage error.
Exit 3: Mailcatcher unreachable or returned invalid JSON.

Usage:
  read_mailcatcher.py --recipient <email> [--pattern <subject-keyword>] [--link-filter <regex>]

--pattern is optional. Omit (or pass empty) to match any subject and just take
the most recent message for the recipient.

Defaults:
  --link-filter: verify|confirm|signup|token|trial|login|finish-signup

Designed to be called via the Bash tool from the test-runner. The skill body in
../SKILL.md documents the underlying Mailcatcher REST API this wraps.
"""
import argparse
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_MAILCATCHER_URL = "http://localhost:1080"
DEFAULT_LINK_FILTER = "verify|confirm|signup|token|trial|login|finish-signup"
# Local dev hosts allowed for extracted URLs. Defaults match
# scripts/external_trigger.py; extend (never replace) via the comma-separated
# env var PLAYWRIGHT_TESTING_ALLOWED_HOSTS, exactly as that script does, so an
# operator override applies to both.
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
    the 3xx status. HTTPError is a URLError subclass, so _http_get's except
    clause below turns it into Unreachable, the same outcome curl -fsS with no
    -L produces when it cannot reach the intended resource.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def allowed_hosts(env):
    hosts = [host.lower() for host in DEFAULT_ALLOWED_HOSTS]
    for entry in env.get("PLAYWRIGHT_TESTING_ALLOWED_HOSTS", "").split(","):
        entry = entry.strip().lower()
        if entry:
            hosts.append(entry)
    return tuple(hosts)


def _http_get(url):
    """GET url and return the body as text. Raises Unreachable on any failure.

    Mirrors curl -fsS: an HTTP error status is a failure, not a body to parse.
    Redirects are never followed (see _NoRedirectHandler), mirroring curl's
    default of no -L.
    """
    handlers = [_NoRedirectHandler]
    if urllib.parse.urlparse(url).scheme == "https":
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        handlers.append(urllib.request.HTTPSHandler(context=context))
    opener = urllib.request.build_opener(*handlers)
    try:
        with opener.open(url, timeout=REQUEST_TIMEOUT) as response:
            return response.read().decode("utf-8", errors="replace")
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
    """Id of the newest message matching the recipient and optional pattern."""
    recipient = recipient.lower()
    pattern = (pattern or "").lower()
    matches = [
        msg
        for msg in messages
        if any(recipient in str(entry).lower() for entry in msg.get("recipients", []))
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
        body = _http_get_or_empty(f"{base}/messages/{message_id}.html")
    return body


def extract_url(body, link_filter):
    for candidate in URL_PATTERN.findall(body or ""):
        if re.search(link_filter, candidate, re.IGNORECASE):
            return candidate
    return None


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
    url = extract_url(fetch_body(base, message_id), link_filter)
    if url is None:
        print(
            f"NO_MATCH: message {message_id} matched but contained no URL "
            f"filtered by '{link_filter}'",
            file=sys.stderr,
        )
        return 2, None
    if not is_local(url, allowed):
        print(f"NO_MATCH: extracted URL '{url}' is not a local dev host", file=sys.stderr)
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

    base = (env.get("MAILCATCHER_URL") or DEFAULT_MAILCATCHER_URL).rstrip("/")
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
