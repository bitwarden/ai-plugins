#!/usr/bin/env python3
"""Trigger-rate evaluator that checks for the real plugin-registered skill.

The skill-creator harness registers a temp copy named
`stacking-pull-requests-skill-<uuid>` and only counts invocations of that name
as triggers. When the real `bitwarden-delivery-tools:stacking-pull-requests`
skill is already installed in the environment running the eval, the model
invokes the real one and the harness records a false negative.

This script runs `claude -p` for each eval query and counts a "trigger" when
any Skill or Read tool call references the real skill token, anywhere in the
response. The scan continues past unrelated Skill invocations (some accounts
auto-fire session-init skills before the model selects a task skill), so the
eval is portable across environments rather than tied to any specific set of
installed plugins.

Triggering is read from the streamed `tool_use` block, which the model emits
before any tool runs, so nothing has to be allowed to run for the measurement to
work. The query set is imperative ("rebase my branch onto main and force push"),
so each subprocess is confined three ways: the built-in mutating tools are denied,
MCP servers are switched off entirely, and the working directory is a fresh temp
directory rather than the caller's checkout.

MCP needs the separate switch because a server starts at session init, before any
tool-permission check, so `--disallowedTools` cannot stop one from running. This
repo ships a server that launches through `bash -c` and holds a write-scoped
token; 60 unattended subprocesses must not reach it.
"""

import argparse
import json
import os
import select
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

TARGET_SKILL_TOKEN = "stacking-pull-requests"

# Deny takes precedence over any allow rule in the caller's settings. Skill and
# Read stay available because they are what the eval measures.
DENIED_TOOLS = ["Bash", "Edit", "Write", "NotebookEdit"]

# --disallowedTools cannot cover MCP: servers launch at session init, ahead of any
# permission check. --strict-mcp-config plus an empty config means none is loaded.
NO_MCP = ["--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}']


def _handle_event(event, state):
    """Fold one stream event into `state`.

    Returns a result dict once the outcome is settled — the target skill was
    seen, or the run reached its terminal `result` event — and None otherwise.
    """
    if event.get("type") == "stream_event":
        se = event.get("event", {})
        if se.get("type") == "content_block_start":
            cb = se.get("content_block", {})
            if cb.get("type") == "tool_use" and cb.get("name") in ("Skill", "Read"):
                state["pending"] = cb.get("name")
                state["accum"] = ""
            # Other tool types are ignored — we only care whether the
            # target skill is invoked at some point in the response.
        elif se.get("type") == "content_block_delta" and state["pending"]:
            delta = se.get("delta", {})
            if delta.get("type") == "input_json_delta":
                state["accum"] += delta.get("partial_json", "")
                if TARGET_SKILL_TOKEN in state["accum"]:
                    return {"triggered": True, "first_skill": state["accum"]}
        elif se.get("type") == "content_block_stop" and state["pending"]:
            if state["first_skill"] is None:
                state["first_skill"] = state["accum"]
            # Keep scanning past unrelated Skill/Read invocations so
            # the eval is portable across accounts that auto-fire
            # session-init or workflow skills before the task skill.
            state["pending"] = None
            state["accum"] = ""
    elif event.get("type") == "assistant":
        msg = event.get("message", {})
        for item in msg.get("content", []):
            if item.get("type") != "tool_use":
                continue
            name = item.get("name")
            inp = item.get("input", {})
            if name == "Skill" and TARGET_SKILL_TOKEN in inp.get("skill", ""):
                return {"triggered": True, "first_skill": inp.get("skill")}
            if name == "Read" and TARGET_SKILL_TOKEN in inp.get("file_path", ""):
                return {"triggered": True, "first_skill": inp.get("file_path")}
    elif event.get("type") == "result":
        # `subtype` reads "success" even for a failed run, so `is_error` is the
        # only field that separates a real non-trigger from a broken one.
        return {"triggered": False, "first_skill": state["first_skill"],
                "is_error": bool(event.get("is_error"))}
    return None


def _drain(buffer, state):
    """Parse every complete line out of `buffer`, returning `(leftover, result)`.

    Called both inside the read loop and once on whatever is left after the
    child exits, so a run that finishes between polls is still parsed rather
    than scored as a non-trigger on unread output.
    """
    while "\n" in buffer:
        line, buffer = buffer.split("\n", 1)
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        result = _handle_event(event, state)
        if result is not None:
            return buffer, result
    return buffer, None


def run_query(query: str, timeout: int, model: str, plugin_dirs=()) -> dict:
    cmd = [
        "claude",
        "-p", query,
        "--output-format", "stream-json",
        "--verbose",
        "--include-partial-messages",
        "--model", model,
        "--disallowedTools", *DENIED_TOOLS,
        *NO_MCP,
    ]
    for d in plugin_dirs:
        cmd += ["--plugin-dir", d]
    # Allowlist rather than "everything minus CLAUDECODE": the caller's environment
    # carries write-scoped tokens for other services, and 60 unattended children
    # have no use for them.
    keep = ("PATH", "HOME", "USER", "LANG", "LC_ALL", "TERM", "TMPDIR", "SHELL")
    env = {k: v for k, v in os.environ.items()
           if k in keep or k.startswith(("ANTHROPIC_", "CLAUDE_")) }
    env.pop("CLAUDECODE", None)

    workdir = None
    stderr_file = None
    process = None
    try:
        workdir = tempfile.mkdtemp(prefix="stack-eval-")
        stderr_file = tempfile.TemporaryFile()
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=stderr_file,
            env=env,
            cwd=workdir,
        )
    except OSError as e:
        # Spawn failed, so there is nothing to wait on or read. Clean up here:
        # the loop's own finally below never runs.
        if stderr_file is not None:
            stderr_file.close()
        if workdir is not None:
            shutil.rmtree(workdir, ignore_errors=True)
        return {"outcome": "errored", "triggered": False, "first_skill": None,
                "error": f"could not start claude: {e}"}

    state = {"pending": None, "accum": "", "first_skill": None}
    outcome = None
    timed_out = False
    buffer = ""
    start = time.time()

    try:
        while True:
            if time.time() - start >= timeout:
                timed_out = True
                break
            if process.poll() is not None:
                rest = process.stdout.read()
                if rest:
                    buffer += rest.decode("utf-8", errors="replace")
                buffer, outcome = _drain(buffer, state)
                break
            ready, _, _ = select.select([process.stdout], [], [], 1.0)
            if not ready:
                continue
            chunk = os.read(process.stdout.fileno(), 8192)
            if not chunk:
                buffer, outcome = _drain(buffer, state)
                break
            buffer += chunk.decode("utf-8", errors="replace")
            buffer, outcome = _drain(buffer, state)
            if outcome is not None:
                break
    finally:
        if process.poll() is None:
            if outcome is None and not timed_out:
                # No verdict of our own, so the exit status is about to be the
                # only evidence of why. Wait for it rather than killing and
                # reading back our own SIGKILL.
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
            else:
                process.kill()
        process.wait()
        stderr_file.seek(0)
        stderr_tail = stderr_file.read().decode("utf-8", errors="replace")[-500:].strip()
        stderr_file.close()
        shutil.rmtree(workdir, ignore_errors=True)

    def errored(reason):
        return {"outcome": "errored", "triggered": False, "first_skill": None, "error": reason}

    # The stream decides the verdict, and the exit status only explains a run
    # that produced none. Either verdict ends the read loop with the child still
    # winding down, so consulting its status here would score a finished run as
    # an error whenever it took longer than the grace wait to reap.
    if outcome is not None:
        if outcome["triggered"]:
            return {"outcome": "triggered", "triggered": True, "first_skill": outcome["first_skill"]}
        if outcome.get("is_error"):
            return errored(f"claude reported an error result: {stderr_tail or 'no stderr'}")
        return {"outcome": "not_triggered", "triggered": False, "first_skill": outcome["first_skill"]}
    if timed_out:
        return errored(f"timed out after {timeout}s")
    if process.returncode != 0:
        return errored(f"exit {process.returncode}: {stderr_tail or 'no stderr'}")
    return errored(f"stream ended with no result event: {stderr_tail or 'no stderr'}")


def runs_for(query, should_trigger, runs, timeout, model, plugin_dirs=()):
    triggers = 0
    errors = 0
    samples = []
    for _ in range(runs):
        r = run_query(query, timeout, model, plugin_dirs)
        if r["outcome"] == "errored":
            errors += 1
            samples.append(f"ERROR: {r['error']}")
            continue
        if r["triggered"]:
            triggers += 1
        samples.append(r.get("first_skill"))
    scored = runs - errors
    # An errored run is not evidence in either direction, so it leaves the
    # denominator rather than counting as a non-trigger.
    rate = triggers / scored if scored else None
    # Surface samples to stderr only when the per-query outcome disagrees with
    # `should_trigger`, so debugging info is available without baking
    # environment-specific tool inputs (absolute paths, etc.) into the
    # persisted result that the README diffs for regression checks.
    if rate is None or (rate >= 0.5) != should_trigger:
        for s in samples:
            print(f"    sample: {s}", file=sys.stderr)
    return {
        "query": query,
        "should_trigger": should_trigger,
        "triggers": triggers,
        "runs": runs,
        "errors": errors,
        "trigger_rate": rate,
    }


def _plugin_identity(d):
    """`<name>@<version>` from a plugin directory, falling back to its path.

    The basename alone is identical for a branch checkout and the installed cache,
    so a run against the wrong one would produce an empty regression diff — the
    exact mix-up `--plugin-dir` is required to prevent.
    """
    manifest = Path(d).resolve() / ".claude-plugin" / "plugin.json"
    try:
        m = json.loads(manifest.read_text())
        return f"{m['name']}@{m['version']}"
    except (OSError, ValueError, KeyError):
        return str(Path(d).resolve())


def main():
    if shutil.which("claude") is None:
        print("claude is not on PATH — see evals/README.md", file=sys.stderr)
        return 1

    parser = argparse.ArgumentParser()
    parser.add_argument("--eval-set", required=True)
    parser.add_argument("--runs-per-query", type=int, default=3)
    parser.add_argument("--num-workers", type=int, default=8)
    # Sized by the should-not-trigger cases: a trigger ends at the token, but a
    # non-trigger has to reach the terminal result event, and any timeout is an
    # error that fails the whole run.
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--model", default="claude-opus-5")
    # Repeatable, and required: every plugin whose skills compete for these
    # queries has to be loaded, or a near-miss scores as a pass against a skill
    # that was never there.
    parser.add_argument("--plugin-dir", action="append", required=True, dest="plugin_dirs")
    args = parser.parse_args()

    eval_set = json.loads(Path(args.eval_set).read_text())
    results = [None] * len(eval_set)
    with ProcessPoolExecutor(max_workers=args.num_workers) as pool:
        futures = {
            pool.submit(runs_for, e["query"], e["should_trigger"], args.runs_per_query, args.timeout, args.model, tuple(args.plugin_dirs)): i
            for i, e in enumerate(eval_set)
        }
        for fut in as_completed(futures):
            i = futures[fut]
            results[i] = fut.result()
            r = results[i]
            tag = "ERROR" if r["trigger_rate"] is None else ("PASS" if (r["trigger_rate"] >= 0.5) == r["should_trigger"] else "FAIL")
            print(f"  [{tag}] rate={r['triggers']}/{r['runs'] - r['errors']} errors={r['errors']} expected={r['should_trigger']}: {r['query'][:80]}", file=sys.stderr)

    scored_results = [r for r in results if r["trigger_rate"] is not None]
    triggers_pass = sum(1 for r in scored_results if r["should_trigger"] and r["trigger_rate"] >= 0.5)
    triggers_total = sum(1 for r in scored_results if r["should_trigger"])
    no_trigger_pass = sum(1 for r in scored_results if not r["should_trigger"] and r["trigger_rate"] < 0.5)
    no_trigger_total = sum(1 for r in scored_results if not r["should_trigger"])
    total_errors = sum(r["errors"] for r in results)

    # Run-invariant only — a timestamp here would make every regression diff
    # non-empty. A model or plugin-set change SHOULD fail the diff: the run it
    # produced is not comparable to the baseline.
    summary = {
        "model": args.model,
        "plugin_dirs": sorted(_plugin_identity(d) for d in args.plugin_dirs),
        "runs_per_query": args.runs_per_query,
        "errors": total_errors,
        "should_trigger_pass_rate": triggers_pass / triggers_total if triggers_total else None,
        "should_not_trigger_pass_rate": no_trigger_pass / no_trigger_total if no_trigger_total else None,
        "should_trigger_pass": f"{triggers_pass}/{triggers_total}",
        "should_not_trigger_pass": f"{no_trigger_pass}/{no_trigger_total}",
        "results": results,
    }
    print(json.dumps(summary, indent=2, default=str))

    # A broken harness scores every should-trigger query at zero, which reads as
    # a routing regression. Fail loudly rather than emit a summary that reads like a score.
    if total_errors:
        print(f"\n{total_errors} run(s) errored — these scores are not comparable to a baseline.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
