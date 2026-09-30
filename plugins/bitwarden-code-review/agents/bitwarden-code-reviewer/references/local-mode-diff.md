# Why Local Mode Looks Like That

Background for the local-mode bullet in `AGENT.md`. The procedure lives there; this file holds
the reasoning, so the agent's system prompt stays short on a path that never runs in PR mode.

## Pass `origin/HEAD` to git, never a resolved name

Nothing is interpolated, so a repository whose default branch is named something like
`main$(id)` cannot turn the base ref into a shell payload. Resolving it to a name first would
put attacker-influenceable text into a command string for no gain. `origin/HEAD` also resolves
to the remote's default branch, so it never compares against a stale local `main`.

## An empty diff is a failure, not a clean result

A three-dot diff compares commits and ignores the working tree, so it exits 0 and prints
nothing whenever the branch is level with `origin/HEAD` — which is exactly the state of a
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

## Why this path has no second candidate

`perform-security-review` probes further before aborting, and this agent cannot mirror it: the
probes there run `git rev-parse --verify`, `git merge-base`, and a REST call for the default
branch. None is available: an agent's `tools:` entries are matched as permission rules, so a
command outside the listed set is denied, and this agent grants none of those three. One candidate
would be reachable without any new grant — `git diff origin/main...HEAD` is already inside
`Bash(git diff:*)` — but it hardcodes a branch name this agent otherwise avoids, which is the
whole reason local mode uses `origin/HEAD`. Adding it would trade a clean abort for a wrong
base on any repository whose default branch is not `main`.
