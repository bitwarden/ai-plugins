#!/usr/bin/env python3
"""Category 3 external-trigger simulation for the bitwarden-playwright-testing
pipeline. The ONLY sanctioned way for the test-runner to issue an outbound
request. Enforces, in code, the localhost-only policy that
references/tool-policy.md describes: a plan step (which may be derived from
untrusted Jira/Confluence content) cannot drive a request to a metadata
endpoint, a private-network host, an external host, or a remote Bitwarden
QA/cloud domain.

Usage:
  external_trigger.py --url <url> --rationale <text> [--data <json>] [--content-type <ct>]

Method is always POST (Category 3 triggers are POSTs). Allowed hosts default to
localhost/127.0.0.1/::1/bitwarden.test and can be extended (never replaced) via
the comma-separated env var PLAYWRIGHT_TESTING_ALLOWED_HOSTS. Allowed schemes
are http and https. Every permitted call is logged; if
PLAYWRIGHT_TESTING_ARTIFACTS_DIR is set, the log line is appended to
<dir>/external-trigger.log.

Exit codes: 0 request completed (any HTTP status); 1 transport failure;
2 usage error; 10 disallowed host; 11 disallowed scheme; 12 disallowed method;
13 malformed URL.
"""
import argparse
import os
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_ALLOWED_HOSTS = ("localhost", "127.0.0.1", "::1", "bitwarden.test")
REQUEST_TIMEOUT = 10

EXIT_OK = 0
EXIT_TRANSPORT = 1
EXIT_USAGE = 2
EXIT_HOST = 10
EXIT_SCHEME = 11
EXIT_METHOD = 12
EXIT_MALFORMED = 13


class GuardError(Exception):
    """A request rejected by policy, carrying its documented exit code."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Never follow 3xx redirects, matching curl's default (no -L).

    check_request runs exactly once, against the original --url, before
    send() is ever called. The stdlib's default opener installs a
    HTTPRedirectHandler that follows a 301/302/303/307 Location header with
    no second policy check, which would let a redirect drive a request past
    the host guard. Returning None from redirect_request tells the base
    handler not to redirect; it then falls through to
    HTTPDefaultErrorHandler, which raises HTTPError for the 3xx status. main()
    already catches HTTPError, prints the body, and returns exit 0, so a
    surfaced 3xx lands on the same path curl took.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def allowed_hosts(env):
    """Default local dev hosts, extended (never replaced) by the env var."""
    hosts = [host.lower() for host in DEFAULT_ALLOWED_HOSTS]
    for entry in env.get("PLAYWRIGHT_TESTING_ALLOWED_HOSTS", "").split(","):
        entry = entry.strip().lower()
        if entry:
            hosts.append(entry)
    return tuple(hosts)


def check_request(url, method, allowed):
    """Pure policy guard. Returns (scheme, host) or raises GuardError.

    Order matches the bash original: method, then URL parse, then scheme, then
    host. The host is taken from a real URL parser, never from substring
    matching, so https://localhost@evil.com/ is correctly read as evil.com.
    """
    if method != "POST":
        raise GuardError(
            EXIT_METHOD,
            f"method '{method}' not allowed; Category 3 external triggers are POST only",
        )
    try:
        parsed = urllib.parse.urlparse(url)
        scheme = (parsed.scheme or "").lower()
        host = (parsed.hostname or "").lower()
    except ValueError:
        raise GuardError(EXIT_MALFORMED, f"malformed URL: {url}")
    if not scheme or not host:
        raise GuardError(EXIT_MALFORMED, f"malformed URL: {url}")
    if scheme not in ("http", "https"):
        raise GuardError(EXIT_SCHEME, f"scheme '{scheme}' not allowed; use http or https")
    if host not in allowed:
        raise GuardError(
            EXIT_HOST,
            f"host '{host}' is not an allowed local dev host.\n"
            f"       Allowed: {' '.join(allowed)}\n"
            "       For a custom local hostname, set "
            "PLAYWRIGHT_TESTING_ALLOWED_HOSTS=<host>[,<host>...].",
        )
    return scheme, host


def log_call(url, rationale, env):
    """Record the permitted call on stderr and, when configured, on disk."""
    line = f"external-trigger POST {url}: {rationale}"
    print(line, file=sys.stderr)
    artifacts = env.get("PLAYWRIGHT_TESTING_ARTIFACTS_DIR", "")
    if artifacts and os.path.isdir(artifacts):
        with open(os.path.join(artifacts, "external-trigger.log"), "a", encoding="utf-8") as handle:
            handle.write(line + "\n")


def send(url, data, content_type, scheme):
    """POST to url and return the response body as text.

    TLS verification is disabled for https because Bitwarden dev certs are
    self-signed. This is only reached after check_request has constrained the
    host to the local dev allowlist, and mirrors the curl -k the bash version
    used. Redirects are never followed (see _NoRedirectHandler), mirroring
    curl's default of no -L.
    """
    body = data.encode("utf-8") if data else b""
    request = urllib.request.Request(
        url, data=body, method="POST", headers={"Content-Type": content_type}
    )
    handlers = [_NoRedirectHandler]
    if scheme == "https":
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        handlers.append(urllib.request.HTTPSHandler(context=context))
    opener = urllib.request.build_opener(*handlers)
    with opener.open(request, timeout=REQUEST_TIMEOUT) as response:
        return response.read().decode("utf-8", errors="replace")


def main(argv, env):
    parser = argparse.ArgumentParser(
        prog="external_trigger.py",
        description="Issue a policy-guarded Category 3 external-trigger POST.",
    )
    parser.add_argument("--url", required=True)
    parser.add_argument(
        "--rationale",
        required=True,
        help="document why no Bitwarden service can initiate this",
    )
    parser.add_argument("--data")
    parser.add_argument("--content-type", default="application/json")
    parser.add_argument("--method", default="POST")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        # argparse exits 2 on a usage error and 0 on --help. Convert either
        # into a returned code so main always returns an int.
        return exc.code if isinstance(exc.code, int) else EXIT_USAGE

    # Matches the bash original's check ordering: --url, then --rationale,
    # both before any URL parsing or policy check, so an empty value is
    # always exit 2, not whatever exit the later checks would produce.
    if not args.url.strip():
        print("ERROR: --url is required", file=sys.stderr)
        return EXIT_USAGE
    if not args.rationale.strip():
        print(
            "ERROR: --rationale is required (document why no Bitwarden "
            "service can initiate this)",
            file=sys.stderr,
        )
        return EXIT_USAGE

    try:
        scheme, _host = check_request(args.url, args.method, allowed_hosts(env))
    except GuardError as err:
        print(f"ERROR: {err.message}", file=sys.stderr)
        return err.code

    log_call(args.url, args.rationale, env)

    try:
        body = send(args.url, args.data, args.content_type, scheme)
    except urllib.error.HTTPError as err:
        sys.stdout.write(err.read().decode("utf-8", errors="replace"))
        return EXIT_OK
    except (urllib.error.URLError, OSError) as err:
        print(f"ERROR: request to {args.url} failed: {err}", file=sys.stderr)
        return EXIT_TRANSPORT

    sys.stdout.write(body)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], os.environ))
