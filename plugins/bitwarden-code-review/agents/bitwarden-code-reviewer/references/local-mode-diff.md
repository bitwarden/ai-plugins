# Why Local Mode Looks Like That

Background for the local-mode bullet in `AGENT.md`. The procedure lives there; this file holds
the reasoning, so the agent's system prompt stays short on a path that never runs in PR mode.

## Pass `origin/HEAD` to git, never a resolved name

On the default path nothing is interpolated, so a repository whose default branch is named
something like `main$(id)` cannot turn the base ref into a shell payload. Resolving it to a name
first would put attacker-influenceable text into a command string for no gain. `origin/HEAD` also
resolves to the remote's default branch, so it never compares against a stale local `main`.

A caller-supplied `BASE:` ref is the one exception, and the next section is what holds it.

## Why a caller can name the base, and what constrains it

`origin/HEAD` is the right default and the wrong answer on a branch cut from a release branch
such as `rc` or `hotfix-rc`. The three-dot diff takes the merge base with trunk, so every
already-merged commit the release branch carries lands in the review and the scope covers work
that is not in the change. `BASE:` exists for that case, and only that case: a pull request's
base is the one GitHub records and `gh pr diff` already uses it.

The default costs nothing at the shell, because `origin/HEAD` is a literal in the agent's own
text. A caller-supplied ref is not, so it is the one value on this path that reaches a command
string from outside. Two things hold it: the `^[A-Za-z0-9][A-Za-z0-9._/-]*$` pattern, and the
fact that it is checked on both sides of the delegation. The leading character class is the
load-bearing half — `Bash(git diff:*)` is a prefix rule, so it matches `git diff --output=… …`
just as readily as a ref, and a value beginning with `-` is handed to git as a flag. The rest of
the class keeps whitespace, shell metacharacters, and git's own `@{…}` revision syntax out.

The command turn checks it because it is the turn that reads `$ARGUMENTS`. The agent re-checks
it because the command turn is not its only caller — an agent reached directly, or through a
prompt someone else composed, gets the same control either way.

## Why the remote-tracking form is the one to recommend

`--base origin/rc` and `--base rc` both pass the pattern, and the docs and the abort advice
point at the first. Two reasons, and the second is the same one that picked `origin/HEAD` as the
default above.

A bare `rc` resolves only against `refs/heads/rc`, a local branch. The checkout that actually
hits this abort is the one that has no such branch: `actions/checkout`, or any clone where
someone ran `git checkout -b feat/x origin/rc` and never made a local `rc`. Telling that caller
to run `git fetch origin rc` does not help them, because a fetch writes `refs/remotes/origin/rc`
and leaves `refs/heads/rc` absent, so the next run aborts on the identical message. Interpolating
the supplied ref into the advice is worse when it is already `origin/rc`, since
`git fetch origin origin/rc` fails with `couldn't find remote ref`. That is why the advice names
the bare branch in the fetch and the remote-tracking ref in the re-run, rather than echoing back
whatever was supplied.

The second reason is staleness. When a bare `rc` does resolve, it resolves to a local branch that
can sit behind the remote, which is exactly the failure the first section gives for not resolving
`origin/HEAD` to a name. A review scoped against a stale base reports a verdict over the wrong
set of commits, quietly, which is the outcome this whole path is built to refuse.

## Why a `BASE:` that fails aborts instead of falling back

Two ways it fails, and both land on No Verdict.

A ref that fails the pattern is rejected before any command runs. A ref that passes it can still
fail to resolve — a release branch nobody fetched is the ordinary case — and `git diff` exits
non-zero. Neither computed the scope the caller named.

What makes the abort necessary is what the alternatives review instead. Falling back to
`origin/HEAD` is safe at the shell and wrong at the review: the caller named a base precisely
because the default resolves the wrong scope for them, so it reproduces the sweep-in this
parameter was added to prevent. Falling through to the pending-changes path is wrong the same
way and reads worse, because a dirty tree makes it succeed — the agent reviews uncommitted edits
and reports a verdict, and nothing in that verdict says the branch-against-`rc` comparison never
happened. Both produce a confident answer to a question nobody asked. Unknown scope is No
Verdict, the same as an unidentifiable pull request.

An empty result is the one outcome that is not a failure of the ref. The ref resolved; the
branch simply holds nothing ahead of it. That falls back like the default does.

## An empty diff is a failure, not a clean result

A three-dot diff compares commits and ignores the working tree, so it exits 0 and prints
nothing whenever the branch is level with its base — which is exactly the state of a
developer asking for their pending edits to be reviewed. Four agents reviewing an empty diff
report clean, and that verdict is worse than no verdict.

## Why `git status --porcelain` needs a read

`git diff HEAD` shows tracked edits and lists no untracked files, so a branch whose changes are
entirely new files produces an empty diff and is still reviewable. `git status --porcelain`
finds those files, but it emits status codes and paths — not content. Reporting a verdict over
a list of filenames is the same failure as reporting one over an empty diff, so the paths it
marks `??` have to actually be read.

`--untracked-files=all` is part of the command, not a refinement of it. In the default `--untracked-files=normal`
mode git reports a wholly untracked directory as one collapsed `?? some-new-dir/` entry rather
than the files inside it, and `Read` errors on a directory. Without the flag the all-new-files
case yields nothing readable, falls through to the abort, and tells the developer their base ref
is at fault while their new files sit unreviewed. The flag needs no new grant — `Bash(git status:*)`
already covers it.

## Why the untracked-file rule is about quoting, not filenames

Untracked files are by definition the ones no ignore rule has caught yet. On a CI runner that
includes whatever a setup or auth step wrote into the workspace moments earlier — a registry
token, a cloud credential file, a state file — none of which has an entry in `.gitignore`
because nobody anticipated it being there. So `git status` marks it `??` and the fallback reads
it as review input.

That matters because tag mode posts through the MCP comment tool onto a public pull request.
Local mode used to be a plain branch diff and had no path from the working tree to a public
comment at all; this fallback creates one.

A skip list is the obvious control and the wrong one. It fails open on every pattern nobody
thought of, and the failure is silent and public. The rule that holds regardless of filename is
the one in `AGENT.md`: never quote a line from an untracked file verbatim in a posted comment,
cite `path:line` and describe the defect instead. The glob list is kept as a convenience for the
shapes we can name, not as the thing being relied on.

## Why the abort routes through the skill

A subagent's returned text is posted nowhere. An abort that only returns text is therefore
silent, and leaves the workflow's placeholder comment looking like a review that found nothing.
`Skill(posting-review-summary)` owns the routing, and its first row is local mode keyed on the
caller's declaration — so the abort lands in `review-summary.md` in the working directory, the
same place a normal local review goes. Naming a destination here instead would risk writing a
file the active mode does not read, which is as silent as writing nothing.

## Why this path guesses no second candidate

A caller can name a base. The agent cannot pick one for itself, and the abort below is what it
does instead.

`perform-security-review` probes further before aborting, and this agent cannot mirror it: the
probes there run `git rev-parse --verify`, `git merge-base`, and a REST call for the default
branch. None is available: an agent's `tools:` entries are matched as permission rules, so a
command outside the listed set is denied, and this agent grants none of those three. One candidate
would be reachable without any new grant — `git diff origin/main...HEAD` is already inside
`Bash(git diff:*)` — but it hardcodes a branch name this agent otherwise avoids, which is the
whole reason local mode uses `origin/HEAD`. Adding it would trade a clean abort for a wrong
base on any repository whose default branch is not `main`. A guessed base and a caller-supplied
one are not the same thing: the caller knows which branch the work was cut from, and the abort
now tells them the parameter exists.
