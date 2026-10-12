#!/usr/bin/env python3
# Reads hook JSON on stdin, emits one bw.session OTLP log record when a session
# starts, so every session produces at least one record that carries the
# signed-in user even if no other hook fires. Never fails the session: every
# error path exits 0.
import json
import os
import sys

from emit import emit, flush_warning  # sibling module; script dir is on sys.path[0]


def _build_session_attrs(h):
    """Reduce one SessionStart hook dict to the bw.session attrs.

    user.email is not set here; emit() adds it to every record.
    """
    return {
        "event.name": "bw.session",
        "bw.hook": h.get("hook_event_name", ""),
        "session.id": h.get("session_id", ""),
        "repo": os.path.basename(h.get("cwd") or ""),
    }


def main():
    try:
        h = json.load(sys.stdin)
    except Exception:
        return
    if not isinstance(h, dict):
        return
    emit("bw.session", _build_session_attrs(h))


if __name__ == "__main__":
    main()
    flush_warning()
    sys.exit(0)
