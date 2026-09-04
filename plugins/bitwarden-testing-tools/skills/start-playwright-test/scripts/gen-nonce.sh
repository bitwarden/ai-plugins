#!/usr/bin/env bash
# Emit a cryptographically-random per-run fence token (16 hex chars).
set -euo pipefail
python3 -c "import secrets; print(secrets.token_hex(8))"
