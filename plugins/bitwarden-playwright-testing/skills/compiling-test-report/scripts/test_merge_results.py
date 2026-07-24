#!/usr/bin/env python3
"""Unit tests for merge_results: segment assembly, derived totals, validation.

Run with:  python3 -m unittest test_merge_results   (from the scripts/ dir)
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import merge_results

EXAMPLES = os.path.join(HERE, "..", "references", "examples")


def load_example(name):
    with open(os.path.join(EXAMPLES, name), encoding="utf-8") as f:
        return json.load(f)


class MergeTest(unittest.TestCase):
    def test_merge_two_segments_completes(self):
        result = merge_results.merge(
            [load_example("paused-segment.json"), load_example("resume-segment.json")]
        )
        self.assertEqual(result["run_status"], "complete")
        self.assertEqual([c["number"] for c in result["cases"]], [1, 2])
        self.assertEqual(
            result["totals"],
            {"total": 2, "passed": 1, "adaptive": 0, "failed": 1, "errored": 0},
        )
        self.assertNotIn("need_user_input", result)

    def test_single_paused_segment_carries_question(self):
        result = merge_results.merge([load_example("paused-segment.json")])
        self.assertEqual(result["run_status"], "paused")
        self.assertEqual(result["totals"]["total"], 1)
        self.assertIn("Attach a Stripe test clock", result["need_user_input"])

    def test_aborted_segment(self):
        result = merge_results.merge([load_example("aborted-run.json")])
        self.assertEqual(result["run_status"], "aborted")
        self.assertEqual(result["cases"], [])
        self.assertIn("login failed", result["abort_reason"])

    def test_bad_status_exits_3(self):
        with self.assertRaises(SystemExit) as cm:
            merge_results.merge(
                [{"run_status": "complete", "cases": [{"number": 1, "name": "x", "status": "NOPE"}]}]
            )
        self.assertEqual(cm.exception.code, 3)

    def test_main_writes_and_reports_status(self):
        d = tempfile.mkdtemp()
        seg = os.path.join(d, "s1.json")
        out = os.path.join(d, "out.json")
        with open(seg, "w", encoding="utf-8") as f:
            json.dump(load_example("aborted-run.json"), f)
        rc = merge_results.main([seg, "--output", out])
        self.assertEqual(rc, 0)
        with open(out, encoding="utf-8") as f:
            written = json.load(f)
        self.assertEqual(written["run_status"], "aborted")


if __name__ == "__main__":
    unittest.main()
