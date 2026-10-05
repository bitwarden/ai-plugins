#!/usr/bin/env python3
"""Unit tests for check_feature_flags: the running Api is the authority, and
secrets.json is read only for the requested keys.

The HTTP fetch and file reads are injected, so no test touches the network or
the developer's real secrets file.

Run with:  python3 -m unittest discover -s scripts/tests   (from the skill dir)
"""
# cspell:ignore flagvalues
import contextlib
import io
import json
import os
import sys
import unittest
import urllib.error
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)

import check_feature_flags as cff

FLAG = "pm-38333-annual-billing-savings"
SECRETS_PATH = "server/dev/secrets.json"
CONSTANTS_PATH = "server/src/Core/Constants.cs"
CONSTANTS_TEXT = f'public const string PM38333_AnnualBillingSavings = "{FLAG}";'
APPLY_SECRETS = (
    "apply it with `pwsh ./setup_secrets.ps1` from server/dev (or re-run the "
    "setup-secrets resource in the Aspire dashboard)"
)

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


class EvaluateTest(unittest.TestCase):
    def evaluate(self, requirements, states, secrets_text=SECRETS_TEXT,
                 constants_text=CONSTANTS_TEXT):
        secrets = secrets_from(secrets_text) if secrets_text is not None else None
        return cff.evaluate(
            requirements, states, secrets, SECRETS_PATH, constants_text, CONSTANTS_PATH
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

    def test_configured_but_running_off_says_apply_secrets_then_restart(self):
        # The Api reads dotnet user-secrets, which setup_secrets.ps1 copies from
        # secrets.json, so a restart alone cannot pick up a secrets.json change.
        lines, ok = self.evaluate([(FLAG, True)], {FLAG: False})
        self.assertFalse(ok)
        self.assertIn("MISMATCH", lines[0])
        self.assertIn("already sets it", lines[1])
        self.assertIn(APPLY_SECRETS, lines[1])
        self.assertTrue(lines[1].endswith("then restart the Api."))

    def test_unset_flag_says_where_to_set_it(self):
        text = json.dumps({"globalSettings": {"launchDarkly": {"flagValues": {}}}})
        lines, ok = self.evaluate([(FLAG, True)], {FLAG: False}, secrets_text=text)
        self.assertFalse(ok)
        self.assertIn(
            f'Set "{FLAG}": "true" under globalSettings.launchDarkly.flagValues '
            f"in {SECRETS_PATH}, {APPLY_SECRETS}, then restart the Api.",
            lines[1],
        )

    def test_value_in_features_section_is_fixed_there(self):
        text = json.dumps({"features": {"flagValues": {FLAG: "false"}}})
        lines, _ok = self.evaluate([(FLAG, True)], {FLAG: False}, secrets_text=text)
        self.assertIn("under features.flagValues", lines[1])

    def test_flag_the_server_does_not_define_says_so(self):
        lines, ok = self.evaluate([(FLAG, True)], {}, constants_text="// no flags here")
        self.assertFalse(ok)
        self.assertIn(f"{CONSTANTS_PATH} does not define this flag", lines[1])

    def test_unknown_constants_falls_back_to_secrets_advice(self):
        lines, _ok = self.evaluate([(FLAG, True)], {}, constants_text=None)
        self.assertIn("already sets it", lines[1])
        self.assertIn(APPLY_SECRETS, lines[1])

    def test_unreadable_secrets_still_gives_a_resolve_line(self):
        lines, _ok = self.evaluate([(FLAG, True)], {FLAG: False}, secrets_text=None)
        self.assertIn(f"{SECRETS_PATH} could not be read", lines[1])
        self.assertIn(APPLY_SECRETS, lines[1])


class MainTest(unittest.TestCase):
    def run_main(self, argv, states=None, fetch=None, files=None):
        files = {SECRETS_PATH: SECRETS_TEXT, CONSTANTS_PATH: CONSTANTS_TEXT} if files is None else files
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
        self.assertIn("Resolve:", out)

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

    def test_missing_secrets_file_adds_a_note_on_mismatch(self):
        code, out, _err, _calls = self.run_main(
            [f"{FLAG}=on"], states={FLAG: False}, files={CONSTANTS_PATH: CONSTANTS_TEXT}
        )
        self.assertEqual(code, cff.EXIT_MISMATCH)
        self.assertIn("configured values are unknown", out)

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
