#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCATOR="${SCRIPT_DIR}/../locate-logs.sh"
FAILED=0

assert_path() {
    local name="$1" platform="$2" project="$3" expected="$4"
    shift 4
    local actual
    actual=$(OSTYPE="$platform" bash "$LOCATOR" "$project" "$@")
    if [[ "$actual" != "${HOME}/.claude/projects/${expected}" ]]; then
        printf 'FAIL %s\n  expected: %s\n  actual: %s\n' "$name" "${HOME}/.claude/projects/${expected}" "$actual"
        FAILED=$((FAILED + 1))
    else
        printf 'PASS %s\n' "$name"
    fi
}

assert_path 'Unix path' linux-gnu /Users/user/project -Users-user-project
assert_path 'Unix single-letter directory' linux-gnu /c/project -c-project
assert_path 'Unix backslash in directory name' linux-gnu '/Users/user/a\b' '-Users-user-a\b'
assert_path 'Windows backslashes' msys 'C:\Users\user\project' C--Users-user-project
assert_path 'Windows forward slashes' msys C:/Users/user/project C--Users-user-project
assert_path 'Windows mixed separators' msys 'C:\Users/user\project' C--Users-user-project
assert_path 'Lowercase Windows drive' msys c:/Users/user/project C--Users-user-project
assert_path 'Windows path from Unix shell' linux-gnu 'D:\Projects\app' D--Projects-app
assert_path 'Git Bash path' msys /c/Users/user/project C--Users-user-project
assert_path 'Git Bash uppercase drive' msys /D/Projects/app D--Projects-app
assert_path 'Session filename' msys /c/Users/user/project C--Users-user-project/demo-session.jsonl demo-session

if (( FAILED > 0 )); then
    exit 1
fi
