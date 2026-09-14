#!/usr/bin/env python3
"""Trigger-rate evaluator: runs `claude -p` per eval query and counts a trigger
only on a plugin-qualified Skill invocation (`<plugin>:<skill>`) or a Read of the
skill's own `SKILL.md`.

Shared by every skill under `bitwarden-testing-tools`. See evals/README.md for the
rationale, arguments, and how to add evals for a new skill.
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


def run_query(query: str, timeout: int, model: str, skill_token: str, plugin: str) -> dict:
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

    # A trigger is the plugin-qualified skill invocation or a Read of the skill's
    # own SKILL.md, never a bare token substring: the eval runs from the skill's
    # evals/ dir, so an exploratory read there carries the token in its path.
    skill_needle = f"{plugin}:{skill_token}"
    read_needle = f"/{skill_token}/SKILL.md"

    triggered = False
    first_skill_seen = None
    start = time.time()
    buffer = ""
    pending = None
    accum = ""
    timed_out = True

    def scan(line: str):
        nonlocal pending, accum, first_skill_seen
        line = line.strip()
        if not line:
            return None
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            return None

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
                    needle = skill_needle if pending == "Skill" else read_needle
                    if needle in accum:
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
                if name == "Skill" and skill_needle in inp.get("skill", ""):
                    return {"triggered": True, "first_skill": inp.get("skill")}
                if name == "Read" and read_needle in inp.get("file_path", ""):
                    return {"triggered": True, "first_skill": inp.get("file_path")}
        elif event.get("type") == "result":
            return {"triggered": triggered, "first_skill": first_skill_seen}
        return None

    try:
        while time.time() - start < timeout:
            exited = process.poll() is not None
            if exited:
                rest = process.stdout.read()
                if rest:
                    buffer += rest.decode("utf-8", errors="replace")
            else:
                ready, _, _ = select.select([process.stdout], [], [], 1.0)
                if not ready:
                    continue
                chunk = os.read(process.stdout.fileno(), 8192)
                if not chunk:
                    exited = True
                else:
                    buffer += chunk.decode("utf-8", errors="replace")

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                result = scan(line)
                if result is not None:
                    return result

            # On process exit the last event can arrive without a trailing
            # newline; scan the leftover so a trigger there is not dropped.
            if exited:
                if buffer:
                    result = scan(buffer)
                    if result is not None:
                        return result
                timed_out = False
                break
    finally:
        _terminate(process)
    return {"triggered": triggered, "first_skill": first_skill_seen, "timed_out": timed_out}


def runs_for(query, should_trigger, runs, timeout, model, skill_token, plugin):
    triggers = 0
    timeouts = 0
    samples = []
    for _ in range(runs):
        r = run_query(query, timeout, model, skill_token, plugin)
        if r["triggered"]:
            triggers += 1
        if r.get("timed_out"):
            timeouts += 1
        samples.append(r.get("first_skill"))
    rate = triggers / runs
    # Surface samples to stderr only when the per-query outcome disagrees with
    # `should_trigger`, so debugging info is available without baking
    # environment-specific tool inputs (absolute paths, etc.) into the
    # persisted result that the README diffs for regression checks.
    if (rate >= 0.5) != should_trigger:
        for s in samples:
            print(f"    sample: {s}", file=sys.stderr)
    # A timeout counts as a non-trigger, so warn (stderr only, not persisted) to
    # keep a slow should-trigger run from silently reading as a real failure.
    if timeouts:
        print(f"    warning: {timeouts}/{runs} run(s) timed out (counted as non-trigger): {query[:80]}", file=sys.stderr)
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


def resolve_plugin(args) -> str:
    if args.plugin:
        return args.plugin
    # skills/<skill>/evals/<file> sits three levels below the plugin root, whose
    # directory name is the token that qualifies a Skill invocation.
    return Path(args.eval_set).resolve().parents[3].name


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval-set", required=True)
    parser.add_argument("--skill", help="Target skill token; inferred from --eval-set path when omitted.")
    parser.add_argument("--plugin", help="Plugin token qualifying a Skill invocation; inferred from --eval-set path when omitted.")
    parser.add_argument("--runs-per-query", type=int, default=3)
    # Each worker holds one ~1GB `claude -p` Node process open at a time; cap the
    # default low so a full run fits in memory on a typical machine.
    parser.add_argument("--num-workers", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--model", default="claude-sonnet-5")
    args = parser.parse_args()

    skill_token = resolve_skill_token(args)
    plugin = resolve_plugin(args)
    eval_set = json.loads(Path(args.eval_set).read_text())
    results = [None] * len(eval_set)
    with ProcessPoolExecutor(max_workers=args.num_workers) as pool:
        futures = {
            pool.submit(runs_for, e["query"], e["should_trigger"], args.runs_per_query, args.timeout, args.model, skill_token, plugin): i
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
