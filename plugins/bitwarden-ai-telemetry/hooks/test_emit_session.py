#!/usr/bin/env python3
"""Unit tests for emit_session: the pure reduction from a SessionStart hook
dict to the bw.session attrs, and main()'s fail-open handling of bad stdin.

Run with:  python3 -m unittest test_emit_session   (from the hooks/ dir)
      or:  python3 -m pytest test_emit_session.py
"""
import io
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import emit_session
from emit_session import _build_session_attrs


class BuildSessionAttrsTest(unittest.TestCase):
    def test_session_start(self):
        attrs = _build_session_attrs({
            "hook_event_name": "SessionStart",
            "session_id": "session-1",
            "cwd": "/Users/dev/bitwarden/clients",
            "source": "startup",
        })
        self.assertEqual(attrs, {
            "event.name": "bw.session",
            "bw.hook": "SessionStart",
            "session.id": "session-1",
            "repo": "clients",
        })

    def test_missing_fields_give_empty_values(self):
        attrs = _build_session_attrs({})
        self.assertEqual(attrs["event.name"], "bw.session")
        self.assertEqual(attrs["bw.hook"], "")
        self.assertEqual(attrs["session.id"], "")
        self.assertEqual(attrs["repo"], "")

    def test_null_cwd_gives_empty_repo(self):
        self.assertEqual(_build_session_attrs({"cwd": None})["repo"], "")


class MainTest(unittest.TestCase):
    def _run(self, stdin):
        with mock.patch.object(sys, "stdin", io.StringIO(stdin)), \
                mock.patch.object(emit_session, "emit") as emit:
            emit_session.main()  # must not raise
        return emit

    def test_bad_json_is_a_no_op(self):
        self._run("{not json").assert_not_called()

    def test_empty_stdin_is_a_no_op(self):
        self._run("").assert_not_called()

    def test_non_object_json_is_a_no_op(self):
        self._run("[1, 2]").assert_not_called()

    def test_valid_input_emits_one_session_record(self):
        emit = self._run('{"hook_event_name": "SessionStart", "session_id": "s-1"}')
        emit.assert_called_once()
        name, attrs = emit.call_args[0]
        self.assertEqual(name, "bw.session")
        self.assertEqual(attrs["session.id"], "s-1")


if __name__ == "__main__":
    unittest.main()
