#!/usr/bin/env python3
"""Unit tests for check_feature_flags: the running Api is the authority, and
secrets.json and the server source are read only for the requested keys.

The HTTP fetch and file reads are injected, and server source trees are built in
temporary directories, so no test touches the network or the developer's real
secrets file or server checkout.

Run with:  python3 -m unittest discover -s scripts/tests   (from the skill dir)
"""
# cspell:ignore flagvalues
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
import urllib.error
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)

import check_feature_flags as cff

FLAG = "pm-38333-annual-billing-savings"
SECRETS_PATH = "server/dev/secrets.json"
SERVER_SRC = "server/src"
FOLLOW_UP = "  Then refresh secrets and restart the dependent services."
NOT_DECLARED = f"no [FlagKeyCollection] class under {SERVER_SRC} declares this flag"
COLLECTION_TEXT = f"""[FlagKeyCollection]
public static partial class InvoicingFeatureFlags
{{
    public const string PM38333_AnnualBillingSavings = "{FLAG}";
}}"""

# Shaped like the real server/dev/secrets.json: JSONC comments, a trailing
# comma, an https:// value, and secrets that must never reach the output.
SECRETS_TEXT = """{
  // dev settings
  "globalSettings": {
    "baseServiceUri": { "vault": "https://localhost:8080" },
    "sqlServer": { "connectionString": "Server=localhost;Password=do-not-leak-me" },
    "launchDarkly": {
      "flagValues": {
        "pm-38333-annual-billing-savings": "true",
        "pm-11111-other-flag": "true",
      }
    }
  },
  "billingSettings": { "stripeApiKey": "sk_test_do-not-leak" }
}"""


def config_body(states):
    return json.dumps({"version": "2026.10.0", "featureStates": states})


def secrets_from(text):
    data, problem = cff.load_secrets(SECRETS_PATH, lambda _path: text)
    assert problem is None, problem
    return data


def write_source(root, relative_path, text):
    path = os.path.join(root, relative_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


class ParseRequirementsTest(unittest.TestCase):
    def test_on_and_off_are_parsed(self):
        self.assertEqual(
            cff.parse_requirements([f"{FLAG}=on", "vfo1-foundation=off"]),
            [(FLAG, True), ("vfo1-foundation", False)],
        )

    def test_uppercase_constant_name_is_refused(self):
        with self.assertRaises(ValueError) as cm:
            cff.parse_requirements(["PM38333_AnnualBillingSavings=on"])
        self.assertIn("PM38333_AnnualBillingSavings=on", str(cm.exception))

    def test_missing_state_is_refused(self):
        with self.assertRaises(ValueError):
            cff.parse_requirements([FLAG])

    def test_state_other_than_on_or_off_is_refused(self):
        with self.assertRaises(ValueError):
            cff.parse_requirements([f"{FLAG}=true"])

    def test_path_shaped_key_is_refused(self):
        with self.assertRaises(ValueError):
            cff.parse_requirements(["../secrets=on"])

    def test_duplicate_flag_is_refused(self):
        with self.assertRaises(ValueError) as cm:
            cff.parse_requirements([f"{FLAG}=on", f"{FLAG}=off"])
        self.assertIn("more than once", str(cm.exception))


class FetchFeatureStatesTest(unittest.TestCase):
    def test_returns_the_feature_states(self):
        urls = []

        def fetch(url):
            urls.append(url)
            return config_body({FLAG: True})

        self.assertEqual(cff.fetch_feature_states(fetch), {FLAG: True})
        self.assertEqual(urls, ["http://localhost:4000/config"])

    def test_unreachable_api_is_an_api_error(self):
        def fetch(_url):
            raise urllib.error.URLError("connection refused")

        with self.assertRaises(cff.ApiError):
            cff.fetch_feature_states(fetch)

    def test_non_json_response_is_an_api_error(self):
        with self.assertRaises(cff.ApiError):
            cff.fetch_feature_states(lambda _url: "<html>")

    def test_missing_feature_states_is_an_api_error(self):
        with self.assertRaises(cff.ApiError):
            cff.fetch_feature_states(lambda _url: json.dumps({"version": "x"}))

    def test_http_get_bypasses_proxies(self):
        handlers = []

        def build_opener(*args):
            handlers.extend(args)
            raise urllib.error.URLError("stop before any network call")

        with mock.patch.object(cff.urllib.request, "build_opener", build_opener):
            with self.assertRaises(urllib.error.URLError):
                cff._http_get(cff.CONFIG_URL)
        proxy_handlers = [h for h in handlers if isinstance(h, urllib.request.ProxyHandler)]
        self.assertEqual(len(proxy_handlers), 1)
        self.assertEqual(proxy_handlers[0].proxies, {})


class LoadSecretsTest(unittest.TestCase):
    def test_jsonc_with_trailing_comma_parses(self):
        data = secrets_from(SECRETS_TEXT)
        self.assertIn("globalSettings", data)

    def test_missing_file_is_not_fatal(self):
        def read(_path):
            raise FileNotFoundError(_path)

        data, problem = cff.load_secrets(SECRETS_PATH, read)
        self.assertIsNone(data)
        self.assertIn("was not found", problem)

    def test_unreadable_file_is_not_fatal(self):
        def read(_path):
            raise IsADirectoryError(_path)

        data, problem = cff.load_secrets(SECRETS_PATH, read)
        self.assertIsNone(data)
        self.assertIn("could not be read", problem)

    def test_unparseable_file_is_not_fatal(self):
        data, problem = cff.load_secrets(SECRETS_PATH, lambda _path: "{ not json")
        self.assertIsNone(data)
        self.assertIn("could not be parsed", problem)


class ConfiguredValueTest(unittest.TestCase):
    def test_reads_the_legacy_section(self):
        self.assertEqual(
            cff.configured_value(secrets_from(SECRETS_TEXT), FLAG),
            (True, "globalSettings.launchDarkly.flagValues"),
        )

    def test_features_section_wins_over_the_legacy_section(self):
        text = json.dumps({
            "features": {"flagValues": {FLAG: "false"}},
            "globalSettings": {"launchDarkly": {"flagValues": {FLAG: "true"}}},
        })
        self.assertEqual(
            cff.configured_value(secrets_from(text), FLAG),
            (False, "features.flagValues"),
        )

    def test_section_and_key_names_ignore_case(self):
        text = json.dumps({
            "GlobalSettings": {"LaunchDarkly": {"FlagValues": {FLAG.upper(): True}}},
        })
        self.assertEqual(
            cff.configured_value(secrets_from(text), FLAG),
            (True, "globalSettings.launchDarkly.flagValues"),
        )

    def test_unset_flag_has_no_configured_value(self):
        self.assertEqual(
            cff.configured_value(secrets_from(SECRETS_TEXT), "pm-99999-unset"),
            (None, None),
        )


class DeclaresFlagTest(unittest.TestCase):
    def setUp(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.root = temp_dir.name

    def declares(self, key=FLAG):
        return cff.declares_flag(self.root, key, cff._read_text)

    def test_key_in_a_library_flag_collection_is_declared(self):
        write_source(self.root, "Libraries/Invoicing/InvoicingFeatureFlags.cs", COLLECTION_TEXT)
        self.assertIs(self.declares(), True)

    def test_key_declared_nowhere_is_not_declared(self):
        write_source(self.root, "Libraries/Invoicing/InvoicingFeatureFlags.cs", COLLECTION_TEXT)
        self.assertIs(self.declares("pm-99999-unset"), False)

    def test_key_outside_a_flag_collection_is_not_declared(self):
        write_source(self.root, "Api/SomeController.cs", f'// see "{FLAG}"')
        self.assertIs(self.declares(), False)

    def test_build_output_is_ignored(self):
        write_source(self.root, "Core/obj/Debug/Generated.cs", COLLECTION_TEXT)
        write_source(self.root, "Core/bin/Debug/Generated.cs", COLLECTION_TEXT)
        self.assertIs(self.declares(), False)

    def test_non_cs_files_are_ignored(self):
        write_source(self.root, "Core/flags.txt", COLLECTION_TEXT)
        self.assertIs(self.declares(), False)

    def test_missing_source_tree_is_unknown(self):
        self.assertIsNone(cff.declares_flag(os.path.join(self.root, "missing"), FLAG, cff._read_text))

    def test_unreadable_source_file_is_unknown(self):
        write_source(self.root, "Core/Constants.cs", COLLECTION_TEXT)

        def read(_path):
            raise PermissionError(_path)

        self.assertIsNone(cff.declares_flag(self.root, FLAG, read))


class EvaluateTest(unittest.TestCase):
    def evaluate(self, requirements, states, secrets_text=SECRETS_TEXT, declared=True):
        secrets = secrets_from(secrets_text) if secrets_text is not None else None
        problem = None if secrets_text is not None else f"{SECRETS_PATH} was not found"
        return cff.evaluate(
            requirements, states, secrets, problem, SECRETS_PATH,
            lambda _key: declared, SERVER_SRC,
        )

    def test_required_on_and_running_on_is_ok(self):
        lines, ok = self.evaluate([(FLAG, True)], {FLAG: True})
        self.assertTrue(ok)
        self.assertEqual(lines, [f"{FLAG}: required on, running on — OK"])

    def test_required_off_and_not_reported_is_ok(self):
        lines, ok = self.evaluate([(FLAG, False)], {})
        self.assertTrue(ok)
        self.assertIn("not reported (treated as off) — OK", lines[0])

    def test_string_true_from_the_api_counts_as_on(self):
        _lines, ok = self.evaluate([(FLAG, True)], {FLAG: "true"})
        self.assertTrue(ok)

    def test_every_mismatch_ends_with_the_follow_up(self):
        lines, ok = self.evaluate([(FLAG, True)], {FLAG: False})
        self.assertFalse(ok)
        self.assertIn("MISMATCH", lines[0])
        self.assertEqual(lines[-1], FOLLOW_UP)

    def test_configured_but_running_off_says_the_api_has_not_picked_it_up(self):
        lines, _ok = self.evaluate([(FLAG, True)], {FLAG: False})
        self.assertEqual(
            lines[1],
            f'  Problem: globalSettings.launchDarkly.flagValues in {SECRETS_PATH} '
            'already sets it to "true", but the running Api has not picked it up.',
        )

    def test_unset_flag_says_where_to_set_it(self):
        text = json.dumps({"globalSettings": {"launchDarkly": {"flagValues": {}}}})
        lines, ok = self.evaluate([(FLAG, True)], {FLAG: False}, secrets_text=text)
        self.assertFalse(ok)
        self.assertEqual(
            lines[1],
            f'  Problem: set "{FLAG}": "true" under globalSettings.launchDarkly.flagValues '
            f"in {SECRETS_PATH}.",
        )

    def test_value_in_features_section_is_fixed_there(self):
        text = json.dumps({"features": {"flagValues": {FLAG: "false"}}})
        lines, _ok = self.evaluate([(FLAG, True)], {FLAG: False}, secrets_text=text)
        self.assertIn("under features.flagValues", lines[1])

    def test_reported_flag_never_checks_the_source(self):
        def is_declared(_key):
            raise AssertionError("a reported flag must not walk the source tree")

        secrets = secrets_from(SECRETS_TEXT)
        _lines, ok = cff.evaluate(
            [(FLAG, True)], {FLAG: False}, secrets, None, SECRETS_PATH, is_declared, SERVER_SRC
        )
        self.assertFalse(ok)

    def test_unreported_flag_missing_from_secrets_and_source_lists_both(self):
        text = json.dumps({})
        lines, _ok = self.evaluate([(FLAG, True)], {}, secrets_text=text, declared=False)
        self.assertEqual(len(lines), 4)
        self.assertIn(f'set "{FLAG}": "true"', lines[1])
        self.assertIn(NOT_DECLARED, lines[2])
        self.assertEqual(lines[3], FOLLOW_UP)

    def test_unreported_flag_set_in_secrets_but_not_declared_names_only_the_source(self):
        lines, _ok = self.evaluate([(FLAG, True)], {}, declared=False)
        self.assertEqual(len(lines), 3)
        self.assertIn(NOT_DECLARED, lines[1])

    def test_unreported_flag_declared_but_unset_names_only_secrets(self):
        text = json.dumps({})
        lines, _ok = self.evaluate([(FLAG, True)], {}, secrets_text=text, declared=True)
        self.assertEqual(len(lines), 3)
        self.assertIn(f'set "{FLAG}": "true"', lines[1])

    def test_unreported_flag_declared_and_set_says_the_api_has_not_picked_it_up(self):
        lines, _ok = self.evaluate([(FLAG, True)], {}, declared=True)
        self.assertEqual(len(lines), 3)
        self.assertIn("has not picked it up", lines[1])

    def test_unreadable_source_is_reported_as_unknown(self):
        lines, _ok = self.evaluate([(FLAG, True)], {}, declared=None)
        self.assertIn(f"{SERVER_SRC} could not be read", lines[1])
        self.assertNotIn("has not picked it up", "".join(lines))

    def test_unreadable_secrets_is_reported_as_unknown(self):
        lines, _ok = self.evaluate([(FLAG, True)], {FLAG: False}, secrets_text=None)
        self.assertEqual(
            lines[1],
            f"  Problem: {SECRETS_PATH} was not found, so its value for this flag is unknown.",
        )
        self.assertEqual(lines[-1], FOLLOW_UP)


class MainTest(unittest.TestCase):
    def run_main(self, argv, states=None, fetch=None, files=None):
        files = {SECRETS_PATH: SECRETS_TEXT} if files is None else files
        calls = []

        def default_fetch(url):
            calls.append(url)
            return config_body(states or {})

        def read_text(path):
            if path not in files:
                raise FileNotFoundError(path)
            return files[path]

        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cff.main(argv, fetch=fetch or default_fetch, read_text=read_text)
        return code, out.getvalue(), err.getvalue(), calls

    def test_all_flags_match_exits_0(self):
        code, out, _err, _calls = self.run_main([f"{FLAG}=on"], states={FLAG: True})
        self.assertEqual(code, cff.EXIT_OK)
        self.assertIn("— OK", out)

    def test_mismatch_exits_3(self):
        code, out, _err, _calls = self.run_main([f"{FLAG}=on"], states={FLAG: False})
        self.assertEqual(code, cff.EXIT_MISMATCH)
        self.assertIn("Problem:", out)

    def test_unreachable_api_exits_1(self):
        def fetch(_url):
            raise urllib.error.URLError("connection refused")

        code, _out, err, _calls = self.run_main([f"{FLAG}=on"], fetch=fetch)
        self.assertEqual(code, cff.EXIT_API)
        self.assertIn("Make sure the Api is running", err)

    def test_bad_argument_exits_2_and_never_calls_the_api(self):
        code, _out, err, calls = self.run_main(["PM38333_AnnualBillingSavings=on"])
        self.assertEqual(code, cff.EXIT_USAGE)
        self.assertEqual(calls, [])
        self.assertIn("PM38333_AnnualBillingSavings=on", err)

    def test_help_is_a_usage_error_and_never_calls_the_api(self):
        # An option-shaped value such as -h must never read as success: the
        # health check treats exit 0 as "every flag is as required".
        with contextlib.redirect_stdout(io.StringIO()):
            code, _out, _err, calls = self.run_main(["--help"])
        self.assertEqual(code, cff.EXIT_USAGE)
        self.assertEqual(calls, [])

    def test_double_dash_ends_options_before_requirements(self):
        code, out, _err, _calls = self.run_main(["--", f"{FLAG}=on"], states={FLAG: True})
        self.assertEqual(code, cff.EXIT_OK)
        self.assertIn("— OK", out)

    def test_option_shaped_requirement_after_double_dash_is_refused(self):
        code, _out, err, calls = self.run_main(["--", "-h=on"])
        self.assertEqual(code, cff.EXIT_USAGE)
        self.assertEqual(calls, [])
        self.assertIn("-h=on", err)

    def test_no_arguments_is_a_usage_error(self):
        with contextlib.redirect_stderr(io.StringIO()):
            code, _out, _err, calls = self.run_main([])
        self.assertEqual(code, cff.EXIT_USAGE)
        self.assertEqual(calls, [])

    def test_missing_secrets_file_is_a_problem_on_mismatch(self):
        code, out, _err, _calls = self.run_main([f"{FLAG}=on"], states={FLAG: False}, files={})
        self.assertEqual(code, cff.EXIT_MISMATCH)
        self.assertIn(f"{SECRETS_PATH} was not found, so its value for this flag is unknown", out)

    def test_server_src_path_is_where_declarations_are_found(self):
        with tempfile.TemporaryDirectory() as root:
            write_source(root, "Libraries/Invoicing/InvoicingFeatureFlags.cs", COLLECTION_TEXT)

            def read_text(path):
                if path == SECRETS_PATH:
                    return json.dumps({})
                return cff._read_text(path)

            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = cff.main(
                    ["--server-src-path", root, "--", f"{FLAG}=on"],
                    fetch=lambda _url: config_body({}),
                    read_text=read_text,
                )
        self.assertEqual(code, cff.EXIT_MISMATCH)
        self.assertIn(f'set "{FLAG}": "true"', out.getvalue())
        self.assertNotIn("declares this flag", out.getvalue())

    def test_no_other_secret_reaches_the_output(self):
        for states in ({FLAG: True}, {FLAG: False}, {}):
            _code, out, err, _calls = self.run_main(
                [f"{FLAG}=on", "pm-99999-unset=on"], states=states
            )
            for leaked in ("do-not-leak", "pm-11111-other-flag", "https://localhost:8080"):
                self.assertNotIn(leaked, out + err)


class ScriptIsExecutableTest(unittest.TestCase):
    def test_script_has_execute_bit(self):
        script_path = os.path.join(SCRIPTS, "check_feature_flags.py")
        self.assertTrue(os.access(script_path, os.X_OK), f"{script_path} must be executable")


if __name__ == "__main__":
    unittest.main()
