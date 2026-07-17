#!/usr/bin/env python3
"""Reusable trigger-rate eval runner for Bitwarden skills.

A trigger eval asks one narrow question about a skill's description /
when_to_use text: does the model reach for the skill on the real phrasings
it is meant to catch, and does it stay silent on near-misses? This runner
answers that question reproducibly, in two modes, without the caller having
to hand-roll a `claude -p` harness.

Two modes exist because a skill can be evaluated at two different points in
its life:

  installed
    The skill is already registered in the environment running the eval
    (its plugin is installed). The harness cannot inject a temp copy, so it
    watches the real skill token. This is a direct, parameterized port of
    `bitwarden-delivery-tools/.../creating-pull-request/evals/run_real_eval.py`.

  isolated
    The skill is still in development or lives on an unmerged PR, so it is
    not registered. The harness writes a throwaway slash-command file into
    `<project_root>/.claude/commands/` carrying the skill's real description
    in YAML frontmatter, so the model sees the description in its available
    surface, then watches for that temp token. The temp file is always
    cleaned up. This mechanism is ported from skill-creator's `run_eval.py`.
    Concurrent workers testing the same skill would otherwise write several
    byte-identical-description clones into that shared directory at once,
    which the model cannot reliably tell apart, producing false negatives
    unrelated to the skill's actual description. An flock scoped to the
    skill's name serializes the write/run/cleanup critical section per
    skill, so only one clone of a given skill exists at any instant no
    matter how many `--num-workers` are testing it; concurrent isolated
    evals of *different* skills are not serialized against each other.

Both modes share one deliberate behavior: they scan **tolerantly** past
unrelated `Skill` / `Read` tool_use calls rather than giving up on the first
one. Some accounts auto-fire session-init or workflow skills before the model
selects a task skill; a stricter scanner would record those as false
negatives. This tolerance is the entire reason this runner exists instead of
skill-creator's stricter harness, and it is applied identically in both modes
so repeated-run reliability semantics match across them.

Output is a single JSON summary on stdout. Diagnostic lines (balance
warnings, per-case PASS/FAIL, regression detail) go to stderr, so stdout
stays a clean, diffable artifact.
"""

import argparse
import fcntl
import json
import os
import select
import subprocess
import sys
import time
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

# Blended pass/fail threshold, kept identical to the field semantics of the
# existing creating-pull-request baseline.json for continuity.
TRIGGER_THRESHOLD = 0.5


# ---------------------------------------------------------------------------
# SKILL.md parsing (local implementation; not imported from skill-creator,
# which is a separately maintained external plugin).
# ---------------------------------------------------------------------------

def parse_skill_md(skill_path: Path) -> tuple[str, str, str]:
    """Parse a SKILL.md file, returning (name, description, full_content).

    Handles both single-line descriptions and YAML block scalars
    (``>``, ``|``, ``>-``, ``|-``) folded into a single string.
    """
    content = (skill_path / "SKILL.md").read_text()
    lines = content.split("\n")

    if lines[0].strip() != "---":
        raise ValueError(f"{skill_path}/SKILL.md missing frontmatter (no opening ---)")

    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        raise ValueError(f"{skill_path}/SKILL.md missing frontmatter (no closing ---)")

    name = ""
    description = ""
    frontmatter_lines = lines[1:end_idx]
    i = 0
    while i < len(frontmatter_lines):
        line = frontmatter_lines[i]
        if line.startswith("name:"):
            name = line[len("name:"):].strip().strip('"').strip("'")
        elif line.startswith("description:"):
            value = line[len("description:"):].strip()
            if value in (">", "|", ">-", "|-"):
                continuation: list[str] = []
                i += 1
                while i < len(frontmatter_lines) and (
                    frontmatter_lines[i].startswith("  ")
                    or frontmatter_lines[i].startswith("\t")
                ):
                    continuation.append(frontmatter_lines[i].strip())
                    i += 1
                description = " ".join(continuation)
                continue
            description = value.strip('"').strip("'")
        i += 1

    if not name:
        raise ValueError(f"{skill_path}/SKILL.md frontmatter missing 'name:' field")
    return name, description, content


def find_project_root(start: Path | None = None) -> Path:
    """Walk up from ``start`` (default cwd) looking for a ``.claude/`` dir.

    Mimics how Claude Code discovers its project root, so a temp command file
    we create ends up where ``claude -p`` will look for it.
    """
    current = start or Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".claude").is_dir():
            return parent
    return current


# ---------------------------------------------------------------------------
# Shared stream scanner.
# ---------------------------------------------------------------------------

def _scan_process(
    process: subprocess.Popen,
    target_token: str,
    exclude_skills: list[str],
    timeout: int,
) -> dict:
    """Scan a `claude -p` stream for the target token, tolerantly.

    Returns ``{"triggered", "first_skill", "sibling_fires"}``. ``sibling_fires``
    maps each excluded token to whether it fired in this single run. The scan
    keeps going past unrelated ``Skill`` / ``Read`` calls (the tolerance that
    makes this eval portable across accounts) and returns as soon as the
    target token is seen, for speed, carrying any sibling fires observed up to
    that point.
    """
    triggered = False
    first_skill_seen: str | None = None
    sibling_fires: dict[str, bool] = {tok: False for tok in exclude_skills}
    start = time.time()
    buffer = ""
    pending: str | None = None
    accum = ""

    def note_siblings(text: str) -> None:
        for tok in exclude_skills:
            if tok in text:
                sibling_fires[tok] = True

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
                    se_type = se.get("type")
                    if se_type == "content_block_start":
                        cb = se.get("content_block", {})
                        if cb.get("type") == "tool_use" and cb.get("name") in ("Skill", "Read"):
                            pending = cb.get("name")
                            accum = ""
                        # Other tool types are ignored; we only care whether
                        # the target skill is invoked at some point.
                    elif se_type == "content_block_delta" and pending:
                        delta = se.get("delta", {})
                        if delta.get("type") == "input_json_delta":
                            accum += delta.get("partial_json", "")
                            note_siblings(accum)
                            if target_token in accum:
                                return {
                                    "triggered": True,
                                    "first_skill": accum,
                                    "sibling_fires": sibling_fires,
                                }
                    elif se_type == "content_block_stop" and pending:
                        if first_skill_seen is None:
                            first_skill_seen = accum
                        note_siblings(accum)
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
                        ref = ""
                        if name == "Skill":
                            ref = inp.get("skill", "")
                        elif name == "Read":
                            ref = inp.get("file_path", "")
                        if not ref:
                            continue
                        if first_skill_seen is None:
                            first_skill_seen = ref
                        note_siblings(ref)
                        if target_token in ref:
                            return {
                                "triggered": True,
                                "first_skill": ref,
                                "sibling_fires": sibling_fires,
                            }
                elif event.get("type") == "result":
                    return {
                        "triggered": triggered,
                        "first_skill": first_skill_seen,
                        "sibling_fires": sibling_fires,
                    }
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()

    return {
        "triggered": triggered,
        "first_skill": first_skill_seen,
        "sibling_fires": sibling_fires,
    }


def _base_env() -> dict:
    """Environment for the subprocess, minus CLAUDECODE.

    The CLAUDECODE guard is for interactive terminal conflicts; nesting a
    programmatic `claude -p` subprocess inside a Claude Code session is safe.
    """
    return {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}


# ---------------------------------------------------------------------------
# Installed mode.
# ---------------------------------------------------------------------------

def run_query_installed(
    query: str,
    skill_token: str,
    exclude_skills: list[str],
    timeout: int,
    model: str,
) -> dict:
    """Run one query and detect the already-registered skill token.

    Parameterized port of run_real_eval.py::run_query.
    """
    cmd = [
        "claude",
        "-p", query,
        "--output-format", "stream-json",
        "--verbose",
        "--include-partial-messages",
        "--model", model,
    ]
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        env=_base_env(),
    )
    return _scan_process(process, skill_token, exclude_skills, timeout)


# ---------------------------------------------------------------------------
# Isolated mode.
# ---------------------------------------------------------------------------

def run_query_isolated(
    query: str,
    skill_name: str,
    description: str,
    exclude_skills: list[str],
    project_root: Path,
    timeout: int,
    model: str,
) -> dict:
    """Run one query against a temp command file carrying the skill description.

    Generates a fresh uuid per individual call (not per query) so parallel
    repeated runs never collide on the same temp filename. Scans tolerantly,
    exactly like installed mode (a deliberate divergence from skill-creator's
    stricter first-tool-use gate), then always cleans up the temp file.

    Holds an flock scoped to ``skill_name`` across the write/run/cleanup
    critical section, so only one clone of this skill exists in the shared
    commands directory at a time. Without it, concurrent workers testing the
    same skill write several byte-identical-description clones at once, and
    the model has no way to tell them apart, producing false negatives
    unrelated to the skill's actual description.
    """
    unique_id = uuid.uuid4().hex[:8]
    clean_name = f"{skill_name}-skill-{unique_id}"
    commands_dir = Path(project_root) / ".claude" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)
    command_file = commands_dir / f"{clean_name}.md"
    lock_file = commands_dir / f".trigger_eval_isolated_{skill_name}.lock"

    lock_fd = open(lock_file, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        try:
            # YAML block scalar avoids breaking on quotes/colons in the description.
            indented_desc = "\n  ".join(description.split("\n"))
            command_file.write_text(
                "---\n"
                "description: |\n"
                f"  {indented_desc}\n"
                "---\n\n"
                f"# {skill_name}\n\n"
                f"This skill handles: {description}\n"
            )

            cmd = [
                "claude",
                "-p", query,
                "--output-format", "stream-json",
                "--verbose",
                "--include-partial-messages",
                "--model", model,
            ]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                cwd=str(project_root),
                env=_base_env(),
            )
            return _scan_process(process, clean_name, exclude_skills, timeout)
        finally:
            command_file.unlink(missing_ok=True)
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()


# ---------------------------------------------------------------------------
# Repeated-run aggregation.
# ---------------------------------------------------------------------------

def runs_for_query(
    mode: str,
    query: str,
    should_trigger: bool,
    ctx: dict,
    runs: int,
    timeout: int,
    model: str,
    exclude_skills: list[str],
) -> dict:
    """Run one query ``runs`` times and aggregate.

    ``ctx`` carries mode-specific parameters:
      installed -> {"skill_token": str}
      isolated  -> {"skill_name": str, "description": str, "project_root": Path}
    """
    triggers = 0
    samples: list[str | None] = []
    sibling_totals: dict[str, int] = {tok: 0 for tok in exclude_skills}

    for _ in range(runs):
        if mode == "installed":
            r = run_query_installed(
                query, ctx["skill_token"], exclude_skills, timeout, model
            )
        else:
            r = run_query_isolated(
                query,
                ctx["skill_name"],
                ctx["description"],
                exclude_skills,
                ctx["project_root"],
                timeout,
                model,
            )
        if r["triggered"]:
            triggers += 1
        samples.append(r.get("first_skill"))
        for tok, fired in r.get("sibling_fires", {}).items():
            if fired:
                sibling_totals[tok] += 1

    rate = triggers / runs
    # pass^k-style reliability: every run agreed with the expectation.
    if should_trigger:
        all_runs_agree = triggers == runs
    else:
        all_runs_agree = triggers == 0

    # Surface samples to stderr only when the blended outcome disagrees with
    # the expectation, so debugging info is available without baking
    # environment-specific tool inputs into the persisted result.
    if (rate >= TRIGGER_THRESHOLD) != should_trigger:
        for s in samples:
            print(f"    sample: {s}", file=sys.stderr)

    result = {
        "query": query,
        "should_trigger": should_trigger,
        "triggers": triggers,
        "runs": runs,
        "trigger_rate": rate,
        "all_runs_agree": all_runs_agree,
    }
    if exclude_skills:
        result["sibling_fires"] = sibling_totals
    return result


# ---------------------------------------------------------------------------
# Balance / summary / regression.
# ---------------------------------------------------------------------------

def check_balance(eval_set: list[dict]) -> str | None:
    """Warn (never block) if the true/false split is off by more than ~20%.

    A lopsided set biases the blended pass rate toward whichever class
    dominates.
    """
    total = len(eval_set)
    if total == 0:
        return None
    true_count = sum(1 for e in eval_set if e.get("should_trigger"))
    true_frac = true_count / total
    if abs(true_frac - 0.5) > 0.20:
        msg = (
            f"eval-set balance is skewed: {true_count}/{total} should_trigger=true "
            f"({true_frac:.0%}). Aim for a roughly even true/false split so the "
            f"pass rate is not biased toward one class."
        )
        print(f"WARNING: {msg}", file=sys.stderr)
        return msg
    return None


def build_summary(
    mode: str,
    results: list[dict],
    skill_token: str | None,
    skill_name: str | None,
    runs_per_query: int,
    model: str,
    balance_warning: str | None,
) -> dict:
    """Assemble the report from per-case results."""
    trig_pass = sum(1 for r in results if r["should_trigger"] and r["trigger_rate"] >= TRIGGER_THRESHOLD)
    trig_total = sum(1 for r in results if r["should_trigger"])
    no_trig_pass = sum(1 for r in results if not r["should_trigger"] and r["trigger_rate"] < TRIGGER_THRESHOLD)
    no_trig_total = sum(1 for r in results if not r["should_trigger"])

    trig_reliable = sum(1 for r in results if r["should_trigger"] and r["all_runs_agree"])
    no_trig_reliable = sum(1 for r in results if not r["should_trigger"] and r["all_runs_agree"])
    total_reliable = sum(1 for r in results if r["all_runs_agree"])

    return {
        "mode": mode,
        "skill_token": skill_token,
        "skill_name": skill_name,
        "runs_per_query": runs_per_query,
        "model": model,
        "balance_warning": balance_warning,
        # Blended pass rates: same field names as the existing baseline.json.
        "should_trigger_pass_rate": trig_pass / trig_total if trig_total else None,
        "should_not_trigger_pass_rate": no_trig_pass / no_trig_total if no_trig_total else None,
        "should_trigger_pass": f"{trig_pass}/{trig_total}",
        "should_not_trigger_pass": f"{no_trig_pass}/{no_trig_total}",
        # Reliability: pass^k signal, every run agreeing with the expectation.
        "reliability": {
            "all_runs_agree_rate": total_reliable / len(results) if results else None,
            "should_trigger_reliable": f"{trig_reliable}/{trig_total}",
            "should_not_trigger_reliable": f"{no_trig_reliable}/{no_trig_total}",
        },
        "results": results,
    }


def check_regression(fresh_summary: dict, baseline: dict) -> dict:
    """Compare a fresh summary against a recorded baseline, matching by query.

    Matching by query string (not index) is robust to eval-set reordering.
    Two regression classes are flagged:
      - hard: baseline blended pass was True, fresh is False.
      - reliability: baseline all_runs_agree was True, fresh is False.
    """
    def blended_pass(case: dict) -> bool:
        return (case["trigger_rate"] >= TRIGGER_THRESHOLD) == case["should_trigger"]

    baseline_by_query = {c["query"]: c for c in baseline.get("results", [])}
    hard: list[dict] = []
    reliability: list[dict] = []

    for fresh in fresh_summary.get("results", []):
        base = baseline_by_query.get(fresh["query"])
        if base is None:
            continue
        if blended_pass(base) and not blended_pass(fresh):
            hard.append({
                "query": fresh["query"],
                "should_trigger": fresh["should_trigger"],
                "baseline_rate": base["trigger_rate"],
                "fresh_rate": fresh["trigger_rate"],
            })
        if base.get("all_runs_agree") and not fresh.get("all_runs_agree"):
            reliability.append({
                "query": fresh["query"],
                "should_trigger": fresh["should_trigger"],
                "baseline_triggers": f"{base['triggers']}/{base['runs']}",
                "fresh_triggers": f"{fresh['triggers']}/{fresh['runs']}",
            })

    return {"hard_regressions": hard, "reliability_regressions": reliability}


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Reusable trigger-rate eval runner for Bitwarden skills.",
    )
    parser.add_argument("--mode", choices=["installed", "isolated"], required=True)
    parser.add_argument("--eval-set", required=True,
                        help="Path to JSON array of {query, should_trigger} cases.")
    parser.add_argument("--skill-token", default=None,
                        help="Registered skill token to watch (installed mode).")
    parser.add_argument("--skill-path", default=None,
                        help="Path to the skill directory (required in isolated mode; "
                             "source for deriving --skill-token in installed mode).")
    parser.add_argument("--description", default=None,
                        help="Override the description baked into the temp command file "
                             "(isolated mode only).")
    parser.add_argument("--exclude-skill", action="append", default=[],
                        help="Sibling skill token to also watch for (report-only). "
                             "Repeatable.")
    parser.add_argument("--project-root", default=None,
                        help="Override find_project_root() (isolated mode only).")
    parser.add_argument("--runs-per-query", type=int, default=3)
    parser.add_argument("--num-workers", type=int, default=8)
    parser.add_argument("--timeout", type=int, default=45)
    parser.add_argument("--model", default="claude-opus-4-7")
    parser.add_argument("--baseline", default=None,
                        help="Path to a recorded baseline summary (required with "
                             "--check-regression).")
    parser.add_argument("--check-regression", action="store_true", default=False)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Cross-field validation.
    if args.mode == "installed" and not (args.skill_token or args.skill_path):
        parser.error("--mode installed requires --skill-token or --skill-path")
    if args.mode == "isolated" and not args.skill_path:
        parser.error("--mode isolated requires --skill-path")
    if args.check_regression and not args.baseline:
        parser.error("--check-regression requires --baseline")

    eval_set = json.loads(Path(args.eval_set).read_text())
    balance_warning = check_balance(eval_set)

    exclude_skills = list(args.exclude_skill)

    # Resolve mode-specific context.
    skill_token: str | None = None
    skill_name: str | None = None
    ctx: dict = {}

    if args.mode == "installed":
        if args.description:
            print("WARNING: --description is ignored in installed mode.", file=sys.stderr)
        if args.project_root:
            print("WARNING: --project-root is ignored in installed mode.", file=sys.stderr)
        skill_token = args.skill_token
        if not skill_token and args.skill_path:
            skill_name, _, _ = parse_skill_md(Path(args.skill_path))
            skill_token = skill_name
        ctx = {"skill_token": skill_token}
    else:  # isolated
        if args.skill_token:
            print("WARNING: --skill-token is ignored in isolated mode.", file=sys.stderr)
        skill_name, parsed_desc, _ = parse_skill_md(Path(args.skill_path))
        description = args.description or parsed_desc
        if args.project_root:
            project_root = Path(args.project_root)
        else:
            project_root = find_project_root()
        ctx = {
            "skill_name": skill_name,
            "description": description,
            "project_root": project_root,
        }

    # Fan out over (query, should_trigger) pairs.
    results: list[dict | None] = [None] * len(eval_set)
    with ProcessPoolExecutor(max_workers=args.num_workers) as pool:
        futures = {
            pool.submit(
                runs_for_query,
                args.mode,
                e["query"],
                e["should_trigger"],
                ctx,
                args.runs_per_query,
                args.timeout,
                args.model,
                exclude_skills,
            ): i
            for i, e in enumerate(eval_set)
        }
        for fut in as_completed(futures):
            i = futures[fut]
            r = fut.result()
            results[i] = r
            tag = "PASS" if (r["trigger_rate"] >= TRIGGER_THRESHOLD) == r["should_trigger"] else "FAIL"
            reliable = "reliable" if r["all_runs_agree"] else "FLAKY"
            print(
                f"  [{tag}/{reliable}] rate={r['triggers']}/{r['runs']} "
                f"expected={r['should_trigger']}: {r['query'][:80]}",
                file=sys.stderr,
            )

    summary = build_summary(
        mode=args.mode,
        results=[r for r in results if r is not None],
        skill_token=skill_token,
        skill_name=skill_name,
        runs_per_query=args.runs_per_query,
        model=args.model,
        balance_warning=balance_warning,
    )

    exit_code = 0
    if args.check_regression:
        baseline = json.loads(Path(args.baseline).read_text())
        regression = check_regression(summary, baseline)
        summary["regression"] = regression
        if regression["hard_regressions"] or regression["reliability_regressions"]:
            exit_code = 1
            print("REGRESSION DETECTED:", file=sys.stderr)
            for r in regression["hard_regressions"]:
                print(f"  hard: {r['query'][:80]} "
                      f"(baseline {r['baseline_rate']} -> fresh {r['fresh_rate']})",
                      file=sys.stderr)
            for r in regression["reliability_regressions"]:
                print(f"  reliability: {r['query'][:80]} "
                      f"(baseline {r['baseline_triggers']} -> fresh {r['fresh_triggers']})",
                      file=sys.stderr)

    print(json.dumps(summary, indent=2, default=str))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
