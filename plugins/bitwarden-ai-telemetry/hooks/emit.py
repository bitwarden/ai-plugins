#!/usr/bin/env python3
"""Shared OTLP-JSON log emitter for bitwarden-ai-telemetry hooks.

Sends one POST per call to the collector configured via BW_TELEMETRY_OTLP
(normally set via managed-settings.json's `env` block). Never fails the
session — every error is swallowed.
"""
import json
import os
import time
import urllib.request
from urllib.parse import urlsplit

_ALLOWED_COLLECTOR_HOST = "bitwarden.pw"
_ALLOWED_COLLECTOR_SUFFIX = ".bitwarden.pw"


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


def emit(body_name, attrs):
    """POST one OTLP-JSON log record. ``attrs`` is a dict of str -> value;
    empty/falsey values are dropped. No-op when BW_TELEMETRY_OTLP isn't set,
    isn't https, or isn't a bitwarden.pw host. Fail-open otherwise: any error
    returns silently."""
    if not COLLECTOR:
        return
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
        urllib.request.urlopen(req, timeout=1)
    except Exception:
        pass  # fail-open, always
