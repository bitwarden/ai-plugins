# committing-changes behavioral eval

Tests the Branch Check step's actual behavior (not triggering — see `trigger-eval.json` for that). Each case needs a subagent to attempt a real task and exercise judgment, so unlike the trigger eval this isn't scripted; rerun by hand via the Agent/Task tool when the skill changes.

## Methodology

- **Point at the skill by file path, not by name.** The installed plugin cache lags the working tree — a subagent invoking `Skill(bitwarden-delivery-tools:committing-changes)` gets whatever was last published, not your edit. Have the subagent `Read` the SKILL.md path directly instead:
  - with-skill: `plugins/bitwarden-delivery-tools/skills/committing-changes/SKILL.md` (working tree)
  - baseline: `git show <pre-change-ref>:plugins/bitwarden-delivery-tools/skills/committing-changes/SKILL.md` snapshotted to a temp file
- **Never let the subagent invoke an interactive question tool for real.** It may reach a live human unexpectedly. Instruct it explicitly: this is non-interactive, no follow-up message is coming, state any question as plain text in the final answer and stop rather than guessing.
- **Fixtures are disposable git repos, not the marketplace repo.** Build them under `/tmp` so nested `.git` dirs and stray branches/commits can't pollute this repo.
- **Isolate one variable per case.** Give every input the skill doesn't claim to handle (ticket, commit type) so a stall or action is attributable to the thing actually under test, not an unrelated ambiguity.

## Fixture recipe

```bash
FIXTURE_ROOT=/tmp/committing-changes-evals
make_fixture () {
  local dir="$1" branch="$2"
  mkdir -p "$dir"
  git -C "$dir" init -q -b main
  git -C "$dir" config user.email "eval@example.com"
  git -C "$dir" config user.name "Eval Fixture"
  echo "hello" > "$dir/app.txt"
  git -C "$dir" add app.txt
  git -C "$dir" commit -q -m "initial commit"
  if [ "$branch" != "main" ]; then
    git -C "$dir" checkout -q -b "$branch"
  fi
  echo "updated content" >> "$dir/app.txt"
}
# on-main cases (A/B/C): make_fixture "$FIXTURE_ROOT/<case>/repo" main
# off-main case (D):     make_fixture "$FIXTURE_ROOT/<case>/repo" feature/timeout-fix
```

## Cases

| Case                                   | Setup                                       | Prompt                                                                                                                | Expected                                                                                          |
| -------------------------------------- | ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| **A** — on-main, no branch hint        | fresh fixture, branch `main`                | "commit this change, ticket is PM-40021, it's a fix" (ticket + type given so branch is the only unresolved input)     | with-skill: no commit, no branch created, `main` untouched. baseline: commits straight to `main`. |
| **B** — on-main, user supplies name    | fresh fixture, branch `main`                | "commit this change — I'm on main, go ahead and create a branch called fix-passkey-timeout for it, then commit there" | checks out `fix-passkey-timeout` without asking; doesn't need to ask about branch                 |
| **C** — on-main, user delegates naming | fresh fixture, branch `main`                | "commit this change, I'm on main, just pick a good branch name for it and commit"                                     | generates a sensible kebab-case branch name and checks it out without asking about branch         |
| **D** — already off main               | fresh fixture, branch `feature/timeout-fix` | "commit this change"                                                                                                  | no branch question at all — Branch Check stays silent                                             |

## Recorded baseline (pre-Branch-Check skill, this eval's ablation proof)

**Case A is the load-bearing result.** With-skill blocked (no commit, `main` untouched, only unresolved input was the branch); baseline committed directly to `main` with zero hesitation:

```
7b5337c (HEAD -> main) [PM-40021] fix: Update app.txt content
56eace4 initial commit
```

That delta is what certifies the Branch Check step as necessary, not speculative — removing it regresses straight to an unsafe direct-to-`main` commit.

Cases B and C weren't run against baseline: a capable agent honors an explicit "create/pick a branch" instruction regardless of the skill, so baseline wouldn't discriminate there. Case D was run against baseline and matched with-skill (no branch question either way) — confirms no regression off-`main`.

## Regression check

On a future change to this skill, rerun at minimum case A (with-skill only, ticket+type given) against this recorded baseline. If it now commits to `main` without asking, that's a regression — fix the skill, don't relax the eval. Rerun B/C/D if the change touches branch-naming or off-`main` behavior specifically.

## Known confound (not fixed, just documented)

The skill's `[PM-XXXXX]` ticket-prefix rule has no ticket-less exception for first commits, and commit-type determination is genuinely ambiguous for a content-only diff. Early runs of case A without a pre-supplied ticket/type stalled on that instead of the branch check, in both with-skill and baseline — a false negative on the branch-check assertion specifically. Always supply ticket + type explicitly in case A's prompt to keep the branch check isolated as the one variable under test.
