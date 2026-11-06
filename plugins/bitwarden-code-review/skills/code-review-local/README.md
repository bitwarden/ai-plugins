# `/code-review-local` - Local Code Review Skill

Reviews a GitHub pull request or your local git changes with the `bitwarden-code-reviewer` agent and writes the review to local files instead of posting it. Use it to preview a review before it goes on a pull request, to review a branch that has no pull request yet, or to feed a review into your own tooling.

## Usage

```bash
/code-review-local [PR# | PR URL | --base <ref>] [--output-dir <path>]
```

- **`PR#` or `PR URL`**: the pull request to review, by number or full URL
- **`--base <ref>`**: for local changes only, the ref the branch is diffed against instead of `origin/HEAD`. Use the remote-tracking form (`origin/rc`): a bare `rc` needs a local branch of that name, which can sit behind the remote. Dropped with a pull request target, where GitHub's recorded base is used. The ref must match `^[A-Za-z0-9][A-Za-z0-9._/-]*$`
- **`--output-dir <path>`**: directory for the review files. Defaults to `${CLAUDE_PLUGIN_DATA}/code-reviews/`
- **No arguments**: the command asks whether to review a pull request or the local changes

Only the space-separated forms are accepted. `--base=rc`, `--output-dir=foo`, or a flag with no value is refused before the review starts.

## Examples

```bash
# A pull request, by number or URL
/code-review-local 123
/code-review-local https://github.com/bitwarden/mobile/pull/4567

# Local changes: choose "local changes" when asked
/code-review-local

# A branch cut from a release branch
/code-review-local --base origin/rc

# Somewhere other than the default directory
/code-review-local 123 --output-dir /tmp/reviews
```

For local changes the agent reviews one scope, not both: the branch against its base when it has commits ahead of that base, otherwise your pending changes (tracked edits plus untracked source files). To review uncommitted edits on a branch that is already ahead of its base, commit them first and re-run. The summary names the scope and the base it used. A `--base` ref that does not resolve produces a No Verdict rather than a review of some other scope.

## Output files

The agent, not this command, decides where the files go and what they are called; the command only passes `--output-dir` through. The [agent flow diagrams](../../docs/code-review-agent-flows.md) show the rule.

| Target        | Files                                                                                                              |
| ------------- | ------------------------------------------------------------------------------------------------------------------ |
| Pull request  | `code-review-local-PR-<n>-summary.md`, `code-review-local-PR-<n>-inline-comments.md`                               |
| Local changes | `code-review-local-<branch>-<YYYY-MM-DD>-summary.md`, `code-review-local-<branch>-<YYYY-MM-DD>-inline-comments.md` |

Both land in `${CLAUDE_PLUGIN_DATA}/code-reviews/`, or in `--output-dir` when given, and the command prints the full path of each. Writes under `~/.claude/` ask for approval, so headless runs (`claude -p`) need `--output-dir` set to an allowed directory.

**Summary file.** The summary comment, in the format `posting-review-summary` posts to GitHub:

```markdown
## 🤖 Bitwarden Claude Code Review

**Overall Assessment:** APPROVE / REQUEST CHANGES

[Up to 4 neutral sentences describing what was reviewed]

<details>
<summary>Code Review Details</summary>

- ❌ : [One-line description]
  - `filename.ts:42`

</details>
```

When nothing could be reviewed it carries the `NO VERDICT` form instead, with the reason in place of the assessment sentences.

**Inline-comments file.** Every inline comment the agent would have posted, with file and line references. Empty when there are none.

```markdown
## [file-path]:[line-number]

[Emoji] **[SEVERITY]**: [One-line description]

<details>
<summary>Details and fix</summary>

[Full details, code examples, rationale]

</details>

---
```

### Posting a reviewed draft

```bash
/code-review-local 123 --output-dir /tmp/reviews
cat /tmp/reviews/code-review-local-PR-123-summary.md
gh pr comment 123 --body-file /tmp/reviews/code-review-local-PR-123-summary.md
```

## Requirements

- GitHub CLI (`gh`) installed and authenticated, for pull request targets
- The `bitwarden-code-review` plugin installed

## Related documentation

- [Bitwarden Code Review Plugin README](../../README.md)
- [Bitwarden Code Reviewer Agent](../../agents/bitwarden-code-reviewer/AGENT.md)
- [Code review agent flows](../../docs/code-review-agent-flows.md)
