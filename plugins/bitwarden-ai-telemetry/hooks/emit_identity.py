#!/usr/bin/env python3
# Reads hook JSON on stdin, emits one bw.identity OTLP log record recovering the
# skill/agent identity that native telemetry redacts. Never fails the session:
# every error path exits 0.
import json
import os
import sys

from emit import emit  # sibling module; script dir is on sys.path[0]


def _build_identity_attrs(h):
    """Reduce one hook-invocation dict to the bw.identity attrs.

    agent_type prefers the top-level `agent_type` (set on SubagentStop) over
    `tool_input.subagent_type` (set on a Task|Agent PostToolUse dispatch) —
    the two hooks fire for different event shapes, never both populated at
    once in practice, but SubagentStop's is the more authoritative of the two
    when both exist. skill comes from tool_input.skill (a Skill dispatch).
    """
    tin = h.get("tool_input") or {}
    return {
        "event.name": "bw.identity",
        "bw.hook": h.get("hook_event_name", ""),
        "bw.agent_type": h.get("agent_type") or tin.get("subagent_type") or "",
        "bw.skill": tin.get("skill") or "",
        "bw.tool": h.get("tool_name", ""),
        "session.id": h.get("session_id", ""),
        "repo": os.path.basename(h.get("cwd") or ""),
    }


def main():
    try:
        h = json.load(sys.stdin)
    except Exception:
        return
    emit("bw.identity", _build_identity_attrs(h))


if __name__ == "__main__":
    main()
    sys.exit(0)
