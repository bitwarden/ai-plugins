#!/usr/bin/env python3
"""Non-trigger evaluator for the six agents `start-playwright-test` dispatches.

Every one of those agent descriptions claims "Do not invoke directly". This
measures whether that holds: run it once per agent name and expect zero
triggers across the whole query set.

Usage: run_agent_eval.py --agent <agent-name> [harness args...]
"""

import sys
from pathlib import Path

# Top-level, not inside a function: a spawned child re-imports this module and
# needs the path set before it can import the harness.
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from eval_harness import EvalConfig, main  # noqa: E402

AGENTS = (
    "playwright-test-context-gatherer",
    "playwright-test-case-scoper",
    "services-under-test-mapper",
    "playwright-test-case-writer",
    "localhost-web-health-checker",
    "playwright-test-runner",
)

if __name__ == "__main__":
    if "--agent" not in sys.argv:
        sys.exit(f"--agent is required, one of: {', '.join(AGENTS)}")
    i = sys.argv.index("--agent")
    agent = sys.argv[i + 1]
    if agent not in AGENTS:
        sys.exit(f"unknown agent {agent!r}, expected one of: {', '.join(AGENTS)}")
    del sys.argv[i : i + 2]
    sys.exit(main(EvalConfig(target_skill_token=agent)))
