# Atlassian Reader — Claude Instructions

## Read-Only Enforcement

This plugin includes a safety hook (`hooks/block-mutating-atlassian.sh`) that blocks all mutating API calls to Atlassian. The hook uses an allowlist security model — only explicitly safe curl patterns are permitted, everything else is denied.

**Never create, update, or delete any Atlassian resource.**

## After Modifying Hooks

When any change is made to `hooks/block-mutating-atlassian.sh` or `hooks/hooks.json`:

1. Read `skills/atlassian-reader/references/hook-testing.md` for the test harness and full category list
2. Generate test payloads dynamically for every gate — do not commit test payloads to source control
3. Run both safe (must pass) and blocked (must deny) cases
4. Verify each blocked case returns `permissionDecision: "deny"` with the correct gate's message
