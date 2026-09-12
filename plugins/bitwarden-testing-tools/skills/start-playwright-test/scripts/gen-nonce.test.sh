#!/usr/bin/env bash
# Test: gen-nonce.sh prints exactly one 16-char lowercase hex token.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
out="$("$DIR/gen-nonce.sh")"
if [[ ! "$out" =~ ^[0-9a-f]{16}$ ]]; then
  echo "FAIL: output not 16 hex chars: '$out'"; exit 1
fi
out2="$("$DIR/gen-nonce.sh")"
if [[ "$out" == "$out2" ]]; then
  echo "FAIL: two runs produced the same token (not random)"; exit 1
fi
echo "PASS"
