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
            self.assertEqual(keys, {"bw.tool"})

    def test_network_error_is_swallowed_fail_open(self):
        os.environ["BW_TELEMETRY_OTLP"] = "https://example.bitwarden.pw/v1/logs"
        importlib.reload(emit_module)
        with mock.patch("urllib.request.urlopen", side_effect=OSError("connection refused")):
            emit_module.emit("bw.identity", {"bw.skill": "x"})  # must not raise


if __name__ == "__main__":
    unittest.main()
