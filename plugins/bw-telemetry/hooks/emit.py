#!/usr/bin/env python3
"""Shared OTLP-JSON log emitter for bw-telemetry hooks.

Sends one POST per call to the collector configured via BW_TELEMETRY_OTLP
(normally set via managed-settings.json's `env` block). Never fails the
session — every error is swallowed.
"""
import json
import os
import time
import urllib.request

COLLECTOR = os.environ.get("BW_TELEMETRY_OTLP")


def emit(body_name, attrs):
    """POST one OTLP-JSON log record. ``attrs`` is a dict of str -> value;
    empty/falsey values are dropped. No-op when BW_TELEMETRY_OTLP isn't set.
    Fail-open otherwise: any error returns silently."""
    if not COLLECTOR:
        return
    kv = [{"key": k, "value": {"stringValue": str(v)}}
          for k, v in attrs.items() if v]
    payload = {"resourceLogs": [{
        "resource": {"attributes": [
            {"key": "service.name", "value": {"stringValue": "bw-telemetry"}}]},
        "scopeLogs": [{"scope": {"name": "bw.telemetry.hooks"},
                       "logRecords": [{"timeUnixNano": str(time.time_ns()),
                                       "body": {"stringValue": body_name},
                                       "attributes": kv}]}]}]}
    try:
        req = urllib.request.Request(
            COLLECTOR, data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=1).read()
    except Exception:
        pass  # fail-open, always
