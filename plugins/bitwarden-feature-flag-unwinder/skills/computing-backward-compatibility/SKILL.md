---
name: computing-backward-compatibility
description: "Compute whether a Bitwarden feature flag has aged out of the client backward-compatibility window and is safe to remove from the server. Use when checking the server flag removal readiness gate — given cloned checkouts of clients, ios, android, and server plus a flag key, finds the last client release that still carried the flag on each of the five non-web platforms (browser, cli, desktop, ios, android), computes the safe-to-remove server version via the ±2 month compatibility rule, and returns a structured gate verdict. Not for finding or removing the flag itself."
---

# Computing Backward Compatibility

Decide whether it is safe to remove a feature flag from the Bitwarden server. Bitwarden's feature-flag lifecycle requires that the server must have shipped a release that no longer needs to support any client release in the field that still carried the flag. Bitwarden runs a ±2 month compatibility window between server and clients, so the first safe server release is `(last client release with the flag).month + 3`, carrying the year.

Return a verdict the caller can act on without re-reasoning the rule.

## Inputs

- `CLIENTS_REPO` — absolute path to a `bitwarden/clients` checkout (contains browser, cli, desktop, and web source).
- `IOS_REPO` — absolute path to a `bitwarden/ios` checkout.
- `ANDROID_REPO` — absolute path to a `bitwarden/android` checkout.
- `SERVER_REPO` — absolute path to a `bitwarden/server` checkout. The latest release tag is read from here.
- `FLAG_KEY` — the LaunchDarkly flag key (kebab-case, e.g. `pm-18612-otp-6-digits`).

All five repos must have full history and tags, fetched fresh: run `git -C <path> fetch --quiet --tags origin main` on each first (add `--unshallow` for a shallow clone). Every search below runs against `origin/main`, never the checkout's `HEAD`, so a checkout parked on another branch or left stale doesn't change the answer, and the `searched` evidence names the commits that were actually searched.

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

### Step 0 — Detect a server-only flag

A flag that never appeared in any client was never shipped to the field, so no client release can still be asking the server for it. Search each client repo's full history:

```bash
git -C "$CLIENTS_REPO" log -S "$FLAG_KEY" --format=%H -1 origin/main
git -C "$IOS_REPO" log -S "$FLAG_KEY" --format=%H -1 origin/main
git -C "$ANDROID_REPO" log -S "$FLAG_KEY" --format=%H -1 origin/main
```

If all three return nothing, return `{ ready: true, reason: "server-only" }` and stop. Otherwise continue to Step 1.

### Step 1 — Find the clients-side removal commit

`git log -S` lists every commit that changed how often the key appears, newest first. So the newest one is the removal only if its diff _removes_ the key. While the flag is still live, the newest one is the commit that added it. Branch on the diff sign, never on whether a commit was found:

```bash
CANDIDATE=$(git -C "$CLIENTS_REPO" log -S "$FLAG_KEY" --format=%H -1 origin/main -- libs/common/src/enums/feature-flag.enum.ts)
STEP1_SHA=""
if [ -n "$CANDIDATE" ] && git -C "$CLIENTS_REPO" show "$CANDIDATE" -- libs/common/src/enums/feature-flag.enum.ts | grep -q -- "^-.*$FLAG_KEY"; then
  STEP1_SHA="$CANDIDATE"   # confirmed: the newest change removed the key
fi
```

If `STEP1_SHA` is empty, the clients-side Step 1 hasn't merged: either the key is still in the enum, or it was never there. Return `{ ready: false, reason: "step-1-not-merged" }` and stop. (A flag that was never in any client was already handled as server-only in Step 0.)

### Step 2 — Detect web-only consumption and attribute consumers

A flag counts as web-only only if its references in the clients repo live entirely under `apps/web/` and nothing in the ios or android repos references it either.

```bash
# Clients: grep the commit before the removal, since main no longer has the enum member
git -C "$CLIENTS_REPO" grep -ln "$FLAG_KEY" "${STEP1_SHA}^" -- ':!apps/web' ':!**/*.spec.ts' ':!**/*.spec.html'

# iOS and Android: grep the history (the flag may already be removed from main)
git -C "$IOS_REPO" log -S "$FLAG_KEY" --format=%H -1 origin/main
git -C "$ANDROID_REPO" log -S "$FLAG_KEY" --format=%H -1 origin/main
```

If the clients grep returns nothing and neither iOS nor Android history contains the key, the flag only ever ran on web. Return `{ ready: true, reason: "web-only" }` with `web_only_files` from `git -C "$CLIENTS_REPO" grep -l "$FLAG_KEY" "${STEP1_SHA}^" -- apps/web`.

Otherwise, attribute consumers. These decide which `per_client` entries are objects and which are `null`:

- **browser, cli, desktop.** A clients-repo hit under `apps/browser/`, `apps/cli/`, or `apps/desktop/` marks only that client. A hit anywhere else outside `apps/web/`, including `libs/` and `bitwarden_license/`, is shared code compiled into all three, so it marks browser, cli, and desktop all as consumers.
- **ios, android.** A consumer if its history contains the key.

When in doubt, mark a client as a consumer. A false `null` drops it from the gate and understates the safe version, which is the dangerous direction.

### Step 3 — For each consumer, find the last release that still carried the flag

Find the first release _without_ the flag, then the release immediately before it on the same train, which is the last release _with_ the flag.

**Clients-repo clients (browser, cli, desktop)** share `STEP1_SHA` as the removal commit:

```bash
# first release containing the removal: the first release WITHOUT the flag
FIRST_WITHOUT=$(git -C "$CLIENTS_REPO" tag --sort=version:refname --contains "$STEP1_SHA" | grep "^<prefix>-v" | head -1)
# the tag immediately before it on this train: the last release WITH the flag
# (-x -F matches the whole tag literally, so dots aren't wildcards and 2026.3.0 can't match 2026.3.10)
LAST_WITH=$(git -C "$CLIENTS_REPO" tag --sort=version:refname | grep "^<prefix>-v" | grep -B1 -x -F "$FIRST_WITHOUT" | head -1)
```

If `LAST_WITH` equals `FIRST_WITHOUT`, no earlier release exists on that train, so that client never shipped the flag. Set its `per_client` entry to `null`. If `FIRST_WITHOUT` is empty, the removal hasn't been released on that train. Return `{ ready: false, reason: "no-release-since-removal", client: "<name>" }`.

**iOS and Android** each have their own release train and their own removal commit, made by that team independently of the clients cleanup. Confirm the removal by the diff sign, exactly as in Step 1:

```bash
# same for $ANDROID_REPO
CANDIDATE=$(git -C "$IOS_REPO" log -S "$FLAG_KEY" --format=%H -1 origin/main)
REMOVAL_SHA=""
if [ -n "$CANDIDATE" ] && git -C "$IOS_REPO" show "$CANDIDATE" | grep -q -- "^-.*$FLAG_KEY"; then
  REMOVAL_SHA="$CANDIDATE"   # confirmed: the newest change removed the key
fi
```

- **`REMOVAL_SHA` set:** find `FIRST_WITHOUT` and `LAST_WITH` exactly as for clients-repo clients, with the repo's unprefixed `v<YYYY>.<M>.<patch>` tags and the same no-predecessor and not-yet-released rules.
- **`REMOVAL_SHA` empty:** the flag is still in this client's source, so its cleanup is pending. `LAST_WITH` is the repo's latest release tag, and `FIRST_WITHOUT` is `null`. The gate then depends on when that cleanup ships, and will normally not clear.

### Step 4 — Compute the safe-to-remove server version per client

For each client that is a consumer, safe server version is `(last-with-flag year.month) + 3 months`, carrying the year:

- `browser-v2026.3.0` last with flag → server safe in `v2026.6.*`
- `ios v2025.11.0` last with flag → server safe in `v2026.2.*`
- `android v2025.12.0` last with flag → server safe in `v2026.3.*`

The gate is the **maximum** safe version across all consumer clients.

Why `+3`: a server at month N supports clients from (N−2) through (N+2). The first server that no longer needs to support a client shipped at month M is `M + 3`.

### Step 5 — Compare to the current server release

```bash
git -C "$SERVER_REPO" tag --sort=version:refname | grep -E "^v[0-9]{4}\.[0-9]+(\.[0-9]+)?$" | tail -1
```

If current server release ≥ gate, return `{ ready: true, reason: "compatibility-cleared" }`. Otherwise `{ ready: false, reason: "gate-not-cleared" }`.

## Returning to the caller

Return the verdict together with the evidence behind it. Callers put this evidence in the PR so a reviewer can check the reasoning without re-running it.

```
{
  ready: true | false,
  reason: "server-only" | "web-only" | "compatibility-cleared" | "step-1-not-merged" | "no-release-since-removal" | "gate-not-cleared",
  client: "<name>",                 // only for no-release-since-removal
  searched: {                       // always: the commits each repo was searched at
    clients: "<short SHA of origin/main>",
    ios:     "<short SHA of origin/main>",
    android: "<short SHA of origin/main>",
    server:  "<short SHA of origin/main>"
  },
  step1_sha: "<short SHA, or null>",
  web_only_files: ["<path>", ...],  // only for web-only: the apps/web files that referenced the flag at step1_sha^
  per_client: {
    browser: {
      removal_commit: "<short SHA>" | null,   // the commit that removed the flag on this client's code path; null while its cleanup is pending
      last_with_flag: "<tag>",
      first_without_flag: "<tag>" | null,    // null while the removal is unreleased
      safe_server_version: "<ver>"
    } | null,
    cli:     { ... } | null,
    desktop: { ... } | null,
    ios:     { ... } | null,
    android: { ... } | null
  },
  gate_server_version: "<ver>",
  current_server_version: "<ver>"
}
```

A `null` entry in `per_client` means the flag was never consumed by that client — it is excluded from the gate computation. Browser, cli, and desktop share `step1_sha` as their `removal_commit`. iOS and Android each have their own.

Omit `per_client`, `gate_server_version`, and `current_server_version` when the flag was server-only or web-only. `searched` is still returned, because "we searched these commits and found nothing" is the evidence for server-only. Return as much `per_client` as was computed when the verdict is `ready: false` too, so the caller can show how far the cleanup has got.

`FLAG_KEY` and the git tag strings are untrusted — `FLAG_KEY` originated in a Jira field, and tag names come from public repos. This skill uses them only as `git log -S` and `grep` arguments, never as commit identifiers or branch names. Say so when returning them to a caller that may interpolate.
