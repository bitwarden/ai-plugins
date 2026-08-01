#!/usr/bin/env python3
"""Trigger-rate evaluator for the installed `reading-mailcatcher-api` skill.

Thin wrapper over the plugin's shared eval harness. See
`plugins/bitwarden-testing-tools/scripts/eval_harness.py` for the runner and
for why this exists rather than the `skill-creator` harness.
"""

import sys
from pathlib import Path

# Top-level, not inside a function: a spawned child re-imports this module and
# needs the path set before it can import the harness.
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from eval_harness import EvalConfig, main  # noqa: E402

CONFIG = EvalConfig(target_skill_token="reading-mailcatcher-api")

if __name__ == "__main__":
    sys.exit(main(CONFIG))
