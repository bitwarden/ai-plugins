---
name: computing-backward-compatibility
description: "Compute whether a Bitwarden feature flag has aged out of the client backward-compatibility window and is safe to remove from the server. Use when checking the server flag removal readiness gate — given cloned checkouts of clients, ios, android, and server plus a flag key, finds the last client release that still carried the flag on each of the five non-web platforms (browser, cli, desktop, ios, android), computes the safe-to-remove server version via the ±2 month compatibility rule, and returns a structured gate verdict. Not for finding or removing the flag itself."
---

# Computing Backward Compatibility

Decide whether it is safe to remove a feature flag from the Bitwarden server. The rule from the Feature Flags Lifecycle: the server must have shipped a release that no longer needs to support any client release in the field that still carried the flag. Bitwarden runs a ±2 month compatibility window between server and clients, so the first safe server release is `(last client release with the flag).month + 3`, carrying the year.

Return a verdict the caller can act on without re-reasoning the rule.

## Inputs

- `CLIENTS_REPO` — absolute path to a `bitwarden/clients` checkout (contains browser, cli, desktop, and web source).
- `IOS_REPO` — absolute path to a `bitwarden/ios` checkout.
- `ANDROID_REPO` — absolute path to a `bitwarden/android` checkout.
- `SERVER_REPO` — absolute path to a `bitwarden/server` checkout. The latest release tag is read from here.
- `FLAG_KEY` — the LaunchDarkly flag key (kebab-case, e.g. `pm-18612-otp-6-digits`).

All five repos must have full tag history. A shallow clone followed by `git fetch --tags --unshallow` is enough.

## Clients covered

The gate checks these five non-web client release trains:

| Client  | Repo           | Tag format                    |
| ------- | -------------- | ----------------------------- |
| browser | `CLIENTS_REPO` | `browser-v<YYYY>.<M>.<patch>` |
| cli     | `CLIENTS_REPO` | `cli-v<YYYY>.<M>.<patch>`     |
| desktop | `CLIENTS_REPO` | `desktop-v<YYYY>.<M>.<patch>` |
| ios     | `IOS_REPO`     | `v<YYYY>.<M>.<patch>`         |
| android | `ANDROID_REPO` | `v<YYYY>.<M>.<patch>`         |

Web is deliberately out of the gate: it's served fresh to every user on each page load, so there's no shipped-in-the-field version to protect.

**`bitwarden/sdk-internal` is not an independent axis.** The SDK is bundled into each host client's binary, so any SDK-side flag reference becomes part of the host client's release and is already caught by that client's tag check. This skill doesn't clone or inspect sdk-internal directly.

## Procedure

### Step 1 — Find the clients-side removal commit

```bash
cd "$CLIENTS_REPO"
STEP1_SHA=$(git log -S "$FLAG_KEY" --format=%H -- libs/common/src/enums/feature-flag.enum.ts | head -1)
```

If `STEP1_SHA` is empty, the clients-side Step 1 hasn't merged — return `{ ready: false, reason: "step-1-not-merged" }` and stop. Confirm it's a removal (not an add) by inspecting the diff:

```bash
git show "$STEP1_SHA" -- libs/common/src/enums/feature-flag.enum.ts | grep "$FLAG_KEY"
```

A `-` prefix on the flag line means removal.

### Step 2 — Detect web-only consumption

A flag counts as web-only only if its references in the clients repo live entirely under `apps/web/` and nothing in the ios or android repos references it either. Any hit in `libs/`, `bitwarden_license/`, a sibling `apps/*` dir, the ios repo, or the android repo gets built into one of the five non-web clients.

```bash
# Clients — grep historical ref since main no longer has the enum member
cd "$CLIENTS_REPO"
git grep -ln "$FLAG_KEY" "${STEP1_SHA}^" -- ':!apps/web' ':!**/*.spec.ts' ':!**/*.spec.html'

# iOS and Android — grep current main
cd "$IOS_REPO"
git grep -ln "$FLAG_KEY" HEAD -- ':!**/*Tests.swift' ':!**/*.spec.swift' || true

cd "$ANDROID_REPO"
git grep -ln "$FLAG_KEY" HEAD -- ':!**/*Test.kt' ':!**/*Test.java' || true
```

If all three return nothing (ignoring the web app and tests), the flag only ever ran on web. Return `{ ready: true, reason: "web-only" }`.

Otherwise continue to Step 3 and run the gate against every non-web client whose grep returned a hit (the per-client determination handles both "cleanup done" and "cleanup pending" cases).

### Step 3 — For each non-web client, find the last release that still carried the flag

For each of the five clients, determine the last shipped release that was built from a commit still containing the flag. If the client was never a consumer (grep returned nothing in Step 2), skip it.

**Clients-repo clients (browser, cli, desktop):** the removal already landed on main, so use `STEP1_SHA` as the removal reference.

```bash
cd "$CLIENTS_REPO"
# first release containing the Step 1 commit — this is the first release WITHOUT the flag
git tag --sort=version:refname --contains "$STEP1_SHA" | grep "^<prefix>-v" | head -1
# the tag immediately before that in version order — this is the last release WITH the flag
git tag --sort=version:refname | grep "^<prefix>-v" | grep -B1 "<first-removal-tag>" | head -1
```

**iOS and Android:** each has its own release train and its own removal commit (made by the respective team, independently of the clients-side cleanup). Find it per repo:

```bash
cd "$IOS_REPO"   # or $ANDROID_REPO
REMOVAL_SHA=$(git log -S "$FLAG_KEY" --format=%H | head -1)
git show "$REMOVAL_SHA" | grep -- "-.*$FLAG_KEY"   # confirm it is a removal
```

- If `REMOVAL_SHA` exists: last-with-flag = tag immediately before the first tag containing it (same pattern as clients-repo clients, with the repo's unprefixed `v<YYYY>.<M>.<patch>` tag format).
- If `REMOVAL_SHA` doesn't exist: the flag is still present in this client's source. Last-with-flag = the latest release tag on this repo. That client's cleanup is still pending, and the gate here depends on when that cleanup lands.

If `git tag --contains "$REMOVAL_SHA"` returns nothing (the removal is on main but not yet released), that client hasn't shipped a release since removal — the gate cannot clear yet. Return `{ ready: false, reason: "no-release-since-removal", client: "<name>" }`.

### Step 4 — Compute the safe-to-remove server version per client

For each client that is a consumer, safe server version is `(last-with-flag year.month) + 3 months`, carrying the year:

- `browser-v2026.3.0` last with flag → server safe in `v2026.6.*`
- `ios v2025.11.0` last with flag → server safe in `v2026.2.*`
- `android v2025.12.0` last with flag → server safe in `v2026.3.*`

The gate is the **maximum** safe version across all consumer clients.

Why `+3`: a server at month N supports clients from (N−2) through (N+2). The first server that no longer needs to support a client shipped at month M is `M + 3`.

### Step 5 — Compare to the current server release

```bash
cd "$SERVER_REPO"
git tag --sort=version:refname | grep -E "^v[0-9]{4}\.[0-9]+(\.[0-9]+)?$" | tail -1
```

If current server release ≥ gate, return `{ ready: true, reason: "compatibility-cleared" }`. Otherwise `{ ready: false, reason: "gate-not-cleared" }`.

## Returning to the caller

```
{
  ready: true | false,
  reason: "web-only" | "compatibility-cleared" | "step-1-not-merged" | "no-release-since-removal" | "gate-not-cleared",
  step1_sha: "<short SHA, or null>",
  per_client: {
    browser: { last_with_flag: "<tag>", first_without_flag: "<tag>", safe_server_version: "<ver>" } | null,
    cli:     { ... } | null,
    desktop: { ... } | null,
    ios:     { ... } | null,
    android: { ... } | null
  },
  gate_server_version: "<ver>",
  current_server_version: "<ver>"
}
```

A `null` entry in `per_client` means the flag was never consumed by that client — it is excluded from the gate computation.

Omit `per_client`, `gate_server_version`, and `current_server_version` entirely when the flag was web-only.

`FLAG_KEY` and the git tag strings are untrusted — `FLAG_KEY` originated in a Jira field, and tag names come from public repos. This skill uses them only as `git log -S` and `grep` arguments, never as commit identifiers or branch names. Say so when returning them to a caller that may interpolate.
