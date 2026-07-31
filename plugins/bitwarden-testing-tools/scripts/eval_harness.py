#!/usr/bin/env python3
"""Shared trigger-rate evaluator for `bitwarden-testing-tools` skills.

Unlike the skill-creator harness (which only counts a temp `*-skill-<uuid>`
copy), this runs `claude -p` per query and counts a trigger when any Skill or
Read call references the real skill token — so it works against the real
installed skill and is portable across environments. Read-only `gh`/`git`
lookups (see EvalConfig.read_only_bash) are scanned past, but any other
real-work tool (see EvalConfig.exec_tools) bails to avoid the adversarial
should-not-trigger queries cloning repos and spawning toolchains until they
exhaust memory.

Each skill's `evals/run_real_eval.py` is a thin wrapper that builds an
`EvalConfig` for its own target skill token and calls `main(config)`.
"""

import argparse
import json
import os
import select
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class EvalConfig:
    target_skill_token: str

    # Requesting one of these means the model chose real work over the target
    # skill; we bail on it (see run_query) to avoid the heavy child processes
    # it would spawn.
    exec_tools: frozenset = field(default_factory=lambda: frozenset({"Bash", "Task"}))

    # Read-only Bash lookups scanned past instead of counted as real work.
    read_only_bash: tuple = (
        "gh pr view",
        "gh pr list",
        "gh search",
        "gh api",
        "git rev-parse",
        "git remote",
    )

    # A read-only prefix only earns the carve-out if it's a single command; any
    # shell operator could chain heavy work onto it (`gh api ... && npm test`).
    shell_chains: tuple = (";", "|", "&", "`", "$(", "\n")


def is_read_only_bash(command: str, config: EvalConfig) -> bool:
    return command.startswith(config.read_only_bash) and not any(
        op in command for op in config.shell_chains
    )


def run_query(query: str, timeout: int, model: str, config: EvalConfig) -> dict:
    cmd = [
        "claude",
        "-p", query,
        "--output-format", "stream-json",
        "--verbose",
        "--model", model,
    ]
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        env=env,
    )

    first_skill_seen = None
    start = time.time()
    buffer = ""
    # Assume a timeout until we see a decisive event or a clean EOF; the caller
    # uses this to distinguish a slow run from a genuine non-trigger.
    timed_out = True

    def scan():
        # Parse complete lines out of `buffer`, returning a terminal result dict
        # once the target skill triggers or a real-work tool is reached, else
        # None. Mutates `buffer`, leaving any trailing partial line in place.
        nonlocal buffer, first_skill_seen
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            if event.get("type") == "assistant":
                msg = event.get("message", {})
                for item in msg.get("content", []):
                    if item.get("type") != "tool_use":
                        continue
                    name = item.get("name")
                    inp = item.get("input", {})
                    if name == "Skill" and config.target_skill_token in inp.get("skill", ""):
                        return {"triggered": True, "first_skill": inp.get("skill")}
                    fp = inp.get("file_path", "")
                    # Count a Read only when it opens the skill's own SKILL.md,
                    # not any file that merely has the token in its path.
                    if name == "Read" and config.target_skill_token in fp and fp.rstrip().endswith("SKILL.md"):
                        return {"triggered": True, "first_skill": fp}
                    # A real-work tool without the target skill first → no
                    # trigger. Bail so the finally block kills the child before
                    # its tool_use spawns anything. (Cheap read-only tools are
                    # scanned past; the model may inspect files first.)
                    if name == "Bash":
                        cmd = inp.get("command", "").strip()
                        if is_read_only_bash(cmd, config):
                            continue
                    if name in config.exec_tools:
                        if first_skill_seen is None:
                            first_skill_seen = f"{name} (bailed: real-work tool)"
                        return {"triggered": False, "first_skill": first_skill_seen}
            elif event.get("type") == "result":
                return {"triggered": False, "first_skill": first_skill_seen}
        return None

    try:
        while time.time() - start < timeout:
            if process.poll() is not None:
                rest = process.stdout.read()
                if rest:
                    buffer += rest.decode("utf-8", errors="replace")
                # Child exited — parse the final buffer before giving up so a
                # trigger event in the last chunk isn't dropped as a non-trigger.
                result = scan()
                if result is not None:
                    return result
                timed_out = False
                break
            ready, _, _ = select.select([process.stdout], [], [], 1.0)
            if not ready:
                continue
            chunk = os.read(process.stdout.fileno(), 8192)
            if not chunk:
                timed_out = False
                break
            buffer += chunk.decode("utf-8", errors="replace")

            result = scan()
            if result is not None:
                return result
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
    return {"triggered": False, "first_skill": first_skill_seen, "timed_out": timed_out}


def runs_for(query, should_trigger, runs, timeout, model, config: EvalConfig):
    triggers = 0
    timeouts = 0
    samples = []
    for _ in range(runs):
        r = run_query(query, timeout, model, config)
        if r["triggered"]:
            triggers += 1
        if r.get("timed_out"):
            timeouts += 1
        samples.append(r.get("first_skill"))
    rate = triggers / runs
    # Print samples to stderr only on unexpected outcomes — keeps env-specific
    # paths out of the persisted result used for regression diffs.
    if (rate >= 0.5) != should_trigger:
        for s in samples:
            print(f"    sample: {s}", file=sys.stderr)
    # A timeout is counted as a non-trigger, so warn (stderr only, not persisted)
    # to keep a slow should-trigger run from silently reading as a real failure.
    if timeouts:
        print(f"    warning: {timeouts}/{runs} run(s) timed out (counted as non-trigger): {query[:80]}", file=sys.stderr)
    return {
        "query": query,
        "should_trigger": should_trigger,
        "triggers": triggers,
        "runs": runs,
        "trigger_rate": rate,
    }


def main(config: EvalConfig):
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval-set", required=True)
    parser.add_argument("--runs-per-query", type=int, default=3)
    parser.add_argument("--num-workers", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=45)
    parser.add_argument("--model", default="claude-opus-4-8")
    args = parser.parse_args()

    eval_set = json.loads(Path(args.eval_set).read_text())
    results = [None] * len(eval_set)
    with ProcessPoolExecutor(max_workers=args.num_workers) as pool:
        futures = {
            pool.submit(runs_for, e["query"], e["should_trigger"], args.runs_per_query, args.timeout, args.model, config): i
            for i, e in enumerate(eval_set)
        }
        for fut in as_completed(futures):
            i = futures[fut]
            results[i] = fut.result()
            r = results[i]
            tag = "PASS" if (r["trigger_rate"] >= 0.5) == r["should_trigger"] else "FAIL"
            print(f"  [{tag}] rate={r['triggers']}/{r['runs']} expected={r['should_trigger']}: {r['query'][:80]}", file=sys.stderr)

    triggers_pass = sum(1 for r in results if r["should_trigger"] and r["trigger_rate"] >= 0.5)
    triggers_total = sum(1 for r in results if r["should_trigger"])
    no_trigger_pass = sum(1 for r in results if not r["should_trigger"] and r["trigger_rate"] < 0.5)
    no_trigger_total = sum(1 for r in results if not r["should_trigger"])

    summary = {
        "should_trigger_pass_rate": triggers_pass / triggers_total if triggers_total else None,
        "should_not_trigger_pass_rate": no_trigger_pass / no_trigger_total if no_trigger_total else None,
        "should_trigger_pass": f"{triggers_pass}/{triggers_total}",
        "should_not_trigger_pass": f"{no_trigger_pass}/{no_trigger_total}",
        "results": results,
    }
    print(json.dumps(summary, indent=2, default=str))
