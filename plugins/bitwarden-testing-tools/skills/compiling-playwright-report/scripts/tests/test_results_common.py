#!/usr/bin/env python3
"""Unit tests for results_common, the helpers shared by the report scripts.

Run with:  python3 -m unittest discover -s scripts/tests   (from the skill dir)
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)

import results_common


class TallyTest(unittest.TestCase):
    def test_counts_by_status(self):
        cases = [
            {"status": "PASS"},
            {"status": "PASS (adaptive)"},
            {"status": "FAIL"},
            {"status": "ERROR"},
            {"status": "PASS"},
        ]
        self.assertEqual(
            results_common.tally(cases),
            {"total": 5, "passed": 2, "adaptive": 1, "failed": 1, "errored": 1},
        )

    def test_invalid_status_exits_3(self):
        with self.assertRaises(SystemExit) as cm:
            results_common.tally([{"number": 1, "status": "NOPE"}])
        self.assertEqual(cm.exception.code, 3)


if __name__ == "__main__":
    unittest.main()
