# owning-team-classifier evals

`classification-eval.json` holds 23 synthetic pull requests. Each case covers one change kind, one signal, or one security guard, and states the result the classifier must reach. The eval measures whether the classifier sends each change to the right reviewer, and whether it names the right kind.

## Corpus

`fixtures/setup.sh` builds every case from the same base repository. Four modules have an `INTENT.md`, and one has none:

| Module              | Owner in `CODEOWNERS`          | What the `INTENT.md` says                                                                                              |
| ------------------- | ------------------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| `libs/platform/`    | `@bitwarden/team-platform-dev` | Sync never hides failures, `getSync` is deprecated, no feature dependencies, a sync trigger, and "do not need" entries |
| `libs/vault/`       | `@bitwarden/team-vault-dev`    | A filtering trigger                                                                                                    |
| `libs/test-utils/`  | `@bitwarden/team-platform-dev` | An exception that lets any engineer approve `api-additive` changes                                                     |
| `src/Core/Billing/` | `@bitwarden/team-billing-dev`  | A pricing trigger, and a commands-and-queries pattern                                                                  |
| `apps/tools/`       | none                           | No `INTENT.md`, so the global policy applies                                                                           |

Each case applies one change on a branch and commits it. The repository is left checked out at the base commit, as a `pull_request_target` checkout is.

| ID  | Fixture                             | Covers                                                   | Expected     |
| --- | ----------------------------------- | -------------------------------------------------------- | ------------ |
| 1   | `fix-off-by-one`                    | `fix`                                                    | any engineer |
| 2   | `pattern-following-key-definition`  | `pattern-following`                                      | any engineer |
| 3   | `debt-extending-deprecated`         | `debt-extending`, deprecated symbol                      | owning team  |
| 4   | `debt-extending-ts-ignore`          | `debt-extending`, suppressed check                       | owning team  |
| 5   | `pattern-breaking-local-cache`      | `pattern-breaking`                                       | owning team  |
| 6   | `special-case-client-type`          | `special-case` that looks like a fix                     | owning team  |
| 7   | `structural-feature-import`         | `structural`, platform depends on a feature              | owning team  |
| 8   | `cross-owner-move`                  | `structural`, file moved across a module boundary        | owning team  |
| 9   | `api-additive-export`               | `api-additive`                                           | owning team  |
| 10  | `api-breaking-rename`               | `api-breaking`, renamed public method                    | owning team  |
| 11  | `api-breaking-default-timeout`      | `api-breaking`, behavior change with no signature change | owning team  |
| 12  | `change-trigger-sync-interval`      | `change-trigger`, quoted verbatim                        | owning team  |
| 13  | `do-not-need-test-only`             | `do-not-need`                                            | any engineer |
| 14  | `domain-critical-path`              | domain critical path left to the ruleset                 | any engineer |
| 15  | `no-intent-global-defaults`         | no `INTENT.md`, so the global policy applies             | any engineer |
| 16  | `intent-change-loosening`           | the base `INTENT.md` judges a PR that loosens it         | owning team  |
| 17  | `kind-override-test-utils`          | a module's override of a kind default                    | any engineer |
| 18  | `mixed-routine-and-export`          | a mixed PR, with the routine part reported               | owning team  |
| 19  | `injection-in-diff`                 | contributor content that addresses the classifier        | owning team  |
| 20  | `unsafe-path`                       | file names with shell syntax                             | owning team  |
| 21  | `server-new-endpoint`               | `api-additive` in .NET                                   | owning team  |
| 22  | `server-fix-null`                   | `fix` in .NET                                            | any engineer |
| 23  | `intent-conflict-swallowed-failure` | `intent-conflict` with no mechanical indicator           | owning team  |

## Real pull requests

`real-pr-eval.json` holds 14 squash-merged `bitwarden/clients` pull requests and one open one from authors outside Platform that changed Platform-owned code between 2026-05-01 and 2026-10-31. These cases are harder than the synthetic ones: the diffs are real, they mix files and concerns, and several look routine.

The real repository has no `INTENT.md` files yet. `fixtures/setup-real.sh` replays each pull request on a base that carries a draft Platform `INTENT.md`:

1. Check out the merge commit's parent.
2. Copy `fixtures/intent/clients/platform.md` to `INTENT.md` in every Platform-owned directory, and commit. This commit is the fixture's base.
3. Apply the pull request's diff and commit. This commit is the fixture's head. A merged case takes its base and diff from the squash-merge commit. An open case names `base_sha` and `head_sha`.

The draft Platform intent states the boundary "platform code does not carry behavior that exists for one feature," a migration trigger, and "do not need" entries for new `StateDefinition` entries, comment-only changes, and test-only changes. Every other module gets the global policy.

Expected results fail shut, as the classifier does. A behavior change counts as a fix only when the base commit shows the old behavior was wrong, so cases 110 and 111 expect the owning team even though both PRs fix bugs. That over-flagging is accepted: it costs one extra review, never a missed one.

Each expected result is a hand label that follows `change-kinds.md` and the draft intent, not a record of what Platform's reviewers did. Each case also records `platform_review`. Seven owner-required cases were approved by Platform without comment. These cases show where the rules ask for more review than Platform gave in practice, which is calibration data for the intent and not a classifier error.

| ID  | PR                                                        | Covers                                                                        | Expected     | Platform's review                    |
| --- | --------------------------------------------------------- | ----------------------------------------------------------------------------- | ------------ | ------------------------------------ |
| 101 | [#23046](https://github.com/bitwarden/clients/pull/23046) | `special-case`: Send-only, flag-gated retry in the shared full sync           | owning team  | Approved, pending an SDK bump        |
| 102 | [#20235](https://github.com/bitwarden/clients/pull/20235) | `api-additive`: new options on an exported routing helper                     | owning team  | Asked for the use case               |
| 103 | [#23088](https://github.com/bitwarden/clients/pull/23088) | `api-additive`: new server setting, response mapping, and getter              | owning team  | Caught an inverted default           |
| 104 | [#20637](https://github.com/bitwarden/clients/pull/20637) | `special-case`: flag branch for one logout reason, copying an existing branch | owning team  | Approved without comment             |
| 105 | [#23445](https://github.com/bitwarden/clients/pull/23445) | `api-breaking`: `getFeatureFlag$` stops re-emitting unchanged values          | owning team  | Approved without comment             |
| 106 | [#20793](https://github.com/bitwarden/clients/pull/20793) | `api-additive`: new public getter inside a race fix                           | owning team  | Approved without comment             |
| 107 | [#24204](https://github.com/bitwarden/clients/pull/24204) | `structural`: platform imports an Admin Console mapper                        | owning team  | Approved without comment             |
| 108 | [#21189](https://github.com/bitwarden/clients/pull/21189) | `api-breaking`: removed constructor dependencies and changed behavior         | owning team  | Approved without comment             |
| 109 | [#23955](https://github.com/bitwarden/clients/pull/23955) | shape change: a read cache in CLI storage                                     | owning team  | Approved with design discussion      |
| 110 | [#22929](https://github.com/bitwarden/clients/pull/22929) | fail shut: sync-state change a base test asserted against                     | owning team  | Approved, deferring to Admin Console |
| 111 | [#22477](https://github.com/bitwarden/clients/pull/22477) | fail shut: exported URL guard accepts more input                              | owning team  | Approved                             |
| 112 | [#20182](https://github.com/bitwarden/clients/pull/20182) | `api-breaking`: a persisted key moves to a new storage location               | owning team  | Approved without comment             |
| 113 | [#23090](https://github.com/bitwarden/clients/pull/23090) | `api-breaking`: mark and measure drop out of non-dev builds                   | owning team  | Approved without comment             |
| 114 | [#22754](https://github.com/bitwarden/clients/pull/22754) | comment-only change                                                           | any engineer | Approved without comment             |
| 115 | [#24340](https://github.com/bitwarden/clients/pull/24340) | a new Platform library, plus swaps to it in other teams' code                 | owning team  | Open                                 |

Run the set with `EVAL_SET=real-pr-eval.json` and `CLONES_DIR` set to a directory holding a `clients` clone. Each fixture is a shared clone of about 120 MB.

## Scoring

`score.jq` checks each result deterministically. There is no grader model.

- **Result.** `result` matches the expected value.
- **Entries.** Each expected entry exists: required or not, for the named file, with an acceptable kind or signal. A kind matches when it is the entry's `change_kind` or is in its `other_kinds`.
- **Feedback.** Every required entry has an `explanation`, a `next_step`, and at least one `review_focus` item.
- **Checks.** Some cases add assertions:
  - `no_file`: a file a malicious path would create does not exist.
  - `text_excludes`: the feedback text does not repeat injected text.
  - `rule_quoted`: the trigger or intent statement is quoted verbatim in `rule`.
  - `pr_body_not_read`: no `gh pr view` call asked for the title or body.

A run passes when every check passes. `aggregate.sh` reports the pass rate, result accuracy, kind accuracy, and cost, and counts **false negatives** separately: cases where the classifier said any engineer and the owning team was needed. A false negative is the expensive mistake, so a change must never add one.

A run that ended in an API error is left out of every rate, so a crash never counts as a miss.

## Running

Needs `claude`, `git`, `jq`, and `python3`. Runs never reach GitHub: `fixtures/gh-stub/gh` serves the canned pull request and rejects everything else.

```bash
export OUT_DIR=$(mktemp -d)
runs() { for id in $(jq -r '.evals[].id' classification-eval.json); do for r in 1 2 3; do echo "$id $r"; done; done; }
runs | xargs -P 3 -L 1 ./run-eval.sh
runs | xargs -L 1 ./score.sh
./aggregate.sh > result.json
```

`MODEL` overrides the model, which defaults to `opus`.

## Permissions

A fixture is untrusted input, as a real pull request is. Each run calls `scripts/prepare-context.sh` the way a real caller does, with the `gh` stub first on `PATH`, then runs the agent with `--permission-mode dontAsk` and only `Read`, `Grep`, and `Glob`. `Read` is scoped to the context directory and the plugin's own files. The agent has no shell and no write tool, so the run captures its printed result from the transcript. Runs load only `local` settings, and refuse a fixture that carries `.claude/settings.local.json`.

## Regression gate

A change to the agent, `change-kinds.md`, or `intent-format.md` must not add a false negative, and must not lower result accuracy. Run all cases three times and compare with the baseline. When a change is intentional, record the new baseline in this file in the same pull request.

## Baseline (2026-11-01, agent 0.1.0, Opus, three runs per case)

| Set       | Cases | Runs | Pass rate | False negatives | False positives | Cost  |
| --------- | ----- | ---- | --------- | --------------- | --------------- | ----- |
| Synthetic | 23    | 69   | 69 / 69   | 0               | 0               | $8.12 |
| Real PRs  | 15    | 45   | 45 / 45   | 0               | 0               | $9.17 |

Every case passed all three runs, with the agent limited to `Read`, `Grep`, and `Glob` on a prepared context. Cases 2, 18, and 112 accept `api-additive` as well as `pattern-following`, because a new definition that a barrel file re-exports meets the new-export indicator. The "do not need" entry decides both cases in every run.

On real cases 101, 104, and 107, the classifier decided on `intent-conflict` and quoted the draft Platform boundary: platform code does not carry behavior that exists for one feature.

Each run took 20 to 60 seconds and cost $0.06 to $0.35.

Read the baseline with two caveats:

- **The labels fail shut.** Real cases 110 and 111 fix bugs, but nothing on their base commits shows the old behavior was wrong, so the expected result is the owning team. Synthetic case 22 carries an interface comment that documents the corrected behavior, which is what lets it count as a fix.
- **The intent overlay is a draft.** The real-PR results measure the classifier against a draft Platform `INTENT.md`, not intent Platform has agreed to.

For an `unreadable-path` entry, the agent leaves `files` empty instead of repeating the unsafe name. The enforcing workflow matches those files to their owner from its own file list.

## Adding a case

Every confirmed miss from the feedback loop becomes a case. Add the change to the `change` function in `fixtures/setup.sh`, then add the case to `classification-eval.json` with the expected result, and the kinds or signals that are acceptable. Prefer a fixture that has one right answer. A case that a careful reviewer could classify two ways measures the fixture, not the classifier.
