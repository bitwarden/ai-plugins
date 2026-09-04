#!/usr/bin/env bash
# Deletes the scratch directory created by gather-evidence.sh. Only accepts
# a single path matching that script's exact mktemp pattern
# (/tmp/plugin-audit.XXXXXXXX, 8 characters), so a path an adversarial
# audited repo could influence (e.g. via prompt injection into the agent's
# own command construction) can't ride along as an extra rm target under
# this script's allowed-tools grant.
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "usage: cleanup.sh <scratch-dir>" >&2
  exit 2
fi

target=$1

case "$target" in
  /tmp/plugin-audit.????????) ;;
  *)
    echo "Refusing to delete unexpected path: $target" >&2
    exit 1
    ;;
esac

rm -rf -- "$target"
