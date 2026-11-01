#!/usr/bin/env bash
# Extracts the classifier's JSON result from its final message, the way every caller should.
# The JSON starts at the first line that begins with "{". Any text before it and any code fence are
# dropped. Exits non-zero when no valid JSON object remains, which a caller treats as no-verdict.
# Usage: extract-result.sh < final-message.txt > result.json
set -euo pipefail
sed -e '/^```/d' | awk '/^\{/ { found = 1 } found' | jq -e 'if type == "object" then . else error("not an object") end'
