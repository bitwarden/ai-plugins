#!/usr/bin/env python3
"""Shared OTLP-JSON log emitter for bitwarden-ai-telemetry hooks.

Sends one POST per call to the collector configured via BW_TELEMETRY_OTLP
(normally set via managed-settings.json's `env` block). Never fails the
session — every error is swallowed.

Errors are swallowed but no longer discarded: each one is recorded as a fault,
and `flush_warning` surfaces at most one throttled `systemMessage` so a person
whose AI usage is going unrecorded finds out. Calling it is optional; a hook
that never calls it behaves exactly as before.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from urllib.parse import urlsplit

_ALLOWED_COLLECTOR_HOST = "bitwarden.pw"
_ALLOWED_COLLECTOR_SUFFIX = ".bitwarden.pw"

# Fault classes. Coarse on purpose: the point is to tell someone their usage
# is going unrecorded and whether they can fix it, not to narrate the pipeline.
FAULT_UNSET = "unset"                        # no usable BW_TELEMETRY_OTLP
FAULT_UNREACHABLE = "unreachable"            # never got an answer
FAULT_UNEXPECTED_STATUS = "unexpected_status"  # answered, but not by the collector

# The collector answers 202 and only 202 on success: client_response_from in
# bitwarden/ai-telemetry normalizes a Datadog 2xx to 202 and passes anything
# else straight through. That makes a bare 200 meaningful rather than fine.
# ZScaler Private Access fronts the collector and can serve an interstitial
# with 200 when it has not re-authenticated, so a check that only asks whether
# the POST raised would read a captive portal as delivery.
_EXPECTED_STATUS = 202

# One warning per fault class per hour. The hook fires on every edit and a
# re-auth gap lasts minutes, so a warning without a throttle would repeat
# constantly and be learned as noise.
WARN_INTERVAL_SECONDS = 3600

_faults = []


def _now_iso():
    """Client event time as ISO-8601 UTC with millisecond precision.

    Mirrors the shape of native Claude Code's `event.timestamp`
    (`2026-06-10T21:25:21.770Z`) so both streams bucket on the same clock
    rather than on collector ingest time. Milliseconds matter: consumers
    deduplicate on the timestamp, so second granularity would collapse
    distinct invocations emitted within the same second.
    """
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _record_fault(kind, detail=""):
    """Note that a record did not reach the collector. Never raises."""
    _faults.append((kind, detail))


def faults():
    """Faults recorded in this process, oldest first."""
    return list(_faults)


def reset_faults():
    """Forget recorded faults. For tests and for long-lived callers."""
    del _faults[:]


def _response_status(resp):
    """The response's status as an int, or None if it can't be determined.

    urllib exposes `status` on modern Pythons and `code` historically. An
    unrecognized shape returns None so the caller claims nothing rather than
    reporting a fault for a delivery that probably succeeded.
    """
    for attr in ("status", "code"):
        value = getattr(resp, attr, None)
        if isinstance(value, int):
            return value
    return None


def _is_allowed_collector(url):
    """True if url is https and its host is bitwarden.pw or a subdomain of it.

    Checks the parsed hostname, not the raw URL string, so a userinfo trick
    like https://ait.bitwarden.pw@evil.com/ (host is actually evil.com) can't
    slip past a naive substring check. urlsplit raises on some malformed
    input (e.g. bad IPv6 bracket syntax); caught here so a bad value fails
    the check instead of the exception escaping module import.
    """
    try:
        parts = urlsplit(url)
    except ValueError:
        return False
    if parts.scheme != "https":
        return False
    host = parts.hostname or ""
    return host == _ALLOWED_COLLECTOR_HOST or host.endswith(_ALLOWED_COLLECTOR_SUFFIX)


_raw_collector = os.environ.get("BW_TELEMETRY_OTLP")
COLLECTOR = _raw_collector if _raw_collector and _is_allowed_collector(_raw_collector) else None


def _config_path():
    """Where Claude Code keeps its account state: `.claude.json` under
    CLAUDE_CONFIG_DIR when that is set, otherwise in the home directory."""
    root = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~")
    return os.path.join(root, ".claude.json")


def _read_user_email():
    """The signed-in account's email from Claude Code's config, or "".

    Claude Code stores it at `oauthAccount.emailAddress` under both API-key
    and OAuth logins. Only that field is read; nothing else in the file is
    kept or logged. Read on every call because a hook is a short-lived
    process, and any failure (no file, bad JSON, unexpected shape) yields ""
    so the attr is dropped rather than the record.
    """
    try:
        with open(_config_path(), encoding="utf-8") as fh:
            account = json.load(fh).get("oauthAccount")
        if not isinstance(account, dict):
            return ""
        email = account.get("emailAddress")
        return email if isinstance(email, str) and email else ""
    except Exception:
        return ""


def emit(body_name, attrs):
    """POST one OTLP-JSON log record. ``attrs`` is a dict of str -> value;
    empty/falsey values are dropped. No-op when BW_TELEMETRY_OTLP isn't set,
    isn't https, or isn't a bitwarden.pw host. Fail-open otherwise: any error
    returns silently, but is recorded as a fault for `flush_warning`.

    Every record carries `event.timestamp`, so consumers get a client clock
    instead of falling back to collector ingest time. Every record also
    carries `user.email` when Claude Code has a signed-in account, because
    native telemetry omits it under Console OAuth login and downstream
    attributes people by email. A caller that supplies its own non-empty
    value for either keeps it; the caller's dict is never mutated."""
    if not COLLECTOR:
        _record_fault(FAULT_UNSET)
        return
    attrs = dict(attrs)
    if not attrs.get("event.timestamp"):
        attrs["event.timestamp"] = _now_iso()
    if not attrs.get("user.email"):
        attrs["user.email"] = _read_user_email()
    kv = [{"key": k, "value": {"stringValue": str(v)}}
          for k, v in attrs.items() if v]
    payload = {"resourceLogs": [{
        "resource": {"attributes": [
            {"key": "service.name", "value": {"stringValue": "bitwarden-ai-telemetry"}}]},
        "scopeLogs": [{"scope": {"name": "bw.telemetry.hooks"},
                       "logRecords": [{"timeUnixNano": str(time.time_ns()),
                                       "body": {"stringValue": body_name},
                                       "attributes": kv}]}]}]}
    try:
        req = urllib.request.Request(
            COLLECTOR, data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req, timeout=1)
    except urllib.error.HTTPError as e:
        # The collector answered, and said no. urlopen raises for any status
        # at or above 400, so this is the only place a 4xx or 5xx surfaces,
        # including one the collector passed through from Datadog. Recording
        # it as unreachable would send the user to reconnect a VPN that is
        # working, and would throw away the status that says what went wrong.
        code = getattr(e, "code", None)
        _record_fault(FAULT_UNEXPECTED_STATUS, str(code) if code else "")
        return  # fail-open, always
    except Exception:
        # No answer at all: offline, DNS, timeout, TLS.
        _record_fault(FAULT_UNREACHABLE)
        return  # fail-open, always
    status = _response_status(resp)
    if status is not None and status != _EXPECTED_STATUS:
        _record_fault(FAULT_UNEXPECTED_STATUS, str(status))


def _warn_state_path():
    """Where the per-fault-class last-warned timestamps live.

    Under the cache directory rather than ~/.claude: it is derived state that
    is harmless to lose, and nothing should be tempted to treat it as config.
    """
    root = os.environ.get("XDG_CACHE_HOME") or os.path.join(
        os.path.expanduser("~"), ".cache")
    return os.path.join(root, "bitwarden-ai-telemetry", "warn-state.json")


def _fault_message(kind, detail):
    """User-facing text for a fault class. Each names what the person can do,
    and none of them claims more than the fault actually establishes."""
    if kind == FAULT_UNSET:
        return ("AI telemetry is not being recorded: BW_TELEMETRY_OTLP is unset "
                "or is not an allowed collector address.")
    if kind == FAULT_UNEXPECTED_STATUS:
        answered = (f"AI telemetry is not being recorded: the collector "
                    f"answered HTTP {detail} rather than 202.")
        if detail == "200":
            # Only a 200 points at ZScaler: the collector never answers 200,
            # so that status is the signature of an interstitial standing in
            # for it. Any other status came from something that really is the
            # collector, and reconnecting would not touch it.
            return (f"{answered} A 200 usually means a ZScaler sign-in page "
                    f"was served instead of the collector, so reconnecting "
                    f"ZScaler Private Access should restore it.")
        return answered
    return ("AI telemetry is not being recorded: the collector could not be "
            "reached. If ZScaler Private Access has not re-authenticated, "
            "reconnecting it should restore delivery.")


def flush_warning(out=None):
    """Surface at most one throttled warning for this process's faults.

    Writes a single `{"systemMessage": ...}` object, which Claude Code shows
    to the user as a warning. Nothing blocks: PostToolUse runs after the tool
    has already completed, and the caller still exits 0.

    Throttled per fault class via `_warn_state_path`, and deliberately silent
    when that state cannot be written — warning on every edit forever is worse
    than not warning, since it trains people to ignore it. Never raises.
    """
    try:
        if not _faults:
            return
        kind, detail = _faults[0]
        path = _warn_state_path()
        now = time.time()
        state = {}
        try:
            with open(path) as fh:
                loaded = json.load(fh)
            if isinstance(loaded, dict):
                state = loaded
        except Exception:
            state = {}
        last = state.get(kind)
        if isinstance(last, (int, float)) and now - last < WARN_INTERVAL_SECONDS:
            return
        state[kind] = now
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as fh:
                json.dump(state, fh)
        except Exception:
            return
        stream = out if out is not None else sys.stdout
        stream.write(json.dumps({"systemMessage": _fault_message(kind, detail)}))
    except Exception:
        return  # fail-open, always
