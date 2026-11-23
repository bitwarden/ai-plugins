---
name: setting-up-regression-runs
description: Use when setting up the QA manual regression runs for a Bitwarden release in Testmo — e.g. "set up the 2026.8.0 regression runs", "create the partial release regression suite", "create the full regression runs for this milestone". Picks the release profile (partial or full), applies any per-release exclusions, and hands the profile's shipped specs to the bitwarden-testmo-tools creating-test-runs skill. Do NOT use it for a one-off Testmo run outside a release (use creating-test-runs directly) or to write test cases.
argument-hint: "[partial | full] [milestone name]"
allowed-tools: "Read, Skill(bitwarden-testmo-tools:creating-test-runs)"
---

# Setting Up Regression Runs

Bitwarden's manual regression suite for a release is a fixed set of Testmo runs, one per spec in
`specs/`, all linked to the release's milestone. This skill decides **which** specs a release needs;
`Skill(bitwarden-testmo-tools:creating-test-runs)` creates them. If that skill is not available, stop
and ask the user to install `bitwarden-testmo-tools`.

## Release profiles

[`release-profiles.json`](release-profiles.json) lists every spec in each profile:

- **`partial`** — Web (Password Manager, Admin Console, Admin Portal / SM / Providers), Old Client /
  New Server, Mobile (iOS, Android), and Directory Connector (BWDC).
- **`full`** — the same Web, Old Client / New Server, and Mobile runs, plus CLI, 3 Desktop and 4
  Extension configuration variants. **No BWDC.**

`full` is not a superset of `partial`. Use exactly the list in the file.

## Workflow

1. **Collect the inputs** from the user: the profile (`partial` or `full`), the milestone's exact name
   (e.g. `2026.8.0 Manual Regression`), and any spec to skip this release. Ask for whichever is missing.
2. **Confirm the milestone exists.** The user creates it in the Testmo UI — the API cannot. Releases
   use a parent `YYYY.M.0 Release` milestone with `… Manual Regression` and `… Automated Regression`
   children; manual regression runs link to the `… Manual Regression` child.
3. **Build the spec list.** Read the profile from `release-profiles.json` and drop any skipped specs.
   A name the user asks to skip that is not in the profile is a typo — stop and ask rather than
   continuing. Turn each remaining name into
   `${CLAUDE_PLUGIN_ROOT}/skills/setting-up-regression-runs/specs/<name>.json`, written out as a
   literal absolute path. Never pass `${CLAUDE_PLUGIN_ROOT}` itself to `creating-test-runs` — in that
   skill it means the `bitwarden-testmo-tools` root, not this plugin's.
4. **Hand off.** Invoke `Skill(bitwarden-testmo-tools:creating-test-runs)` and follow it, passing every
   spec path as its own `--spec` and the milestone as `--milestone-name`. That skill owns the dry-run,
   the user's review, and `--create` — never run the dry-run and `--create` in the same turn.
5. **Finish the multi-configuration runs.** Every Mobile, Desktop, and Extension run needs a manual
   Testmo UI pass after creation (`full` has all three; `partial` only Mobile). Tell the user which runs
   still need it, using [`references/regression-configurations.md`](references/regression-configurations.md)
   and each spec's `_comment`.

To add one run that is missing from an already-populated milestone, pass only that spec — the
script's per-run duplicate check leaves the existing runs alone.

## Changing the suite

The specs and profiles here are shipped in the plugin; edits in the installed copy are overwritten by
`/plugin update`. If a spec is skipped every cycle, or a new run joins the suite, change `specs/` and
`release-profiles.json` in a PR to `bitwarden/ai-plugins`.

Case counts drift as the repository changes. Compare each dry-run against the previous cycle; a large
swing usually means a renamed folder or tag.
