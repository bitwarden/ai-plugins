#!/usr/bin/env python3
"""Unit tests for get_admin_email: it emits only the adminSettings.admins value
and never any other field of the secrets file, and honors the exit-code contract.

Run with:  python3 -m unittest discover -s scripts/tests   (from the skill dir)
"""
import contextlib
import io
import json
import os
import shutil
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


class StripJsoncTest(unittest.TestCase):
    def test_strips_line_and_block_comments_and_trailing_commas(self):
        text = """{
            // a leading admin
            "adminSettings": {
                "admins": "admin@localhost", /* the portal login */
            },
        }"""
        self.assertEqual(
            json.loads(get_admin_email.strip_jsonc(text)),
            {"adminSettings": {"admins": "admin@localhost"}},
        )

    def test_preserves_comment_markers_and_commas_inside_strings(self):
        # A // in a URL value and a , before } inside a string must survive.
        text = '{"url": "bitwarden://checkout,}", "n": 1,}'
        self.assertEqual(
            json.loads(get_admin_email.strip_jsonc(text)),
            {"url": "bitwarden://checkout,}", "n": 1},
        )


def make_root(test):
    root = tempfile.mkdtemp()
    test.addCleanup(shutil.rmtree, root, True)
    return root


def write_text(test, text, relative=os.path.join("dev", "secrets.json")):
    """Write text at <temp root>/<relative>, by default a dev/secrets.json."""
    path = os.path.join(make_root(test), relative)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path


class CheckSecretsPathTest(unittest.TestCase):
    def test_dev_secrets_json_is_accepted(self):
        get_admin_email.check_secrets_path("/work/server/dev/secrets.json")

    def test_relative_default_is_accepted(self):
        get_admin_email.check_secrets_path(get_admin_email.DEFAULT_SECRETS_FILE)

    def test_other_file_name_is_refused(self):
        with self.assertRaises(get_admin_email.SecretsPathError):
            get_admin_email.check_secrets_path("/work/server/dev/other.json")

    def test_secrets_json_outside_dev_is_refused(self):
        with self.assertRaises(get_admin_email.SecretsPathError):
            get_admin_email.check_secrets_path("/etc/secrets.json")

    def test_traversal_out_of_dev_is_refused(self):
        with self.assertRaises(get_admin_email.SecretsPathError):
            get_admin_email.check_secrets_path("/work/dev/secrets.json/../../.ssh/config")

    def test_symlink_named_dev_secrets_json_is_refused(self):
        target = write_text(self, "{}", relative="elsewhere.json")
        link_dir = os.path.join(make_root(self), "dev")
        os.makedirs(link_dir)
        link = os.path.join(link_dir, "secrets.json")
        os.symlink(target, link)
        with self.assertRaises(get_admin_email.SecretsPathError):
            get_admin_email.check_secrets_path(link)


class MainTest(unittest.TestCase):
    def _write_secrets(self, payload):
        return write_text(self, json.dumps(payload))

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

    def test_reads_jsonc_secrets_file(self):
        # Mirrors Bitwarden's dev secrets.json: comments and a trailing comma.
        jsonc = """{
            // dev admin accounts
            "adminSettings": {
                "admins": "admin@localhost,owner@localhost", /* portal */
            },
            "globalSettings": {
                "premiumCheckoutSuccessUrl": "bitwarden://result?ok=1",
            },
        }"""
        path = write_text(self, jsonc)
        code, out, _err = self._run(["--secrets-file", path, "--all"])
        self.assertEqual(code, 0)
        self.assertEqual(out.split(), ["admin@localhost", "owner@localhost"])

    def test_output_never_contains_other_secrets(self):
        path = self._write_secrets(SECRETS)
        _code, out, _err = self._run(["--secrets-file", path, "--all"])
        self.assertNotIn("doNotLeakThisValue", out)

    def test_missing_file_exits_3(self):
        code, _out, err = self._run(["--secrets-file", "/nonexistent/dev/secrets.json"])
        self.assertEqual(code, 3)
        self.assertIn("not found", err)

    def test_invalid_json_exits_3(self):
        path = write_text(self, "not json")
        code, _out, err = self._run(["--secrets-file", path])
        self.assertEqual(code, 3)
        self.assertIn("invalid JSON", err)

    def test_path_outside_dev_secrets_json_exits_2_without_reading(self):
        # A JSON file holding an admins value proves the refusal happens before
        # the read: were it read, its address would reach stdout.
        path = write_text(
            self,
            json.dumps({"adminSettings": {"admins": "probe@localhost"}}),
            relative="other.json",
        )
        code, out, err = self._run(["--secrets-file", path])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("dev/secrets.json", err)

    def test_missing_admins_key_exits_3(self):
        path = self._write_secrets({"adminSettings": {}})
        code, _out, _err = self._run(["--secrets-file", path])
        self.assertEqual(code, 3)


if __name__ == "__main__":
    unittest.main()
