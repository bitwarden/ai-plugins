#!/usr/bin/env python3
"""PreToolUse hook: confine localhost-web-health-checker's Bash and Skill use.

The agent holds unscoped `Bash` and reads an untrusted test plan, and a plugin
agent cannot declare its own hooks. Only its own skill's scripts, the
`playwright-cli` calls render verification makes, and those two skills may run.
Any other call is blocked.

A command must be a single simple command: a character gate rejects every shell
metacharacter before the command is split into words and checked against one of
the allowed forms below.

A block exits 2, which Claude Code applies before permission rules are
evaluated. Every other agent, and the main session, passes through (exit 0).

The caller is matched on the first and last `:`-separated segments of its
`agent_type`.
"""
import json
import os
import re
import sys

PLUGIN_NAME = "bitwarden-testing-tools"
AGENT_NAME = "localhost-web-health-checker"
HEALTH_SKILL = "bitwarden-testing-tools:checking-localhost-web-health"
ALLOWED_SKILLS = (HEALTH_SKILL, "playwright-cli")
SCRIPTS_DIR = "skills/checking-localhost-web-health/scripts"
# Mirrors the names health-check.sh accepts.
SERVICE_NAMES = frozenset(
    {"Api", "Identity", "Billing", "billing-pricing", "Web", "Admin", "Notifications", "Events", "Icons"}
)
URLS = frozenset({"https://localhost:8080", "http://localhost:62911"})

COMMAND_CHARS = re.compile(r"[A-Za-z0-9_./:=,' -]+")
ROOT_CHARS = re.compile(r"[A-Za-z0-9_./:=,-]+")
TIMEOUT_ENV = re.compile(r"HEALTH_CHECK_TIMEOUT=[0-9]{1,5}")
FLAG = re.compile(r"[a-z0-9][a-z0-9.-]*=(on|off)")
SCREENSHOT = re.compile(
    r"--filename=(/(?:[A-Za-z0-9_.-]+/)*screenshots/render-verify-[0-9]{8}-[0-9]{4}\.png)"
)

SKILL_BLOCK = (
    "Only the checking-localhost-web-health and playwright-cli skills may be invoked in "
    "this agent (bitwarden-testing-tools policy). Report this step as an obstacle."
)
BASH_BLOCK = (
    "This command is not allowed in this agent (bitwarden-testing-tools policy). Allowed: "
    "the checking-localhost-web-health scripts, and playwright-cli open|goto "
    "<https://localhost:8080|http://localhost:62911>, screenshot, and close. Report this "
    "step as an obstacle."
)


def is_health_checker(agent_type):
    if not isinstance(agent_type, str):
        return False
    segments = agent_type.split(":")
    return len(segments) >= 2 and segments[0] == PLUGIN_NAME and segments[-1] == AGENT_NAME


def is_allowed_skill(skill):
    """True only for an exact allowed name, ignoring outer spaces and one leading '/'."""
    if not isinstance(skill, str):
        return False
    name = skill.strip()
    if name.startswith("/"):
        name = name[1:]
    return name in ALLOWED_SKILLS


def unquote_flag(token):
    if len(token) >= 2 and token[0] == "'" and token[-1] == "'":
        return token[1:-1]
    return token


def is_allowed_script_call(words, scripts):
    """words[0] is a script path; check its arguments."""
    script = words[0]
    args = words[1:]
    if script == scripts + "/preflight-check.sh":
        return not args
    if script == scripts + "/health-check.sh":
        return bool(args) and all(a in SERVICE_NAMES for a in args)
    if script == scripts + "/check_feature_flags.py":
        return (
            len(args) >= 2
            and args[0] == "--"
            and all(FLAG.fullmatch(unquote_flag(a)) for a in args[1:])
        )
    return False


def is_allowed_playwright_call(words):
    sub = words[1] if len(words) > 1 else None
    if sub in ("open", "goto"):
        return len(words) == 3 and words[2] in URLS
    if sub == "screenshot":
        if len(words) != 4 or words[3] != "--full-page":
            return False
        match = SCREENSHOT.fullmatch(words[2])
        return bool(match) and ".." not in match.group(1).split("/")
    if sub == "close":
        return len(words) == 2
    return False


def is_allowed_command(command, root):
    if not isinstance(command, str) or not COMMAND_CHARS.fullmatch(command.strip(" ")):
        return False
    words = command.split()
    if TIMEOUT_ENV.fullmatch(words[0]):
        words = words[1:]
        if not words or not words[0].endswith("/health-check.sh"):
            return False
    if words[0] == "playwright-cli":
        return is_allowed_playwright_call(words)
    if not isinstance(root, str) or not ROOT_CHARS.fullmatch(root):
        return False
    return is_allowed_script_call(words, root.rstrip("/") + "/" + SCRIPTS_DIR)


def decide(payload, env):
    """Return (exit code, stderr message) for one hook invocation."""
    if not is_health_checker(payload.get("agent_type")):
        return 0, ""
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        tool_input = {}
    tool = payload.get("tool_name")
    if tool == "Skill" and not is_allowed_skill(tool_input.get("skill")):
        return 2, SKILL_BLOCK
    if tool == "Bash" and not is_allowed_command(tool_input.get("command"), env.get("CLAUDE_PLUGIN_ROOT")):
        return 2, BASH_BLOCK
    return 0, ""


def main(stdin, env):
    try:
        payload = json.loads(stdin)
    except ValueError:
        return 0
    except RecursionError:
        # No Bash or Skill input is nested this deeply. Block if it could come
        # from the health checker rather than let the crash exit 1 and fail open.
        if PLUGIN_NAME in stdin and AGENT_NAME in stdin:
            print(BASH_BLOCK, file=sys.stderr)
            return 2
        return 0
    if not isinstance(payload, dict):
        return 0
    try:
        code, message = decide(payload, env)
    except Exception:
        # Fail closed for the agent this hook exists to restrict.
        if not is_health_checker(payload.get("agent_type")):
            return 0
        code, message = 2, BASH_BLOCK
    if code == 2:
        print(message, file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.stdin.buffer.read().decode("utf-8", "replace"), os.environ))
