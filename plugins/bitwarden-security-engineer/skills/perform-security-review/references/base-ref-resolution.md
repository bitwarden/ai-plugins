# Why Base-Ref Resolution Looks Like That

Background for sub-step A2 of `perform-security-review`. The procedure itself lives in
`SKILL.md`; this file explains why each gate is there, so the steps can stay short.

## Never key on the output of `git rev-parse`

`git rev-parse --abbrev-ref origin/HEAD` exits 128 when `origin/HEAD` is unset — and still
prints the literal string `origin/HEAD` on stdout, with the `fatal:` going to stderr. A check
that captures the output and looks for something ref-shaped therefore succeeds on failure,
and hands the rest of the run a base ref that resolves to nothing. The exit status is the
only reliable signal.

## Keep the `origin/` prefix

`origin/main` and `main` are different refs. `main` is whatever the local branch last pointed
at, which on a machine that has not pulled in a week is not the base anyone means. Stripping
the prefix silently reviews against stale history.

## Why `origin/HEAD` is not enough on its own

`refs/remotes/origin/HEAD` is a convenience symbolic ref, and plenty of checkouts never
create it. `actions/checkout` is the common case: it does `git init`, adds the remote, and
fetches a single ref pattern that creates `refs/remotes/origin/<branch>` without ever writing
`origin/HEAD`. So the repository's default branch has to be asked for by name as a second
candidate.

Naming it is not the same as having it. A default `actions/checkout` fetches one refspec at
`fetch-depth: 1`, so on a feature-branch build `refs/remotes/origin/main` is absent too, and
candidate 2 fails check 2 in exactly the environment it was added for. Passing
`--base-ref origin/main` fails the same check for the same reason. Branch comparison mode
needs the base ref to be present locally, which in CI means `fetch-depth: 0` on the checkout
step, or an explicit `git fetch origin <base>` before the review runs. Without one of those
the run reaches the abort — which is the designed outcome, not a silent wrong answer, but the
abort has to name the prerequisite or the caller cannot act on it.

## Why a resolving ref is still not enough

`git rev-parse --verify` proves a ref name resolves to an object. It does not prove that
object shares history with `HEAD`. In a shallow clone the boundary can cut above the point
where the two branches diverged, leaving a ref that resolves and a `git merge-base` that
fails.

That distinction has teeth, because of how the diff is written:

```bash
git diff <base-ref>...HEAD > /tmp/security-review-<identifier>.diff
```

The shell performs the redirection **before** running the command, so the file is created and
truncated whatever happens next. A three-dot diff with no merge base exits 128 having written
nothing, which leaves a zero-byte file that looks exactly like "no changes found". Four agents
then review it and report clean. The `merge-base` gate exists so a resolvable-but-disconnected
candidate falls through to the next candidate instead of reaching that state, and step 1B's
exit-status and emptiness checks exist to catch it if it does anyway.

A non-zero exit can also leave a _partially_ written diff, so step 1B clears the file's contents with `Write` on any
failure rather than assuming it is empty. The step 1-A2 abort never creates one.

## Why not a two-dot diff

`git diff <base>..HEAD` compares two endpoints, so commits that exist only on the base show up
as reversed changes — deletions of code nobody deleted. Feeding that to security agents
manufactures findings. Three-dot is the only correct form here, which is why an absent merge
base is a stop rather than something to work around.

## Why not repair the clone

Deepening or un-shallowing someone's working copy is a side effect a review skill has no
business having, and `git fetch` writes to `.git`. When no candidate passes, the right move is
to stop and point the caller at PR mode, which gets a correct merge-base diff from the API
without touching the local repository at all.

## Validating a branch name the user typed

`git check-ref-format --branch` is a ref-validity check, not a shell-safety check. It rejects
whitespace and `~ ^ : ? * [ \`, but accepts `;`, `&`, `|`, `$`, backticks, and parentheses,
all of which are legal in a ref name. Double-quoting does not help either: parameter expansion
and command substitution both happen inside double quotes, so `"main$(...)"` runs the
substitution and then passes validation, because what is left after expansion is just `main`.

An allowlist applied before the value reaches any command is the strongest control available
here, and it is the control for this value: no `allowed-tools` rule can constrain a ref name
that has already been interpolated into a command, which is why the check has to run before the
value is placed. `tool-grants.md` covers the separate question of why the grants themselves are
written the way they are.
`^[A-Za-z0-9_][A-Za-z0-9._/-]*$` covers every branch name in normal use and admits none of the
above. The leading character is pinned separately because a value beginning `-` is read as an
option rather than a ref, and `--local-env-vars` is a legal branch name that a pattern allowing
`-` anywhere would accept.
