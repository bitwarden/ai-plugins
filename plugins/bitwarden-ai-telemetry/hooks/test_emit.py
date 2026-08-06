#!/usr/bin/env python3
"""Unit tests for emit.emit — the shared OTLP-JSON emitter.

Covers the fail-closed behavior (no network call at all when
BW_TELEMETRY_OTLP isn't set — see emit.py's module docstring for why) and the
payload shape (falsey attrs dropped) when a collector IS configured.

Run with:  python3 -m unittest test_emit   (from the hooks/ dir)
      or:  python3 -m pytest test_emit.py
"""
import importlib
import json
import os
import sys
import unittest
from datetime import datetime, timedelta
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import emit as emit_module


class EmitFailClosedTest(unittest.TestCase):
    def setUp(self):
        # Reload so module-level COLLECTOR is re-read fresh under each test's
        # patched environment, rather than whatever was cached at first import.
        self._env_patch = mock.patch.dict(os.environ, {}, clear=False)
        self._env_patch.start()
        os.environ.pop("BW_TELEMETRY_OTLP", None)
        importlib.reload(emit_module)

    def tearDown(self):
        self._env_patch.stop()
        importlib.reload(emit_module)

    def test_no_network_call_when_collector_unset(self):
        with mock.patch("urllib.request.urlopen") as urlopen:
            emit_module.emit("bw.identity", {"bw.skill": "x"})
            urlopen.assert_not_called()

    def test_posts_when_collector_is_set(self):
        os.environ["BW_TELEMETRY_OTLP"] = "https://example.bitwarden.pw/v1/logs"
        importlib.reload(emit_module)
        with mock.patch("urllib.request.urlopen") as urlopen:
            urlopen.return_value.read.return_value = b""
            emit_module.emit("bw.identity", {"bw.skill": "researching-jira-issues"})
            urlopen.assert_called_once()
            req = urlopen.call_args[0][0]
            self.assertEqual(req.full_url, "https://example.bitwarden.pw/v1/logs")
            body = json.loads(req.data)
            attrs = body["resourceLogs"][0]["scopeLogs"][0]["logRecords"][0]["attributes"]
            self.assertIn({"key": "bw.skill", "value": {"stringValue": "researching-jira-issues"}}, attrs)

    def test_falsey_attrs_are_dropped(self):
        os.environ["BW_TELEMETRY_OTLP"] = "https://example.bitwarden.pw/v1/logs"
        importlib.reload(emit_module)
        with mock.patch("urllib.request.urlopen") as urlopen:
            urlopen.return_value.read.return_value = b""
            emit_module.emit("bw.identity", {"bw.skill": "", "bw.agent_type": None, "bw.tool": "Skill"})
            req = urlopen.call_args[0][0]
            body = json.loads(req.data)
            attrs = body["resourceLogs"][0]["scopeLogs"][0]["logRecords"][0]["attributes"]
            keys = {a["key"] for a in attrs}
            # event.timestamp is stamped on every record; see EventTimestampTest.
            self.assertEqual(keys, {"bw.tool", "event.timestamp"})

    def test_network_error_is_swallowed_fail_open(self):
        os.environ["BW_TELEMETRY_OTLP"] = "https://example.bitwarden.pw/v1/logs"
        importlib.reload(emit_module)
        with mock.patch("urllib.request.urlopen", side_effect=OSError("connection refused")):
            emit_module.emit("bw.identity", {"bw.skill": "x"})  # must not raise

    def test_no_network_call_when_collector_is_plain_http(self):
        os.environ["BW_TELEMETRY_OTLP"] = "http://example.bitwarden.pw/v1/logs"
        importlib.reload(emit_module)
        with mock.patch("urllib.request.urlopen") as urlopen:
            emit_module.emit("bw.identity", {"bw.skill": "x"})
            urlopen.assert_not_called()

    def test_no_network_call_when_collector_is_file_scheme(self):
        os.environ["BW_TELEMETRY_OTLP"] = "file:///etc/passwd"
        importlib.reload(emit_module)
        with mock.patch("urllib.request.urlopen") as urlopen:
            emit_module.emit("bw.identity", {"bw.skill": "x"})
            urlopen.assert_not_called()

    def test_no_network_call_when_collector_is_off_domain(self):
        # A project-level .claude/settings.json could set this env var to
        # redirect telemetry to an attacker-controlled host; the domain
        # allowlist is what stops that, not managed-settings precedence
        # (the hook can't tell which settings layer set the var).
        os.environ["BW_TELEMETRY_OTLP"] = "https://attacker.example.com/v1/logs"
        importlib.reload(emit_module)
        with mock.patch("urllib.request.urlopen") as urlopen:
            emit_module.emit("bw.identity", {"bw.skill": "x"})
            urlopen.assert_not_called()

    def test_module_reload_does_not_raise_on_malformed_collector(self):
        # Every hook script does an unguarded `from emit import emit`, so
        # this reload has to succeed even with a value urlsplit chokes on.
        os.environ["BW_TELEMETRY_OTLP"] = "https://[bad"
        importlib.reload(emit_module)  # must not raise
        self.assertIsNone(emit_module.COLLECTOR)
        with mock.patch("urllib.request.urlopen") as urlopen:
            emit_module.emit("bw.identity", {"bw.skill": "x"})
            urlopen.assert_not_called()


class EventTimestampTest(unittest.TestCase):
    """Every record carries a client-side event.timestamp so consumers don't
    fall back to collector ingest time."""

    def setUp(self):
        self._env_patch = mock.patch.dict(os.environ, {}, clear=False)
        self._env_patch.start()
        os.environ["BW_TELEMETRY_OTLP"] = "https://example.bitwarden.pw/v1/logs"
        importlib.reload(emit_module)

    def tearDown(self):
        self._env_patch.stop()
        importlib.reload(emit_module)

    def _attrs_for(self, attrs):
        with mock.patch("urllib.request.urlopen") as urlopen:
            urlopen.return_value.read.return_value = b""
            emit_module.emit("bw.identity", attrs)
            body = json.loads(urlopen.call_args[0][0].data)
        records = body["resourceLogs"][0]["scopeLogs"][0]["logRecords"][0]
        return {a["key"]: a["value"]["stringValue"] for a in records["attributes"]}

    def test_timestamp_is_added_when_absent(self):
        self.assertIn("event.timestamp", self._attrs_for({"bw.tool": "Skill"}))

    def test_timestamp_parses_as_utc_iso8601(self):
        raw = self._attrs_for({"bw.tool": "Skill"})["event.timestamp"]
        self.assertTrue(raw.endswith("Z"), raw)
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        self.assertEqual(parsed.tzinfo.utcoffset(parsed), timedelta(0))

    def test_timestamp_has_millisecond_precision(self):
        # Second granularity would collapse distinct same-second invocations
        # under a consumer deduplication key that includes the timestamp.
        raw = self._attrs_for({"bw.tool": "Skill"})["event.timestamp"]
        self.assertRegex(raw, r"\.\d{3}Z$")

    def test_caller_supplied_timestamp_is_preserved(self):
        supplied = "2026-06-10T21:25:21.770Z"
        got = self._attrs_for({"bw.tool": "Skill", "event.timestamp": supplied})
        self.assertEqual(got["event.timestamp"], supplied)

    def test_empty_caller_timestamp_falls_back_to_generated(self):
        got = self._attrs_for({"bw.tool": "Skill", "event.timestamp": ""})
        self.assertRegex(got["event.timestamp"], r"\.\d{3}Z$")

    def test_caller_dict_is_not_mutated(self):
        caller = {"bw.tool": "Skill"}
        self._attrs_for(caller)
        self.assertEqual(caller, {"bw.tool": "Skill"})


class IsAllowedCollectorTest(unittest.TestCase):
    def test_bare_domain_is_allowed(self):
        self.assertTrue(emit_module._is_allowed_collector("https://bitwarden.pw/v1/logs"))

    def test_subdomain_is_allowed(self):
        self.assertTrue(emit_module._is_allowed_collector("https://ait.bitwarden.pw/v1/logs"))

    def test_nested_subdomain_is_allowed(self):
        self.assertTrue(emit_module._is_allowed_collector("https://staging.ait.bitwarden.pw/v1/logs"))

    def test_off_domain_is_rejected(self):
        self.assertFalse(emit_module._is_allowed_collector("https://attacker.example.com/v1/logs"))

    def test_lookalike_domain_without_dot_boundary_is_rejected(self):
        # cspell:ignore evilbitwarden
        # "evilbitwarden.pw" ends with "bitwarden.pw" as a raw substring but
        # is not bitwarden.pw or a subdomain of it.
        self.assertFalse(emit_module._is_allowed_collector("https://evilbitwarden.pw/v1/logs"))

    def test_domain_as_suffix_of_attacker_host_is_rejected(self):
        self.assertFalse(emit_module._is_allowed_collector("https://bitwarden.pw.attacker.com/v1/logs"))

    def test_userinfo_bypass_trick_is_rejected(self):
        # The real host is evil.com; bitwarden.pw here is just userinfo
        # before the @. A naive substring check on the raw URL would pass
        # this; parsing .hostname correctly rejects it.
        self.assertFalse(emit_module._is_allowed_collector("https://ait.bitwarden.pw@evil.com/v1/logs"))

    def test_plain_http_is_rejected(self):
        self.assertFalse(emit_module._is_allowed_collector("http://ait.bitwarden.pw/v1/logs"))

    def test_malformed_ipv6_bracket_syntax_is_rejected_not_raised(self):
        # urlsplit raises ValueError on this bracket syntax.
        self.assertFalse(emit_module._is_allowed_collector("https://[bad"))


if __name__ == "__main__":
    unittest.main()
