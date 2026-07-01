# Campaign Spec

A campaign is the compiled, structured form of a generic intent. The user speaks a sentence; the skill turns it into this spec, echoes it back for confirmation, and executes _the spec_ — never the loose sentence. The spec is what makes the pilot, idempotency, chunking, and reporting possible.

This file defines the schema only. It is deliberately abstract — no named change appears here. For fully-worked instances, read `../examples/`.

## Fields

### `intent`

One sentence, in the user's words, restated and confirmed. This is the single source of truth for what every target should end up with. If the pilot diff does something the intent does not describe, the recipe — not the intent — is wrong.

### `scope`

`multi-repo` or `monorepo`.

- `multi-repo` — targets are repositories in the Bitwarden enterprise. Each target is cloned and changed in isolation; each yields its own branch and PR.
- `monorepo` — targets are projects/packages/workspaces inside one repository. The fan-out happens across paths in a single clone; the campaign yields one branch and PR per project, or one grouped PR, as the PR spec dictates.

### `target_selector`

How candidates are enumerated and filtered. Two parts:

- `enumerate` — the command(s) that list all candidate targets (repos in the org, or project paths in the monorepo).
- `applicability_filter` — the _signal_ that marks a candidate as relevant, plus how it is detected. A candidate that lacks the signal is `skipped-not-applicable`, never `failed`.

Both are built from the patterns in `finding-targets.md`. The selector resolves to an explicit, finite list that is shown to the user before anything is touched.

### `recipe`

The per-target unit of work. Has a `type` and the work itself:

- `type` — `deterministic` | `agentic` (see SKILL.md → Recipe types).
- `body` — for deterministic: the exact edit/script and its parameters. For agentic: the scoped sub-agent prompt and its tool allowlist.
- `idempotency` — the condition under which the recipe is already satisfied and must no-op. Required. Without it the campaign cannot be safely remediated or re-run.

### `validation`

The per-target gate that must pass before a commit is made. Defined by what the target's own repo specifies (its CLAUDE.md build/lint/test commands) plus `Skill(perform-preflight)`. A target whose validation fails is recorded as `failed` and left without a PR.

### `pr_spec`

The shape of the change as it is delivered. Confirmed once on the pilot, then replicated:

- `branch` — a deterministic branch name template (same input → same branch, so re-runs are no-ops).
- `title` — follows `Skill(committing-changes)` / `Skill(labeling-changes)` format (`[TICKET] <type>: <summary>`), so CI applies the right `t:` label.
- `body` — fills the target repo's `.github/PULL_REQUEST_TEMPLATE.md` per `Skill(creating-pull-request)`.
- `labels` — the `ai-review` choice and any others, confirmed at pilot.
- `draft` — `true` by default.

### `safety_policy`

The guardrails for this campaign. Defaults live in `safety-and-self-checks.md`; the spec records any deviations explicitly:

- `max_targets_per_run` — default 10.
- `destructive` — whether the recipe removes/rewrites; if true, a reference-check pre-step is required.
- `dry_run` — if true, do everything except push and open PRs.
- `pilot` — `required` by default; `--no-pilot` flips it and is logged.

## Abstract instance

A spec is illustrated here with placeholders only — `<…>` marks where a real campaign substitutes its specifics.

```yaml
intent: "<one-sentence restatement, confirmed by the user>"
scope: multi-repo # or monorepo
target_selector:
  enumerate: "<command listing all candidates in the bitwarden org>"
  applicability_filter:
    signal: "<the thing whose presence makes a target relevant>"
    detect: "<command/probe that returns true when the signal is present>"
recipe:
  type: deterministic # or agentic
  body: "<the exact edit/script, or the scoped sub-agent prompt>"
  idempotency: "<condition under which the target is already done → no-op>"
validation: "<repo-defined build/lint/test> + Skill(perform-preflight)"
pr_spec:
  branch: "<deterministic-branch-name-template>"
  title: "[<TICKET>] <type>: <summary>"
  body: "<filled from the target repo's PR template>"
  labels: ["<ai-review choice>"]
  draft: true
safety_policy:
  max_targets_per_run: 10
  destructive: false
  dry_run: false
  pilot: required
```
