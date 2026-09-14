#!/usr/bin/env python3
"""Trigger-rate evaluator that checks for the real plugin-registered skill.

Shared by every skill under `bitwarden-testing-tools`. Each skill ships only its
own eval data (`trigger-eval.json` + `baseline.json`); this one engine runs them
all. The target skill token is not hardcoded — it is resolved from `--skill`, or
inferred from the eval-set path (the eval file's grandparent directory is the
skill directory), so adding evals for a new skill never means copying this file.

The skill-creator harness registers a temp copy named `<skill>-skill-<uuid>` and
only counts invocations of that name as triggers. When the real plugin-registered
skill is already installed in the environment running the eval, the model invokes
the real one and the harness records a false negative.

This script runs `claude -p` for each eval query and counts a "trigger" when any
Skill or Read tool call references the real skill token, anywhere in the response.
The scan continues past unrelated Skill invocations (some accounts auto-fire
session-init skills before the model selects a task skill), so the eval is
portable across environments rather than tied to any specific set of installed
plugins.
"""

import argparse
import json
import os
import select
import signal
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path


def _terminate(process) -> None:
    """Kill the subprocess and its whole tree. Each `claude -p` is a ~1GB Node
    process that spawns further Node children; `process.kill()` reaps only the
    parent, orphaning the rest, so a full run leaks Node trees until the machine
    runs out of memory. The subprocess is started in its own session (see the
    `start_new_session` Popen call), so its PID is the process-group ID — signal
    the group to take every descendant down with it."""
    # cspell:ignore killpg
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
    except ProcessLookupError:
        pass


def run_query(query: str, timeout: int, model: str, skill_token: str) -> dict:
    # Restrict the subprocess to the only tools trigger detection observes. The
    # should-not-trigger queries are adversarial real-work prompts ("run the jest
    # suite", "write the unit tests"); without this, the child agents clone repos
    # and run build/test toolchains, and N of them in parallel exhaust memory.
    cmd = [
        "claude",
        "-p", query,
        "--output-format", "stream-json",
        "--verbose",
        "--include-partial-messages",
        "--model", model,
        "--allowedTools", "Skill", "Read",
    ]
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        env=env,
        start_new_session=True,
    )

    triggered = False
    first_skill_seen = None
    start = time.time()
    buffer = ""
    pending = None
    accum = ""

    try:
        while time.time() - start < timeout:
            if process.poll() is not None:
                rest = process.stdout.read()
                if rest:
                    buffer += rest.decode("utf-8", errors="replace")
                break
            ready, _, _ = select.select([process.stdout], [], [], 1.0)
            if not ready:
                continue
            chunk = os.read(process.stdout.fileno(), 8192)
            if not chunk:
                break
            buffer += chunk.decode("utf-8", errors="replace")

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if event.get("type") == "stream_event":
                    se = event.get("event", {})
                    if se.get("type") == "content_block_start":
                        cb = se.get("content_block", {})
                        if cb.get("type") == "tool_use" and cb.get("name") in ("Skill", "Read"):
                            pending = cb.get("name")
                            accum = ""
                        # Other tool types are ignored — we only care whether the
                        # target skill is invoked at some point in the response.
                    elif se.get("type") == "content_block_delta" and pending:
                        delta = se.get("delta", {})
                        if delta.get("type") == "input_json_delta":
                            accum += delta.get("partial_json", "")
                            if skill_token in accum:
                                return {"triggered": True, "first_skill": accum}
                    elif se.get("type") == "content_block_stop" and pending:
                        if first_skill_seen is None:
                            first_skill_seen = accum
                        # Keep scanning past unrelated Skill/Read invocations so
                        # the eval is portable across accounts that auto-fire
                        # session-init or workflow skills before the task skill.
                        pending = None
                        accum = ""
                elif event.get("type") == "assistant":
                    msg = event.get("message", {})
                    for item in msg.get("content", []):
                        if item.get("type") != "tool_use":
                            continue
                        name = item.get("name")
                        inp = item.get("input", {})
                        if name == "Skill" and skill_token in inp.get("skill", ""):
                            return {"triggered": True, "first_skill": inp.get("skill")}
                        if name == "Read" and skill_token in inp.get("file_path", ""):
                            return {"triggered": True, "first_skill": inp.get("file_path")}
                elif event.get("type") == "result":
                    return {"triggered": triggered, "first_skill": first_skill_seen}
    finally:
        _terminate(process)
    return {"triggered": triggered, "first_skill": first_skill_seen}


def runs_for(query, should_trigger, runs, timeout, model, skill_token):
    triggers = 0
    samples = []
    for _ in range(runs):
        r = run_query(query, timeout, model, skill_token)
        if r["triggered"]:
            triggers += 1
        samples.append(r.get("first_skill"))
    rate = triggers / runs
    # Surface samples to stderr only when the per-query outcome disagrees with
    # `should_trigger`, so debugging info is available without baking
    # environment-specific tool inputs (absolute paths, etc.) into the
    # persisted result that the README diffs for regression checks.
    if (rate >= 0.5) != should_trigger:
        for s in samples:
            print(f"    sample: {s}", file=sys.stderr)
    return {
        "query": query,
        "should_trigger": should_trigger,
        "triggers": triggers,
        "runs": runs,
        "trigger_rate": rate,
    }


def resolve_skill_token(args) -> str:
    if args.skill:
        return args.skill
    # The eval file lives at skills/<skill>/evals/<file>; the skill directory is
    # its grandparent, so a run from a skill's evals/ dir needs no --skill flag.
    return Path(args.eval_set).resolve().parents[1].name


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval-set", required=True)
    parser.add_argument("--skill", help="Target skill token; inferred from --eval-set path when omitted.")
    parser.add_argument("--runs-per-query", type=int, default=3)
    # Each worker holds one ~1GB `claude -p` Node process open at a time; cap the
    # default low so a full run fits in memory on a typical machine.
    parser.add_argument("--num-workers", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--model", default="claude-sonnet-5")
    args = parser.parse_args()

    skill_token = resolve_skill_token(args)
    eval_set = json.loads(Path(args.eval_set).read_text())
    results = [None] * len(eval_set)
    with ProcessPoolExecutor(max_workers=args.num_workers) as pool:
        futures = {
            pool.submit(runs_for, e["query"], e["should_trigger"], args.runs_per_query, args.timeout, args.model, skill_token): i
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


if __name__ == "__main__":
    main()
