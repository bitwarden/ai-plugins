#!/usr/bin/env python3
"""Unit tests for external_trigger, the policy-guarded Category 3 POST wrapper.

Run with:  python3 -m unittest discover -s scripts/tests   (from the plugin root)
"""
import contextlib
import http.server
import io
import os
import shutil
import ssl
import sys
import tempfile
import threading
import unittest
import urllib.error
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)

import external_trigger


class AllowedHostsTest(unittest.TestCase):
    def test_defaults(self):
        self.assertEqual(
            external_trigger.allowed_hosts({}),
            ("localhost", "127.0.0.1", "::1", "bitwarden.test"),
        )

    def test_env_extends_never_replaces(self):
        hosts = external_trigger.allowed_hosts(
            {"PLAYWRIGHT_TESTING_ALLOWED_HOSTS": "dev.local,other.test"}
        )
        self.assertIn("localhost", hosts)
        self.assertIn("dev.local", hosts)
        self.assertIn("other.test", hosts)

    def test_env_star_is_literal_not_a_wildcard(self):
        # The bash version needed an array plus quoted expansion to stop the
        # shell globbing this against the cwd. Pin that the guarantee survived.
        hosts = external_trigger.allowed_hosts({"PLAYWRIGHT_TESTING_ALLOWED_HOSTS": "*"})
        self.assertIn("*", hosts)
        with self.assertRaises(external_trigger.GuardError) as caught:
            external_trigger.check_request("http://evil.com/x", "POST", hosts)
        self.assertEqual(caught.exception.code, 10)

    def test_blank_entries_ignored(self):
        hosts = external_trigger.allowed_hosts(
            {"PLAYWRIGHT_TESTING_ALLOWED_HOSTS": " dev.local , ,"}
        )
        self.assertIn("dev.local", hosts)
        self.assertNotIn("", hosts)


class TlsContextTest(unittest.TestCase):
    def test_http_needs_no_context(self):
        self.assertIsNone(external_trigger.tls_context("http", "localhost"))

    def test_default_dev_host_skips_verification(self):
        ctx = external_trigger.tls_context("https", "localhost")
        self.assertFalse(ctx.check_hostname)
        self.assertEqual(ctx.verify_mode, ssl.CERT_NONE)

    def test_bitwarden_test_host_skips_verification(self):
        ctx = external_trigger.tls_context("https", "bitwarden.test")
        self.assertEqual(ctx.verify_mode, ssl.CERT_NONE)

    def test_operator_added_host_gets_normal_verification(self):
        ctx = external_trigger.tls_context("https", "dev.internal.example")
        self.assertTrue(ctx.check_hostname)
        self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)


class CheckRequestTest(unittest.TestCase):
    def setUp(self):
        self.allowed = external_trigger.allowed_hosts({})

    def _reject(self, url, method="POST"):
        with self.assertRaises(external_trigger.GuardError) as caught:
            external_trigger.check_request(url, method, self.allowed)
        return caught.exception.code

    def test_accepts_each_default_host(self):
        for url in (
            "http://localhost:4000/x",
            "http://127.0.0.1:4000/x",
            "http://[::1]:4000/x",
            "https://bitwarden.test/x",
        ):
            scheme, host = external_trigger.check_request(url, "POST", self.allowed)
            self.assertIn(scheme, ("http", "https"))
            self.assertIn(host, self.allowed)

    def test_host_comparison_is_case_insensitive(self):
        _scheme, host = external_trigger.check_request(
            "HTTP://LOCALHOST/x", "POST", self.allowed
        )
        self.assertEqual(host, "localhost")

    def test_external_host_rejected(self):
        self.assertEqual(self._reject("http://evil.com/x"), 10)

    def test_userinfo_trick_rejected(self):
        # The real host is evil.com. A substring check on the raw URL passes this.
        self.assertEqual(self._reject("https://localhost@evil.com/x"), 10)

    def test_disallowed_schemes(self):
        self.assertEqual(self._reject("ftp://localhost/x"), 11)
        self.assertEqual(self._reject("file://localhost/etc/passwd"), 11)

    def test_non_post_method_rejected(self):
        self.assertEqual(self._reject("http://localhost/x", "GET"), 12)

    def test_malformed_urls(self):
        self.assertEqual(self._reject("not-a-url"), 13)
        self.assertEqual(self._reject("http://"), 13)
        # No host at all. The bash parser also fails before the scheme check,
        # so this is 13 rather than 11 in both implementations.
        self.assertEqual(self._reject("file:///etc/passwd"), 13)

    def test_urlparse_raising_valueerror_is_malformed(self):
        # urlparse itself raises ValueError (rather than just yielding an
        # empty scheme/host) for a malformed IPv6 literal. Exercises the
        # except ValueError branch in check_request directly.
        self.assertEqual(self._reject("http://[::1/x"), 13)


class MainGuardTest(unittest.TestCase):
    def test_guard_failure_never_sends(self):
        with mock.patch.object(external_trigger, "send") as sender, mock.patch(
            "sys.stderr", new_callable=io.StringIO
        ):
            code = external_trigger.main(
                ["--url", "http://evil.com/x", "--rationale", "why"], {}
            )
        self.assertEqual(code, 10)
        sender.assert_not_called()

    def test_missing_required_flags_exit_2(self):
        with mock.patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(external_trigger.main(["--rationale", "why"], {}), 2)
            self.assertEqual(external_trigger.main(["--url", "http://localhost/x"], {}), 2)

    def test_unknown_argument_exits_2(self):
        with mock.patch("sys.stderr", new_callable=io.StringIO):
            code = external_trigger.main(
                ["--url", "http://localhost/x", "--rationale", "w", "--bogus", "1"], {}
            )
        self.assertEqual(code, 2)

    def test_empty_url_exits_2(self):
        # required=True only enforces presence, not a non-empty value. The
        # bash original rejected an empty --url before it ever reached URL
        # parsing (which would otherwise raise the malformed-URL exit 13).
        err = io.StringIO()
        with mock.patch.object(external_trigger, "send") as sender, mock.patch(
            "sys.stderr", err
        ):
            code = external_trigger.main(["--url", "", "--rationale", "why"], {})
        self.assertEqual(code, 2)
        self.assertIn("ERROR: --url is required", err.getvalue())
        sender.assert_not_called()

    def test_empty_rationale_exits_2_and_never_sends(self):
        # An empty rationale is a blank audit trail for the only sanctioned
        # outbound-request path; it must be refused before anything is sent.
        err = io.StringIO()
        with mock.patch.object(external_trigger, "send") as sender, mock.patch(
            "sys.stderr", err
        ):
            code = external_trigger.main(
                ["--url", "http://localhost/x", "--rationale", "  "], {}
            )
        self.assertEqual(code, 2)
        self.assertIn("ERROR: --rationale is required", err.getvalue())
        sender.assert_not_called()


class MainResponseTest(unittest.TestCase):
    def _run(self, side_effect=None, return_value="ok"):
        buf = io.StringIO()
        with mock.patch.object(external_trigger, "send") as sender, mock.patch(
            "sys.stderr", new_callable=io.StringIO
        ), contextlib.redirect_stdout(buf):
            if side_effect is not None:
                sender.side_effect = side_effect
            else:
                sender.return_value = return_value
            code = external_trigger.main(
                ["--url", "http://localhost:4000/x", "--rationale", "why"], {}
            )
        return code, buf.getvalue()

    def test_success_prints_body(self):
        code, out = self._run(return_value="hello")
        self.assertEqual(code, 0)
        self.assertEqual(out, "hello")

    def test_http_error_prints_body_and_exits_0(self):
        # curl -sS without -f prints the body and exits 0, so a 400 from the
        # trigger endpoint still counts as "request completed".
        error = urllib.error.HTTPError(
            "http://localhost:4000/x", 400, "Bad Request", {}, io.BytesIO(b"bad input")
        )
        code, out = self._run(side_effect=error)
        self.assertEqual(code, 0)
        self.assertEqual(out, "bad input")

    def test_transport_failure_exits_1(self):
        code, _out = self._run(side_effect=urllib.error.URLError("connection refused"))
        self.assertEqual(code, 1)


class LogCallTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.directory, ignore_errors=True)

    def test_appends_when_artifacts_dir_exists(self):
        with mock.patch("sys.stderr", new_callable=io.StringIO):
            external_trigger.log_call(
                "http://localhost/x",
                "because",
                {"PLAYWRIGHT_TESTING_ARTIFACTS_DIR": self.directory},
            )
        with open(os.path.join(self.directory, "external-trigger.log"), encoding="utf-8") as handle:
            self.assertEqual(
                handle.read().strip(),
                "external-trigger POST http://localhost/x: because",
            )

    def test_no_file_when_dir_unset_or_missing(self):
        missing = os.path.join(self.directory, "nope")
        with mock.patch("sys.stderr", new_callable=io.StringIO):
            external_trigger.log_call("http://localhost/x", "because", {})
            external_trigger.log_call(
                "http://localhost/x", "because", {"PLAYWRIGHT_TESTING_ARTIFACTS_DIR": missing}
            )
        self.assertFalse(os.path.exists(missing))
        self.assertEqual(os.listdir(self.directory), [])


class _QuietHandler(http.server.BaseHTTPRequestHandler):
    """BaseHTTPRequestHandler that stays silent on stderr during tests."""

    def log_message(self, *args, **kwargs):  # noqa: D401 - silence per-request logging
        pass


class NoRedirectIntegrationTest(unittest.TestCase):
    """Exercises the real send()/urlopen path against local HTTP servers.

    A first server (on 127.0.0.1, an allowlisted host) answers with a 302
    pointing at a second server on a different port. If external_trigger
    ever followed that redirect, the second server would be hit. It must
    never be hit: check_request only ran once, against the first URL, and a
    followed redirect would bypass the host guard entirely.
    """

    def setUp(self):
        target_hit = threading.Event()
        self.target_hit = target_hit
        redirect_body = b"redirect body, never the target's"
        self.redirect_body = redirect_body

        class TargetHandler(_QuietHandler):
            def do_POST(self):
                target_hit.set()
                body = b"should never be reached"
                self.send_response(200)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        self.target_server = http.server.HTTPServer(("127.0.0.1", 0), TargetHandler)
        target_port = self.target_server.server_address[1]

        class RedirectHandler(_QuietHandler):
            def do_POST(self):
                self.send_response(302)
                self.send_header(
                    "Location", f"http://127.0.0.1:{target_port}/elsewhere"
                )
                self.send_header("Content-Length", str(len(redirect_body)))
                self.end_headers()
                self.wfile.write(redirect_body)

        self.redirect_server = http.server.HTTPServer(("127.0.0.1", 0), RedirectHandler)
        self.redirect_port = self.redirect_server.server_address[1]

        self.threads = [
            threading.Thread(target=server.serve_forever, daemon=True)
            for server in (self.target_server, self.redirect_server)
        ]
        for thread in self.threads:
            thread.start()

        self.addCleanup(self._shutdown)

    def _shutdown(self):
        self.target_server.shutdown()
        self.redirect_server.shutdown()
        self.target_server.server_close()
        self.redirect_server.server_close()
        for thread in self.threads:
            thread.join(timeout=5)

    def test_redirect_is_not_followed(self):
        buf = io.StringIO()
        with mock.patch("sys.stderr", new_callable=io.StringIO), contextlib.redirect_stdout(buf):
            code = external_trigger.main(
                [
                    "--url",
                    f"http://127.0.0.1:{self.redirect_port}/start",
                    "--rationale",
                    "why",
                ],
                {},
            )
        # curl -sS without -L prints the 3xx body and exits 0; the
        # HTTPError path in main() reproduces that.
        self.assertEqual(code, 0)
        self.assertEqual(buf.getvalue(), self.redirect_body.decode("utf-8"))
        self.assertFalse(self.target_hit.is_set())


if __name__ == "__main__":
    unittest.main()
