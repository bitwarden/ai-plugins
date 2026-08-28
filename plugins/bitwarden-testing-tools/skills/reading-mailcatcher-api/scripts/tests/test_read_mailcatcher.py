#!/usr/bin/env python3
"""Unit tests for read_mailcatcher: message selection, URL extraction, and the
exit-code contract. No network: every test patches the _http_get seam.

Run with:  python3 -m unittest discover -s scripts/tests   (from the skill dir)
"""
import contextlib
import http.server
import io
import json
import os
import sys
import threading
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)

import read_mailcatcher

BASE = "http://localhost:1080"


class FakeHTTP:
    """Route table standing in for _http_get. Unrouted URLs are unreachable."""

    def __init__(self, routes):
        self.routes = routes
        self.calls = []

    def __call__(self, url):
        self.calls.append(url)
        if url not in self.routes:
            raise read_mailcatcher.Unreachable(f"no route for {url}")
        value = self.routes[url]
        if isinstance(value, Exception):
            raise value
        return value


def messages_json(*entries):
    return json.dumps(list(entries))


def message(msg_id, recipient, subject):
    return {"id": msg_id, "recipients": [f"<{recipient}>"], "subject": subject}


class SelectMessageTest(unittest.TestCase):
    def test_recipient_match_is_case_insensitive_substring(self):
        msgs = [message(1, "User@Bitwarden.test", "Verify your email")]
        self.assertEqual(read_mailcatcher.select_message(msgs, "user@bitwarden.test", ""), 1)

    def test_subject_pattern_filters(self):
        msgs = [message(1, "a@b.test", "Welcome aboard")]
        self.assertIsNone(read_mailcatcher.select_message(msgs, "a@b.test", "verify"))
        self.assertEqual(read_mailcatcher.select_message(msgs, "a@b.test", "welcome"), 1)

    def test_empty_pattern_matches_any_subject(self):
        msgs = [message(1, "a@b.test", "Anything at all")]
        self.assertEqual(read_mailcatcher.select_message(msgs, "a@b.test", ""), 1)

    def test_newest_id_wins(self):
        msgs = [
            message(1, "a@b.test", "Verify your email"),
            message(7, "a@b.test", "Verify your email"),
            message(4, "a@b.test", "Verify your email"),
        ]
        self.assertEqual(read_mailcatcher.select_message(msgs, "a@b.test", "verify"), 7)

    def test_no_match_returns_none(self):
        msgs = [message(1, "someone@else.test", "Verify your email")]
        self.assertIsNone(read_mailcatcher.select_message(msgs, "a@b.test", "verify"))

    def test_message_without_an_id_is_skipped_not_indexed(self):
        """A missing `id` used to raise KeyError, escaping the exit-code contract."""
        broken = message(1, "a@b.test", "Verify your email")
        del broken["id"]
        msgs = [broken, message(3, "a@b.test", "Verify your email")]
        self.assertEqual(read_mailcatcher.select_message(msgs, "a@b.test", "verify"), 3)

    def test_only_candidate_lacking_an_id_returns_none(self):
        broken = message(1, "a@b.test", "Verify your email")
        broken["id"] = None
        self.assertIsNone(
            read_mailcatcher.select_message([broken], "a@b.test", "verify")
        )

    def test_non_object_entry_is_skipped(self):
        msgs = ["not a message", message(2, "a@b.test", "Verify your email")]
        self.assertEqual(read_mailcatcher.select_message(msgs, "a@b.test", "verify"), 2)


class MatchingUrlsTest(unittest.TestCase):
    def setUp(self):
        self.link_filter = read_mailcatcher.DEFAULT_LINK_FILTER

    def test_keeps_only_urls_matching_the_filter(self):
        body = "Ignore https://localhost:8080/#/home then use https://localhost:8080/#/verify?t=1"
        self.assertEqual(
            read_mailcatcher.matching_urls(body, self.link_filter),
            ["https://localhost:8080/#/verify?t=1"],
        )

    def test_returns_all_matches_in_document_order(self):
        # The caller (attempt) picks the first local one out of these, so the
        # full ordered list must come back, not just the first match.
        body = "first https://localhost:8080/#/login then https://localhost:8080/#/verify?t=1"
        self.assertEqual(
            read_mailcatcher.matching_urls(body, self.link_filter),
            [
                "https://localhost:8080/#/login",
                "https://localhost:8080/#/verify?t=1",
            ],
        )

    def test_returns_empty_when_nothing_matches(self):
        self.assertEqual(
            read_mailcatcher.matching_urls("only https://localhost:8080/#/home here", self.link_filter),
            [],
        )

    def test_returns_empty_for_empty_body(self):
        self.assertEqual(read_mailcatcher.matching_urls("", self.link_filter), [])

    def test_multiline_body_does_not_glue_lines_together(self):
        # grep is line-based, so a newline can never land inside a match. The
        # regex must exclude all whitespace or these two lines would join.
        body = "https://localhost:8080/#/verify?t=1\nhttps://localhost:8080/#/login"
        self.assertEqual(
            read_mailcatcher.matching_urls(body, self.link_filter),
            [
                "https://localhost:8080/#/verify?t=1",
                "https://localhost:8080/#/login",
            ],
        )

    def test_custom_filter_is_honored(self):
        body = "https://localhost:8080/#/sso-landing"
        self.assertEqual(read_mailcatcher.matching_urls(body, "sso"), [body])

    def test_invalid_regex_returns_empty_instead_of_raising(self):
        # An unbalanced group is a malformed ERE. grep -iE would error out
        # and yield no match rather than a match; matching_urls must fall
        # through to [] (and thus the caller's NO_MATCH branch) the same
        # way, instead of letting re.error propagate as a traceback.
        body = "https://localhost:8080/#/verify?t=1"
        self.assertEqual(read_mailcatcher.matching_urls(body, "("), [])


class IsLocalTest(unittest.TestCase):
    def setUp(self):
        self.allowed = read_mailcatcher.allowed_hosts({})

    def test_allowlisted_hosts_accepted(self):
        self.assertTrue(read_mailcatcher.is_local("https://localhost:8080/x", self.allowed))
        self.assertTrue(read_mailcatcher.is_local("http://bitwarden.test/x", self.allowed))

    def test_external_host_rejected(self):
        self.assertFalse(read_mailcatcher.is_local("https://evil.com/x", self.allowed))

    def test_userinfo_trick_rejected(self):
        self.assertFalse(read_mailcatcher.is_local("https://localhost@evil.com/x", self.allowed))

    def test_env_extension_honored(self):
        allowed = read_mailcatcher.allowed_hosts({"PLAYWRIGHT_TESTING_ALLOWED_HOSTS": "dev.local"})
        self.assertTrue(read_mailcatcher.is_local("http://dev.local/x", allowed))

    def test_env_extension_accepts_multiple_hosts(self):
        allowed = read_mailcatcher.allowed_hosts(
            {"PLAYWRIGHT_TESTING_ALLOWED_HOSTS": "one.local, two.local"}
        )
        self.assertTrue(read_mailcatcher.is_local("http://one.local/x", allowed))
        self.assertTrue(read_mailcatcher.is_local("http://two.local/x", allowed))


class MainTest(unittest.TestCase):
    def _run(self, routes, argv=None, env=None):
        argv = argv or ["--recipient", "user@bitwarden.test", "--pattern", "verify"]
        fake = FakeHTTP(routes)
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(read_mailcatcher, "_http_get", fake), mock.patch.object(
            read_mailcatcher.time, "sleep"
        ) as sleeper, contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = read_mailcatcher.main(argv, env or {})
        return code, out.getvalue(), err.getvalue(), fake, sleeper

    def test_success_prints_url(self):
        code, out, _err, _fake, _sleep = self._run(
            {
                f"{BASE}/messages": messages_json(message(1, "user@bitwarden.test", "Verify your email")),
                f"{BASE}/messages/1.plain": "Click https://localhost:8080/#/verify?t=abc to continue",
            }
        )
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "https://localhost:8080/#/verify?t=abc")

    def test_unreachable_exits_3_without_retrying(self):
        code, _out, err, fake, sleeper = self._run({})
        self.assertEqual(code, 3)
        self.assertIn("unreachable", err.lower())
        sleeper.assert_not_called()
        self.assertEqual(len(fake.calls), 1)

    def test_invalid_json_exits_3(self):
        code, _out, _err, _fake, _sleep = self._run({f"{BASE}/messages": "not json at all"})
        self.assertEqual(code, 3)

    def test_no_message_retries_once_then_exits_1(self):
        code, _out, err, fake, sleeper = self._run({f"{BASE}/messages": messages_json()})
        self.assertEqual(code, 1)
        sleeper.assert_called_once_with(read_mailcatcher.RETRY_DELAY)
        self.assertEqual(fake.calls.count(f"{BASE}/messages"), 2)
        self.assertIn("NO_MATCH", err)
        self.assertIn("with subject containing 'verify'", err)

    def test_no_message_without_pattern_omits_subject_clause(self):
        code, _out, err, _fake, _sleep = self._run(
            {f"{BASE}/messages": messages_json()},
            argv=["--recipient", "user@bitwarden.test"],
        )
        self.assertEqual(code, 1)
        self.assertIn("no email for recipient 'user@bitwarden.test'", err)
        self.assertNotIn("subject containing", err)

    def test_matched_message_with_no_matching_url_exits_1(self):
        code, _out, err, _fake, sleeper = self._run(
            {
                f"{BASE}/messages": messages_json(message(1, "user@bitwarden.test", "Verify your email")),
                f"{BASE}/messages/1.plain": "no links in this body",
            }
        )
        self.assertEqual(code, 1)
        self.assertIn("contained no URL", err)
        sleeper.assert_not_called()

    def test_invalid_link_filter_regex_emits_no_match_not_a_traceback(self):
        code, _out, err, _fake, sleeper = self._run(
            {
                f"{BASE}/messages": messages_json(message(1, "user@bitwarden.test", "Verify your email")),
                f"{BASE}/messages/1.plain": "Click https://localhost:8080/#/verify?t=abc",
            },
            argv=[
                "--recipient",
                "user@bitwarden.test",
                "--pattern",
                "verify",
                "--link-filter",
                "(",
            ],
        )
        self.assertEqual(code, 1)
        self.assertIn("NO_MATCH", err)
        self.assertIn("contained no URL", err)
        sleeper.assert_not_called()

    def test_non_local_url_exits_1(self):
        code, _out, err, _fake, _sleep = self._run(
            {
                f"{BASE}/messages": messages_json(message(1, "user@bitwarden.test", "Verify your email")),
                f"{BASE}/messages/1.plain": "Click https://evil.com/verify?t=abc",
            }
        )
        self.assertEqual(code, 1)
        self.assertIn("not a local dev host", err)

    def test_external_footer_link_does_not_mask_a_later_local_link(self):
        # A marketing/help footer link matches the default filter ("login")
        # but is not a local host. It must not shadow the real local action
        # link that follows it: the script walks every filter match and picks
        # the first that is also local.
        body = (
            "Need help? https://bitwarden.com/help/login-with-device\n"
            "Verify: https://localhost:8080/#/finish-signup?token=ABC"
        )
        code, out, _err, _fake, _sleep = self._run(
            {
                f"{BASE}/messages": messages_json(message(1, "user@bitwarden.test", "Verify your email")),
                f"{BASE}/messages/1.plain": body,
            }
        )
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "https://localhost:8080/#/finish-signup?token=ABC")

    def test_empty_plain_body_falls_back_to_html_with_warning(self):
        code, out, err, _fake, _sleep = self._run(
            {
                f"{BASE}/messages": messages_json(message(3, "user@bitwarden.test", "Verify your email")),
                f"{BASE}/messages/3.plain": "",
                f"{BASE}/messages/3.html": '<a href="https://localhost:8080/#/verify?t=z">Verify</a>',
            }
        )
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "https://localhost:8080/#/verify?t=z")
        self.assertIn("WARNING", err)

    def test_html_fallback_unescapes_entities_in_the_link(self):
        # The HTML body carries an href with an `&amp;` entity between query
        # params. Extracting from raw HTML would emit the literal `&amp;` and
        # corrupt every parameter after the first, so the HTML branch must
        # unescape before the URL is returned.
        href = "https://localhost:8080/#/finish-signup?token=ABC&amp;email=qa%40example.com"
        code, out, _err, _fake, _sleep = self._run(
            {
                f"{BASE}/messages": messages_json(message(4, "user@bitwarden.test", "Verify your email")),
                f"{BASE}/messages/4.plain": "",
                f"{BASE}/messages/4.html": f'<a href="{href}">Verify</a>',
            }
        )
        self.assertEqual(code, 0)
        self.assertEqual(
            out.strip(),
            "https://localhost:8080/#/finish-signup?token=ABC&email=qa%40example.com",
        )

    def test_mailcatcher_url_env_is_ignored(self):
        # The base URL is fixed at localhost:1080 and takes no override. A
        # hostile MAILCATCHER_URL env var must have no effect: the script still
        # queries localhost:1080 and never contacts the attacker host. This is
        # the regression guard for the removed base-URL override.
        code, out, _err, fake, _sleep = self._run(
            {
                f"{BASE}/messages": messages_json(message(1, "user@bitwarden.test", "Verify your email")),
                f"{BASE}/messages/1.plain": "Click https://localhost:8080/#/verify?t=safe to continue",
            },
            env={"MAILCATCHER_URL": "https://attacker.example/leak"},
        )
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "https://localhost:8080/#/verify?t=safe")
        self.assertTrue(all(url.startswith(BASE) for url in fake.calls))
        self.assertFalse(any("attacker.example" in url for url in fake.calls))

    def test_missing_recipient_exits_2(self):
        with mock.patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(read_mailcatcher.main([], {}), 2)

    def test_empty_recipient_exits_2(self):
        # required=True only enforces presence, not a non-empty value. An
        # empty --recipient is a substring of every recipient string, so
        # without this guard select_message would return the newest message
        # in the entire inbox regardless of addressee.
        err = io.StringIO()
        with mock.patch("sys.stderr", err):
            code = read_mailcatcher.main(["--recipient", ""], {})
        self.assertEqual(code, 2)
        self.assertIn("ERROR: --recipient is required", err.getvalue())


class _QuietHandler(http.server.BaseHTTPRequestHandler):
    """BaseHTTPRequestHandler that stays silent on stderr during tests."""

    def log_message(self, *args, **kwargs):  # noqa: D401 - silence per-request logging
        pass


class NoRedirectIntegrationTest(unittest.TestCase):
    """Exercises the real _http_get path against local HTTP servers.

    Every MainTest and unit test above patches the _http_get seam, so nothing
    else in this file exercises the real implementation. A redirect server
    (on 127.0.0.1, an allowlisted host) answers with a 302 pointing at a
    target server on a different port. If _http_get ever followed that
    redirect, the target server would be hit. It must never be hit: this is
    what catches a future regression that removes the no-redirect handler.

    An error server rounds out the curl -f parity check: a halted 3xx must
    return its own body as a success, while a status >= 400 must still raise
    Unreachable.
    """

    def setUp(self):
        target_hit = threading.Event()
        self.target_hit = target_hit
        redirect_body = b"redirect body, never the target's"
        self.redirect_body = redirect_body

        class TargetHandler(_QuietHandler):
            def do_GET(self):
                target_hit.set()
                body = b"should never be reached"
                self.send_response(200)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        self.target_server = http.server.HTTPServer(("127.0.0.1", 0), TargetHandler)
        target_port = self.target_server.server_address[1]

        class RedirectHandler(_QuietHandler):
            def do_GET(self):
                self.send_response(302)
                self.send_header(
                    "Location", f"http://127.0.0.1:{target_port}/elsewhere"
                )
                self.send_header("Content-Length", str(len(redirect_body)))
                self.end_headers()
                self.wfile.write(redirect_body)

        self.redirect_server = http.server.HTTPServer(("127.0.0.1", 0), RedirectHandler)
        self.redirect_port = self.redirect_server.server_address[1]

        class ErrorHandler(_QuietHandler):
            def do_GET(self):
                body = b"server error"
                self.send_response(500)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        self.error_server = http.server.HTTPServer(("127.0.0.1", 0), ErrorHandler)
        self.error_port = self.error_server.server_address[1]

        self.threads = [
            threading.Thread(target=server.serve_forever, daemon=True)
            for server in (self.target_server, self.redirect_server, self.error_server)
        ]
        for thread in self.threads:
            thread.start()

        self.addCleanup(self._shutdown)

    def _shutdown(self):
        self.target_server.shutdown()
        self.redirect_server.shutdown()
        self.error_server.shutdown()
        self.target_server.server_close()
        self.redirect_server.server_close()
        self.error_server.server_close()
        for thread in self.threads:
            thread.join(timeout=5)

    def test_redirect_is_not_followed(self):
        """A halted 3xx is a success: it returns the redirect response's own
        body, and the Location target is never requested."""
        url = f"http://127.0.0.1:{self.redirect_port}/start"
        body = read_mailcatcher._http_get(url)
        self.assertEqual(body, self.redirect_body.decode("utf-8"))
        self.assertFalse(self.target_hit.is_set())

    def test_status_500_raises_unreachable(self):
        url = f"http://127.0.0.1:{self.error_port}/fail"
        with self.assertRaises(read_mailcatcher.Unreachable):
            read_mailcatcher._http_get(url)

    def test_fetch_messages_treats_halted_redirect_body_as_the_response(self):
        """The concrete parity break the review identified: bash's curl -fsS
        with no -L treats a 3xx as success and reads its body, so a redirect
        whose body happens to be valid JSON must flow through fetch_messages
        normally instead of becoming exit 3."""
        body = b"[]"

        class MessagesHandler(_QuietHandler):
            def do_GET(self):
                self.send_response(302)
                self.send_header("Location", "http://127.0.0.1:1/unused")
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        server = http.server.HTTPServer(("127.0.0.1", 0), MessagesHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base = f"http://127.0.0.1:{server.server_address[1]}"
            self.assertEqual(read_mailcatcher.fetch_messages(base), [])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
