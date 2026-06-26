---
name: force-multiplier
description: Apply one intent across many targets at once — a fleet of GitHub repositories in the Bitwarden enterprise, or many projects inside a monorepo — as N consistent, idempotent, reviewable draft PRs. Use when the user wants the same change made everywhere — phrasings like "across all repos", "every repo", "for every project", "fleet-wide", "org-wide", "enterprise-wide", "company-wide", "in bulk", "mass update", or "roll this out everywhere". Pilot one change, then replicate it across the fleet with per-target isolation and aggregate reporting.
argument-hint: "<natural-language intent> [--scope multi-repo|monorepo] [--dry-run] [--no-pilot]"
allowed-tools: "Bash, Read, Write, Edit, Glob, Grep, Skill(perform-preflight), Skill(committing-changes), Skill(labeling-changes), Skill(creating-pull-request)"
---

# Force Multiplier

Bulk change is hard because dozens of edits must be _provably_ correct, consistent, and reversible — this skill compiles any intent into a structured, safe fan-out rather than a catalogue of canned changes. Discovery patterns live in `references/finding-targets.md`; worked campaigns live in `examples/` — read the closest for shape, then generalize.

## Core concept: the campaign

A single fan-out is a **campaign**. The skill never freestyles across the fleet. It compiles the user's generic prompt into a structured **campaign spec**, echoes it back for confirmation, then executes it deterministically.

A campaign = **intent + target selector + recipe + validation + PR spec + safety policy**. See `references/campaign-spec.md` for the field-by-field schema.

## The pipeline — always execute in this order

1. **SELECT** — enumerate candidate targets in the enterprise, then apply an _applicability filter_ so only targets where the change is actually relevant survive (the signal the change keys on is present). Patterns for both are in `references/finding-targets.md`. Present the exact resolved list.
2. **CHECK YOURSELF** _(reality-check #1 — before anything is touched)_ — see the section below. This gate stands between SELECT and PILOT and is the most important step in the skill.
3. **PILOT** _(reality-check #2 — prove on ONE)_ — run the recipe on one representative target and surface the **full** diff. Read every line. Validate it (build/lint/test as the repo defines). "Here is exactly what I will do, ×N." If the pilot diverges from intent or fails validation, **STOP — do not fan out.** Mandatory for agentic recipes; default-on for deterministic ones. `--no-pilot` is an explicit opt-out, noted in the report.
4. **FAN-OUT** — apply to each confirmed target _in isolation_: fresh branch (deterministic name) cut from the target's default branch, apply recipe, run the per-target second pass, compare the target's diff shape against the pilot and flag divergence, secrets-scan the staged diff, then commit and open a **draft PR** following the conventions confirmed at pilot. One target failing never aborts the rest.
5. **REPORT** _(reality-check #3 — reconcile, don't declare victory)_ — aggregate target → status (applied / already-compliant / skipped-not-applicable / failed) → PR URL → notes. Reconcile the arithmetic: `selected = applied + already-compliant + skipped-not-applicable + failed`, with nothing silently dropped. Only `applied` targets have a PR; an `already-compliant` no-op has none.
6. **REMEDIATE** — re-run on the failed/skipped subset. Campaigns are idempotent, so re-running a succeeded target is a no-op.

Full per-stage mechanics — enumeration commands, isolation model, validation, PR templating, aggregation format, idempotency rules, remediation, and rate-limit handling — are in `references/pipeline.md`.

## Check yourself, Claude

Before fanning anything out, prove the campaign to yourself. You are about to repeat one decision ×N, so an error here multiplies.

- **Did I understand the intent, or pattern-match?** Restate it in your own words and get the user's confirmation. What you replicate ×N must be what they asked for.
- **Is the target list right, both ways?** Open two or three _included_ targets and confirm the signal is really there (no false positives); reason about what is _missing_ — a target that uses the thing under a different name or path (no false negatives).
- **Is the recipe idempotent?** Re-running it on an already-changed target must be a clean no-op, or the campaign cannot be safely remediated. Fix that first.
- **Is the change destructive?** Deleting or rewriting requires a reference-check pre-step — is the thing being removed depended on elsewhere (a required check, a referenced file)? See `references/safety-and-self-checks.md`.
- **Is the blast radius bounded?** Respect `max_targets_per_run` (default 10) — larger fleets chunk; never fan out unbounded. Scope each sub-agent to the tools it needs, and forbid `WebFetch`/`WebSearch` unless the recipe genuinely requires them.

If you cannot answer one of these, you are not ready to pilot. Say what is unresolved instead of proceeding on hope.

## Recipe types

The **recipe** is the unit of per-target work. Choose the least powerful one that does the job:

- **deterministic** — a script or direct edit makes the change (remove a file, deep-merge a config patch). Reproducible and reviewable as a plain diff. Prefer this whenever the change is mechanical.
- **agentic** — a scoped sub-agent makes the change per target, for work that needs judgment. Non-deterministic, so the pilot is mandatory and per-target validation is non-negotiable.

Fan out agentic recipes with the **Agent tool**: send one chunk's per-target calls in a single message so they run concurrently, capped at `max_targets_per_run`. Target general work at the `general-purpose` subagent type; route domain work to the matching named agent (`bitwarden-security-engineer:bitwarden-security-engineer` for security changes). Constrain each sub-agent to the minimum toolset and pass it only its single target.

## Teaming — top-to-bottom per target

Force Multiplier is the **cross-target** layer. Per-target intelligence lives in the sibling delivery skills, reusing their conventions:

- `Skill(perform-preflight)` — the quality gate before any commit.
- `Skill(committing-changes)` — the commit message format.
- `Skill(labeling-changes)` — the conventional type keyword that drives the `t:` label.
- `Skill(creating-pull-request)` — the draft-PR workflow, template, and `ai-review` label.

Of these, `creating-pull-request` is **interactive** — it prompts per PR, which you cannot answer dozens of times. Resolve it at **PILOT**: walk it once to lock the title format, body template, and labels, then replicate that confirmed pattern non-interactively across the fan-out as draft PRs.

## Safety defaults (non-negotiable unless explicitly overridden)

- Every change is made on a fresh feature branch cut from the target's default branch. Never commit on, or push to, a default branch; never force-push.
- Draft PRs by default. Never auto-merge.
- Respect `max_targets_per_run` (default 10); larger fan-outs chunk or require confirmation.
- Destructive recipes require a reference-check pre-step before they run.
- Secrets-scan the staged diff before every commit.
- Reuse the existing `gh` auth; never inject credentials or commit secrets.
- `--dry-run` does everything except push and open PRs.

Full detail is in `references/safety-and-self-checks.md`.
