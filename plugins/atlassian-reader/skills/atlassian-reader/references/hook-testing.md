# Hook Testing Reference

How to validate the read-only safety hook (`hooks/block-mutating-atlassian.sh`) after any modification.

## Test Harness

The hook reads JSON from stdin and writes JSON to stdout. Pipe a fake `PreToolUse` payload into the script and inspect the result:

```bash
bash hooks/block-mutating-atlassian.sh <<< '{"tool_input":{"command":"<CURL_COMMAND_HERE>"}}'
```

- **No output** = command was allowed (safe).
- **JSON with `permissionDecision: "deny"`** = command was blocked.

## Test Categories

After modifying any gate in the script, generate at least one test per category below. **Do not copy test payloads from this file into source control** — construct them dynamically at test time.

### Safe commands (must be ALLOWED)

| Category              | What to test                                                                     |
| --------------------- | -------------------------------------------------------------------------------- |
| Simple GET            | `curl -s` with an Atlassian URL, no method flag, no data flags                   |
| GET with query params | `curl -G --data-urlencode "jql=..." -H "Authorization: ..."` targeting Atlassian |
| Explicit GET          | `curl -X GET` targeting Atlassian                                                |
| Non-Atlassian URL     | Any curl with `-X POST` or data flags targeting a non-Atlassian domain           |

### Gate 1 — Shell indirection (must be BLOCKED)

Test that commands wrapped in execution indirection are denied:

- `eval` wrapping a curl to Atlassian
- `bash -c` wrapping a curl to Atlassian
- Pipe to `bash`/`sh`/`zsh` with Atlassian URL in the piped content
- Pipe to bare shell name: `| bash` (no path prefix)
- Pipe to non-standard path: `| /usr/local/bin/bash`
- Pipe to full-path env: `| /usr/bin/env bash`

### Gate 2 — Non-curl HTTP clients (must be BLOCKED)

Test that alternative clients targeting Atlassian are denied:

- `wget` with Atlassian URL
- `python` or `node` with Atlassian URL
- `http` (httpie) with Atlassian URL

### Gate 3 — Mutating HTTP methods (must be BLOCKED)

Test all method flag variants:

- `-X POST`, `-X PUT`, `-X DELETE`, `-X PATCH` (with space)
- `-XPOST`, `-XDELETE` (no space — curl accepts this)
- `--request=PUT`, `--request=PATCH` (equals sign)
- Case variations: `-X post`, `-X Post`
- Note: lowercase `-x` (which is curl's `--proxy` flag, not `--request`) is also flagged due to case-insensitive matching — this is intentional safe-side behavior
- Shell-quoted method: `-X"POST"` (double-quoted, no space after -X)
- Shell-quoted method: `-X'DELETE'` (single-quoted, no space after -X)

### Gate 4 — `--json` flag (must be BLOCKED)

Test the implicit-POST flag added in curl 7.82:

- `curl --json '{"key":"val"}' <atlassian-url>`
- `curl --json=<value> <atlassian-url>`

### Gate 5 — Data payload flags without `-G` (must be BLOCKED)

Test data flags that imply POST when `-G` is absent:

- `-d "data"`, `-d"data"` (no space), `-d@file`
- `--data "val"`, `--data="val"`
- `--data-raw`, `--data-binary`, `--data-urlencode` (all without `-G`)

Also verify the **safe case**: `-G` present with `--data-urlencode` must be ALLOWED.

### Gate 6 — Blocked flags (must be BLOCKED)

Test flags the skill never needs:

- `-F`/`--form` (multipart upload)
- `-T`/`--upload-file` (PUT upload)
- `-o`/`--output`/`-O` (write to file)
- `-K`/`--config` (load options from file — bypasses all regex checks)
- `-:`/`--next` (transfer group separator — resets per-transfer options like -G)

### Gate 7 — Variable expansion in method position (must be BLOCKED)

Test shell variable patterns in the `-X` argument:

- `-X $METHOD`
- `-X ${METHOD}`
- `-X $(echo POST)`

## Interpreting Results

For each blocked test, verify the JSON output contains:

1. `"permissionDecision": "deny"` — confirms the hook blocked it
2. A `systemMessage` that identifies **which gate** triggered — confirms the right gate fired (not a false match from a different gate)

For each allowed test, verify **no output** and exit code 0.

## When to Run

- After modifying any gate's regex
- After adding a new gate
- After upgrading curl (new flags may appear)
- During code review of hook changes
