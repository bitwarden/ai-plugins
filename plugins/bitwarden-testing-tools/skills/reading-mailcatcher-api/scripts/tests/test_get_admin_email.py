#!/usr/bin/env python3
"""Unit tests for get_admin_email: it emits only the adminSettings.admins value
and never any other field of the secrets file, and honors the exit-code contract.

Run with:  python3 -m unittest discover -s scripts/tests   (from the skill dir)
"""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)

import get_admin_email

# A secrets fixture that carries admin addresses alongside unrelated secrets.
# The sentinel proves those other fields never reach stdout.
SECRETS = {
    "adminSettings": {
        "admins": "admin@localhost,owner@localhost,cs@localhost",
    },
    "globalSettings": {
        "sqlServer": {"connectionString": "Password=doNotLeakThisValue"},
        "stripeApiKey": "test-key-doNotLeakThisValue",
    },
}


class ExtractAdminsTest(unittest.TestCase):
    def test_splits_comma_separated_admins(self):
        self.assertEqual(
            get_admin_email.extract_admins(SECRETS),
            ["admin@localhost", "owner@localhost", "cs@localhost"],
        )

    def test_missing_admin_settings_raises(self):
        with self.assertRaises(get_admin_email.SecretsError):
            get_admin_email.extract_admins({"other": {}})

    def test_missing_admins_key_raises(self):
        with self.assertRaises(get_admin_email.SecretsError):
            get_admin_email.extract_admins({"adminSettings": {}})

    def test_empty_admins_raises(self):
        with self.assertRaises(get_admin_email.SecretsError):
            get_admin_email.extract_admins({"adminSettings": {"admins": " , "}})

    def test_non_string_admins_raises(self):
        with self.assertRaises(get_admin_email.SecretsError):
            get_admin_email.extract_admins({"adminSettings": {"admins": ["a@b"]}})


class MainTest(unittest.TestCase):
    def _write_secrets(self, payload):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle)
        self.addCleanup(os.unlink, path)
        return path

    def _run(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = get_admin_email.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_default_prints_only_first_admin(self):
        path = self._write_secrets(SECRETS)
        code, out, _err = self._run(["--secrets-file", path])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "admin@localhost")

    def test_all_lists_every_admin(self):
        path = self._write_secrets(SECRETS)
        code, out, _err = self._run(["--secrets-file", path, "--all"])
        self.assertEqual(code, 0)
        self.assertEqual(
            out.split(), ["admin@localhost", "owner@localhost", "cs@localhost"]
        )

    def test_output_never_contains_other_secrets(self):
        path = self._write_secrets(SECRETS)
        _code, out, _err = self._run(["--secrets-file", path, "--all"])
        self.assertNotIn("doNotLeakThisValue", out)

    def test_missing_file_exits_3(self):
        code, _out, err = self._run(["--secrets-file", "/nonexistent/secrets.json"])
        self.assertEqual(code, 3)
        self.assertIn("not found", err)

    def test_invalid_json_exits_3(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write("not json")
        self.addCleanup(os.unlink, path)
        code, _out, err = self._run(["--secrets-file", path])
        self.assertEqual(code, 3)
        self.assertIn("invalid JSON", err)

    def test_missing_admins_key_exits_3(self):
        path = self._write_secrets({"adminSettings": {}})
        code, _out, _err = self._run(["--secrets-file", path])
        self.assertEqual(code, 3)


if __name__ == "__main__":
    unittest.main()
