#!/usr/bin/env python3
"""Unit tests for read_admin_email: narrow extraction from the dev secrets file.

Fixtures mirror the real server/dev/secrets.json shape: JSONC (with // and
/* */ comments), 'admins' nested under 'adminSettings', and a comma-separated
string value. See ledger item TTM-10.

Run with:  python3 -m unittest discover -s scripts/tests   (from the skill dir)
"""
# cspell:ignore adminSettings
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)

import read_admin_email


def write_text(text):
    """Write literal JSONC text to a temp file and return its path.

    Unlike json.dump, this preserves comments and exact byte shape, so the
    fixtures exercise the real parse path (_strip_jsonc then json.loads).
    """
    d = tempfile.mkdtemp()
    path = os.path.join(d, "secrets.json")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


# Shaped like the real server/dev/secrets.json: a JSONC line comment, 'admins'
# nested under 'adminSettings' as a comma-separated string, and an https:// URL
# whose '//' must survive the string-aware comment stripper.
REAL_SHAPED = """{
  // dev admin accounts
  "adminSettings": {
    "admins": "admin@localhost,owner@localhost"
  },
  "database": {
    "connectionString": "Server=localhost;Password=do-not-leak-me"
  },
  "globalSettings": {
    "webAddress": "https://localhost:8080"
  }
}"""


class FirstAdminTest(unittest.TestCase):
    def test_returns_first_admin_from_real_shape(self):
        path = write_text(REAL_SHAPED)
        self.assertEqual(read_admin_email.first_admin(path), "admin@localhost")

    def test_line_comments_are_tolerated(self):
        path = write_text(
            '{\n  // leading comment\n  "adminSettings": {\n'
            '    "admins": "admin@localhost" // trailing comment\n  }\n}'
        )
        self.assertEqual(read_admin_email.first_admin(path), "admin@localhost")

    def test_block_comments_are_tolerated(self):
        path = write_text(
            '{\n  /* block\n     comment */\n  "adminSettings": {\n'
            '    "admins": "admin@localhost"\n  }\n}'
        )
        self.assertEqual(read_admin_email.first_admin(path), "admin@localhost")

    def test_scheme_separator_in_value_survives_stripper(self):
        # The '//' inside https:// must not be treated as a comment.
        path = write_text(
            '{\n  "adminSettings": { "admins": "admin@localhost" },\n'
            '  "globalSettings": { "webAddress": "https://localhost:8080" }\n}'
        )
        self.assertEqual(read_admin_email.first_admin(path), "admin@localhost")

    def test_top_level_admins_fallback(self):
        path = write_text('{ "admins": "admin@localhost,owner@localhost" }')
        self.assertEqual(read_admin_email.first_admin(path), "admin@localhost")

    def test_comma_separated_returns_first(self):
        path = write_text(
            '{ "adminSettings": { "admins": "first@localhost,second@localhost" } }'
        )
        self.assertEqual(read_admin_email.first_admin(path), "first@localhost")

    def test_json_list_still_accepted(self):
        path = write_text(
            '{ "adminSettings": { "admins": ["admin@localhost", "second@localhost"] } }'
        )
        self.assertEqual(read_admin_email.first_admin(path), "admin@localhost")

    def test_strips_surrounding_whitespace(self):
        path = write_text('{ "adminSettings": { "admins": "  admin@localhost  " } }')
        self.assertEqual(read_admin_email.first_admin(path), "admin@localhost")

    def test_empty_admins_raises(self):
        path = write_text('{ "adminSettings": { "admins": "" } }')
        with self.assertRaises(ValueError):
            read_admin_email.first_admin(path)

    def test_missing_admins_key_raises(self):
        path = write_text('{ "globalSettings": { "webAddress": "x" } }')
        with self.assertRaises(ValueError):
            read_admin_email.first_admin(path)


class MainTest(unittest.TestCase):
    def test_prints_only_the_email(self):
        path = write_text(
            '{\n  "adminSettings": { "admins": "admin@localhost" },\n'
            '  "database": { "connectionString": "Password=do-not-leak-me" }\n}'
        )
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            rc = read_admin_email.main(["--secrets-path", path])
        self.assertEqual(rc, 0)
        self.assertEqual(buffer.getvalue().strip(), "admin@localhost")
        self.assertNotIn("do-not-leak-me", buffer.getvalue())

    def test_missing_file_exits_4(self):
        rc = read_admin_email.main(["--secrets-path", "/nonexistent/secrets.json"])
        self.assertEqual(rc, 4)


class ScriptIsExecutableTest(unittest.TestCase):
    def test_script_has_execute_bit(self):
        script_path = os.path.join(SCRIPTS, "read_admin_email.py")
        self.assertTrue(
            os.access(script_path, os.X_OK),
            f"{script_path} must be executable: SKILL.md invokes it by bare "
            "path relying on its shebang, with no python3 prefix",
        )


if __name__ == "__main__":
    unittest.main()
