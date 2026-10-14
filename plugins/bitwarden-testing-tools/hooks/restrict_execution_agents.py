#!/usr/bin/env python3
"""PreToolUse hook: confine the execution agents' Bash, Skill, and Read use.

localhost-web-health-checker and playwright-test-runner hold unscoped `Bash`
and read untrusted input, and a plugin agent cannot declare its own hooks.
Each may run only the commands and skills it uses. Any other `Bash` or `Skill`
call is blocked, and so is a `Read` of a secrets file.

  localhost-web-health-checker  the three scripts of checking-localhost-web-health
  playwright-test-runner        a fixed set of playwright-cli subcommands, the two
                                scripts of running-playwright-tests, and the
                                Mailcatcher reader and Stripe wrapper of the
                                vendor plugins, matched by path shape

A command is split the way a shell would split it, but anything a shell would
expand or chain blocks it: a metacharacter outside quotes, or `$`, a backtick,
or a backslash inside double quotes. So one simple command is checked, and no
second command or substitution reaches the shell. The JavaScript passed to
`playwright-cli eval` and `run-code` is not inspected.

A block exits 2, which Claude Code applies before permission rules are
evaluated. Every other agent, and the main session, passes through (exit 0).

The caller is matched on the first and last `:`-separated segments of its
`agent_type`.
"""
# cspell:ignore dblclick keyup mousemove mousedown mouseup
import json
import os
import re
import sys

PLUGIN_NAME = "bitwarden-testing-tools"
CHECKER = "localhost-web-health-checker"
RUNNER = "playwright-test-runner"
# Each restricted agent, mapped to the plugin-qualified skills it may invoke.
# `playwright-cli` is a bare name, which is how it is installed.
AGENT_SKILLS = {
    CHECKER: ("bitwarden-testing-tools:checking-localhost-web-health",),
    RUNNER: (
        "bitwarden-testing-tools:running-playwright-tests",
        "playwright-cli",
        "bitwarden-mailcatcher-tools:reading-mailcatcher-api",
        "bitwarden-stripe-tools:using-stripe-cli",
    ),
}

HEALTH_SCRIPTS = "skills/checking-localhost-web-health/scripts"
RUNNER_SCRIPTS = "skills/running-playwright-tests/scripts"
RUNNER_CONFIG = "skills/running-playwright-tests/playwright.config.json"
# Mirrors the names health-check.sh accepts.
SERVICE_NAMES = frozenset(
    {"Api", "Identity", "Billing", "billing-pricing", "Web", "Admin", "Notifications", "Events", "Icons"}
)
FLAG = re.compile(r"[a-z0-9][a-z0-9.-]*=(on|off)")

# The vendor plugins' scripts the runner reaches through their skills. The hook
# cannot derive another plugin's root, so they are matched by path shape.
VENDOR_SCRIPTS = (
    re.compile(
        r"/(?:[^/]+/)*bitwarden-mailcatcher-tools/(?:[^/]+/)*"
        r"skills/reading-mailcatcher-api/scripts/read_mailcatcher\.py"
    ),
    re.compile(
        r"/(?:[^/]+/)*bitwarden-stripe-tools/(?:[^/]+/)*"
        r"skills/using-stripe-cli/scripts/stripe_cli\.py"
    ),
)

# Navigation stays on the two local web origins; the next character after the
# origin must start a path, query, or fragment, so `localhost:8080.evil` and
# `localhost:8080@evil` do not match.
LOCAL_URL = re.compile(r"(?:https://localhost:8080|http://localhost:62911)(?:[/?#]\S*)?")
SCREENSHOT_FILE = re.compile(r"--filename=/(?:[^/\n]+/)*screenshots/[^/\n]+\.png")
ELEMENT_REF = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_-]*")
# playwright-cli subcommands that take no argument.
NO_ARGUMENT_SUBCOMMANDS = frozenset(
    {"close", "snapshot", "reload", "go-back", "go-forward", "tab-list", "network", "dialog-dismiss"}
)
# Subcommands whose arguments are element refs, text, keys, numbers, or names.
# Writing or mocking subcommands (state-save, pdf, route, tracing, video,
# upload, delete-data, and the cookie and storage setters) are left out.
ARGUMENT_SUBCOMMANDS = frozenset(
    {
        "click", "dblclick", "fill", "type", "press", "hover", "select", "check", "uncheck", "drag",
        "dialog-accept", "resize", "keydown", "keyup", "mousemove", "mousedown", "mouseup",
        "mousewheel", "console", "tab-close", "tab-select", "cookie-list", "cookie-get",
        "localstorage-list", "localstorage-get", "sessionstorage-list", "sessionstorage-get",
    }
)

SKILL_BLOCK = (
    "Only the {skills} skill(s) may be invoked in this agent (bitwarden-testing-tools "
    "policy). If you invoked one under a different name, retry once as exactly that name; "
    "otherwise report this step as an obstacle."
)
BASH_BLOCK = {
    CHECKER: (
        "This command is not allowed in this agent (bitwarden-testing-tools policy). Allowed: "
        "the checking-localhost-web-health scripts, one simple command at a time. Quote a "
        "script path that has a space or any character beyond letters, digits, and _ . / : = , "
        "@ % + - and retry once; otherwise report this step as an obstacle."
    ),
    RUNNER: (
        "This command is not allowed in this agent (bitwarden-testing-tools policy). Allowed, "
        "one simple command at a time: playwright-cli subcommands, the running-playwright-tests "
        "scripts, and the scripts of the Mailcatcher and Stripe skills. Quote any argument with "
        "characters beyond letters, digits, and _ . / : = , @ % + - ; inside double quotes avoid "
        "$, backticks, and backslashes, or use single quotes. Retry once with a corrected "
        "command; otherwise report this step as an obstacle."
    ),
}
READ_BLOCK = (
    "Reading secrets files is not allowed in this agent (bitwarden-testing-tools policy). Use "
    "the skill's script for the one value you need, or report this step as an obstacle."
)
SECRET_FILE_NAMES = frozenset({"secrets.json"})


def restricted_agent(agent_type):
    """Return the restricted agent's name, or None if agent_type is not one."""
    if not isinstance(agent_type, str):
        return None
    segments = agent_type.split(":")
    if len(segments) >= 2 and segments[0] == PLUGIN_NAME and segments[-1] in AGENT_SKILLS:
        return segments[-1]
    return None


def is_allowed_skill(skill, agent):
    """True only for an exact allowed name, ignoring outer spaces and one leading '/'."""
    if not isinstance(skill, str):
        return False
    name = skill.strip()
    if name.startswith("/"):
        name = name[1:]
    return name in AGENT_SKILLS[agent]


def split_command(command):
    """Split one simple command into words, or return None if a shell would do more.

    Unquoted text is limited to characters a shell never expands. Single quotes
    are literal. Double quotes may not hold `$`, a backtick, or a backslash.
    """
    words, word, in_word, quote = [], [], False, None
    for char in command:
        if char == "\0":
            return None
        if quote == "'":
            if char == "'":
                quote = None
            else:
                word.append(char)
        elif quote == '"':
            if char == '"':
                quote = None
            elif char in "$`\\":
                return None
            else:
                word.append(char)
        elif char in " \t":
            if in_word:
                words.append("".join(word))
                word, in_word = [], False
        elif char in "'\"":
            quote, in_word = char, True
        elif re.fullmatch(r"[A-Za-z0-9_./:,@%+-]", char) or (char == "=" and in_word):
            word.append(char)
            in_word = True
        else:
            return None
    if quote is not None:
        return None
    if in_word:
        words.append("".join(word))
    return words or None


def plugin_path(root, relative):
    return root.rstrip("/") + "/" + relative


def is_health_script_call(words, root):
    scripts = plugin_path(root, HEALTH_SCRIPTS)
    script, args = words[0], words[1:]
    if script == scripts + "/preflight-check.sh":
        return not args
    if script == scripts + "/health-check.sh":
        return bool(args) and all(a in SERVICE_NAMES for a in args)
    if script == scripts + "/check_feature_flags.py":
        return len(args) >= 2 and args[0] == "--" and all(FLAG.fullmatch(a) for a in args[1:])
    return False


def is_screenshot_argument(arg):
    """`--full-page`, an element ref, or a --filename under a `screenshots/` directory."""
    if arg == "--full-page" or ELEMENT_REF.fullmatch(arg):
        return True
    return bool(SCREENSHOT_FILE.fullmatch(arg)) and ".." not in arg.split("/")


def is_allowed_playwright_call(words, root):
    sub, args = words[1] if len(words) > 1 else None, words[2:]
    if sub == "open":
        return bool(root) and words[2:] == ["--config=" + plugin_path(root, RUNNER_CONFIG)]
    if sub == "goto":
        return len(args) == 1 and bool(LOCAL_URL.fullmatch(args[0]))
    if sub == "tab-new":
        return len(args) <= 1 and all(LOCAL_URL.fullmatch(a) for a in args)
    if sub == "screenshot":
        return all(is_screenshot_argument(a) for a in args)
    if sub == "eval":
        return 1 <= len(args) <= 2
    if sub == "run-code":
        return len(args) == 1
    if sub in NO_ARGUMENT_SUBCOMMANDS:
        return not args
    return sub in ARGUMENT_SUBCOMMANDS


def is_vendor_script(path):
    return ".." not in path.split("/") and any(p.fullmatch(path) for p in VENDOR_SCRIPTS)


def is_runner_call(words, root):
    first = words[0]
    if first == "playwright-cli":
        return is_allowed_playwright_call(words, root)
    if bool(root) and first in (
        plugin_path(root, RUNNER_SCRIPTS + "/external_trigger.py"),
        plugin_path(root, RUNNER_SCRIPTS + "/read_admin_email.py"),
    ):
        return True
    return is_vendor_script(first)


def is_allowed_command(agent, command, root):
    if not isinstance(command, str):
        return False
    words = split_command(command)
    if not words:
        return False
    root = root if isinstance(root, str) else ""
    if agent == CHECKER:
        return bool(root) and is_health_script_call(words, root)
    return is_runner_call(words, root)


def reads_secrets_file(file_path, cwd):
    """True when the path, or what it resolves to, names a secrets file."""
    if not isinstance(file_path, str) or not file_path:
        return True
    expanded = os.path.expanduser(file_path)
    if not os.path.isabs(expanded):
        expanded = os.path.join(cwd if isinstance(cwd, str) and cwd else os.getcwd(), expanded)
    names = (os.path.basename(expanded), os.path.basename(os.path.realpath(expanded)))
    return any(name.lower() in SECRET_FILE_NAMES for name in names)


def decide(payload, env):
    """Return (exit code, stderr message) for one hook invocation."""
    agent = restricted_agent(payload.get("agent_type"))
    if agent is None:
        return 0, ""
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        tool_input = {}
    tool = payload.get("tool_name")
    if tool == "Skill" and not is_allowed_skill(tool_input.get("skill"), agent):
        return 2, SKILL_BLOCK.format(skills=", ".join(AGENT_SKILLS[agent]))
    if tool == "Bash" and not is_allowed_command(
        agent, tool_input.get("command"), env.get("CLAUDE_PLUGIN_ROOT")
    ):
        return 2, BASH_BLOCK[agent]
    if tool == "Read" and reads_secrets_file(tool_input.get("file_path"), payload.get("cwd")):
        return 2, READ_BLOCK
    return 0, ""


def main(stdin, env):
    try:
        payload = json.loads(stdin)
    except (ValueError, RecursionError):
        # An unparseable or too-deeply-nested payload hides the caller. Block if
        # it could come from a restricted agent rather than fail open.
        agent = next((a for a in AGENT_SKILLS if PLUGIN_NAME in stdin and a in stdin), None)
        if agent is None:
            return 0
        print(BASH_BLOCK[agent], file=sys.stderr)
        return 2
    if not isinstance(payload, dict):
        return 0
    try:
        code, message = decide(payload, env)
    except Exception:
        # Fail closed for the agents this hook exists to restrict.
        agent = restricted_agent(payload.get("agent_type"))
        if agent is None:
            return 0
        code, message = 2, BASH_BLOCK[agent]
    if code == 2:
        print(message, file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.stdin.buffer.read().decode("utf-8", "replace"), os.environ))
