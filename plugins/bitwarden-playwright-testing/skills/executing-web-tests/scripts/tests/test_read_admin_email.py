#!/usr/bin/env python3
"""Unit tests for read_admin_email: narrow extraction from the dev secrets file.

Run with:  python3 -m unittest discover -s scripts/tests   (from the skill dir)
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)

import read_admin_email


def write_secrets(payload):
    d = tempfile.mkdtemp()
    path = os.path.join(d, "secrets.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    return path


class FirstAdminTest(unittest.TestCase):
    def test_returns_first_admin(self):
        path = write_secrets(
            {"admins": ["admin@bitwarden.test", "second@bitwarden.test"],
             "sqlPassword": "should-never-be-read"}
        )
        self.assertEqual(read_admin_email.first_admin(path), "admin@bitwarden.test")

    def test_strips_surrounding_whitespace(self):
        path = write_secrets({"admins": ["  admin@bitwarden.test  "]})
        self.assertEqual(read_admin_email.first_admin(path), "admin@bitwarden.test")

    def test_empty_admins_raises(self):
        path = write_secrets({"admins": []})
        with self.assertRaises(ValueError):
            read_admin_email.first_admin(path)

    def test_missing_admins_key_raises(self):
        path = write_secrets({"sqlPassword": "x"})
        with self.assertRaises(ValueError):
            read_admin_email.first_admin(path)


class MainTest(unittest.TestCase):
    def test_prints_only_the_email(self):
        path = write_secrets(
            {"admins": ["admin@bitwarden.test"], "stripeApiKey": "sk_test_secret"}
        )
        import io
        from contextlib import redirect_stdout

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            rc = read_admin_email.main(["--secrets-path", path])
        self.assertEqual(rc, 0)
        self.assertEqual(buffer.getvalue().strip(), "admin@bitwarden.test")
        self.assertNotIn("sk_test_secret", buffer.getvalue())

    def test_missing_file_exits_4(self):
        rc = read_admin_email.main(["--secrets-path", "/nonexistent/secrets.json"])
        self.assertEqual(rc, 4)


if __name__ == "__main__":
    unittest.main()
