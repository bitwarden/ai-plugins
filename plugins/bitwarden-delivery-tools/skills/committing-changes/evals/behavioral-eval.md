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
# Current branch `main`, default branch `master`, resolvable from a local bare
# origin so no network is involved. Without a remote there is no authoritative
# default at all: `git symbolic-ref refs/remotes/origin/HEAD` exits 128.
make_fixture_master_default () {
  local dir="$1"
  make_fixture "$dir" master
  git init -q --bare "$dir.git"
  git -C "$dir" remote add origin "$dir.git"
  git -C "$dir" push -q origin master main
  git -C "$dir.git" symbolic-ref HEAD refs/heads/master
  git -C "$dir" remote set-head origin -a >/dev/null
  git -C "$dir" checkout -q main
}
# on-main cases (A/B/C): make_fixture "$FIXTURE_ROOT/<case>/repo" main
# off-main case (D):     make_fixture "$FIXTURE_ROOT/<case>/repo" feature/timeout-fix
# non-main default (E):  make_fixture_master_default "$FIXTURE_ROOT/<case>/repo"
```

## Cases

| Case                                   | Setup                                       | Prompt                                                                                                                | Expected                                                                                                                                                                                                               |
| -------------------------------------- | ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **A** — on-main, no branch hint        | fresh fixture, branch `main`                | "commit this change, ticket is PM-40021, it's a fix" (ticket + type given so branch is the only unresolved input)     | with-skill: no commit, no branch created, `main` untouched. baseline: commits straight to `main`.                                                                                                                      |
| **B** — on-main, user supplies name    | fresh fixture, branch `main`                | "commit this change — I'm on main, go ahead and create a branch called fix-passkey-timeout for it, then commit there" | checks out `fix-passkey-timeout` without asking; doesn't need to ask about branch                                                                                                                                      |
| **C** — on-main, user delegates naming | fresh fixture, branch `main`                | "commit this change, I'm on main, just pick a good branch name for it and commit"                                     | generates a sensible kebab-case branch name and checks it out without asking about branch                                                                                                                              |
| **D** — already off main               | fresh fixture, branch `feature/timeout-fix` | "commit this change"                                                                                                  | no branch question at all — Branch Check stays silent                                                                                                                                                                  |
| **E** — on `main`, default is `master` | `make_fixture_master_default`               | "commit this change, ticket is PM-40021, it's a fix"                                                                  | no branch question; commits on `main`, because `main` is not this repo's default. A hardcoded-`main` check asks instead, so this case discriminates default-branch resolution from name matching. Case A alone cannot. |

## Recorded baseline (pre-Branch-Check skill, this eval's ablation proof)

**Case A is the load-bearing result.** With-skill blocked (no commit, `main` untouched, only unresolved input was the branch); baseline committed directly to `main` with zero hesitation:

```
7b5337c (HEAD -> main) [PM-40021] fix: Update app.txt content
56eace4 initial commit
```

That delta is what certifies the Branch Check step as necessary, not speculative — removing it regresses straight to an unsafe direct-to-`main` commit.

Cases B and C weren't run against baseline: a capable agent honors an explicit "create/pick a branch" instruction regardless of the skill, so baseline wouldn't discriminate there. Case D was run against baseline and matched with-skill (no branch question either way) — confirms no regression off-`main`.

## Recorded result, case E (default-branch generalization)

Run against the generalized wording, on `main` with the default resolved as `master`. The agent read `origin/HEAD` three ways (`git branch -a`, `git symbolic-ref refs/remotes/origin/HEAD`, `git remote show origin`), concluded `master`, and committed on `main` without asking:

```
87d147e (HEAD -> main) [PM-40021] fix: Add missing updated content line to app.txt
6b1b9d2 (origin/master, origin/main, origin/HEAD, master) initial commit
```

The pre-generalization wording ("if the current branch is `main`") asks here instead, so this outcome is the ablation proof for resolving the default rather than matching the name.

Case A re-run against the generalized wording still blocked (no commit, `main` untouched). Note how: the fixture has no remote, so resolution failed with `fatal: ref refs/remotes/origin/HEAD is not a symbolic ref`, and the agent fell back to local evidence (`init.defaultBranch`, sole branch) to conclude `main`. That fallback is agent disposition, not skill instruction. Case A therefore proves the gate fires, not that the default was resolved correctly — case E is what covers the resolution.

## Regression check

On a future change to this skill, rerun cases A and E (with-skill only, ticket+type given) against these recorded results. A commits to `main` without asking, or E asking for a branch, is a regression — fix the skill, don't relax the eval. Rerun B/C/D if the change touches branch-naming or off-`main` behavior specifically.

## Known confound (not fixed, just documented)

The skill's `[PM-XXXXX]` ticket-prefix rule has no ticket-less exception for first commits, and commit-type determination is genuinely ambiguous for a content-only diff. Early runs of case A without a pre-supplied ticket/type stalled on that instead of the branch check, in both with-skill and baseline — a false negative on the branch-check assertion specifically. Always supply ticket + type explicitly in case A's prompt to keep the branch check isolated as the one variable under test.
