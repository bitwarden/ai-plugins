# Why the Tool Grants Look Like That

Background for the `allowed-tools` block and step 1-C of `perform-security-review`. The
operative rules are in `SKILL.md`; this file holds the reasoning.

## A `*` in a Bash rule absorbs whole flags

This is the fact everything below rests on, and it is easy to get wrong. A rule containing `*`
is compiled to an anchored regular expression with each `*` replaced by `.*` under the `s` flag.
`.*` therefore spans spaces, quotes, and entire arguments — it does not stop at a path
separator, a word boundary, or a closing quote.

So a rule cannot pin "this argument is the endpoint and nothing else may follow." Wherever a
`*` appears, an attacker-influenced command can insert flags into it and satisfy the literal
part of the pattern from inside a later argument.

Concretely, this rule looks endpoint-scoped and is not:

```
Bash(gh api --method GET -H "X-GitHub-Api-Version: 2026-03-10" "repos/*/*/code-scanning/alerts?*)
```

It compiles to:

```
^gh api --method GET -H "X-GitHub-Api-Version: 2026-03-10" "repos/.*/.*/code-scanning/alerts\?.*$
```

and matches all of these:

| command                                                                                            | effect              |
| -------------------------------------------------------------------------------------------------- | ------------------- |
| `gh api --method GET -H "…" "repos/O/R/code-scanning/alerts?state=open" --jq '.[]'`                | intended            |
| `gh api --method GET -H "…" "repos/O/R" -X DELETE --jq '"/code-scanning/alerts?y"'`                | `DELETE /repos/O/R` |
| `gh api --method GET -H "…" "repos/O/R" --method DELETE --template '{{.}}/code-scanning/alerts?z'` | `DELETE /repos/O/R` |

The second `*` swallows `R" -X DELETE --jq '"`, and the required literal
`code-scanning/alerts?` is satisfied inside the `--jq` program. `gh` resolves `--method` and
`-X` last-wins, so the request that goes out is a `DELETE` — and `DELETE /repos/{owner}/{repo}`
deletes the repository.

## So `gh api` is not granted at all

There is no `gh api` rule in `allowed-tools`. No pattern could be written that constrains the
verb, and this skill's entire input is a diff an attacker may have influenced, so a rule the
model is merely asked to follow is not a control. Step 1-C's two `gh api` scan-evidence calls
(secret scanning and Dependabot) therefore prompt, and in CI they are denied. Step 1-C's Aikido
call does not go through `gh api`; see "Why the Aikido MCP grant is pre-approved" below.

That is a real capability loss: GHAS evidence is unavailable on the unattended path unless the
deployment grants it. **The control at that level is the token, not a permission rule** — run
the workflow with a read-only `GH_TOKEN` and minimal `permissions:`, and the destructive verb
is unavailable no matter what command is composed. A deployment that has done that can add its
own narrow allow rules with the residual risk understood.

Step 1-C is written to degrade rather than fail: each scanner records its own outcome, and for
the two `gh api` scanners a denial is recorded as `Not checked (permission denied)` so it never
reads as `None`, which would say the scanner ran and found nothing. Aikido cannot reach that
state — its grant is pre-approved, so the call never prompts and is never denied.

## Why the Aikido MCP grant is pre-approved

`mcp__plugin_aikido_aikido-mcp__aikido_issues_list` is granted outright, which looks
inconsistent with refusing every `gh api` rule. The reason it is safe is tool scoping, not the
absence of a wildcard.

The Aikido MCP server exposes four tools: `aikido_full_scan` and `aikido_issues_list` (both
read-only), `aikido_login` (auth), and `aikido_ignore_issue` — a **mutation** that dismisses a
finding from the feed given an `issue_id` and a reason. Only `aikido_issues_list` is granted, so
`aikido_ignore_issue` is not reachable. That is the whole argument, and it is why this grant
**must stay an exact tool name and never become a wildcard**: `mcp__plugin_aikido_aikido-mcp__*`
would pre-approve `aikido_ignore_issue` as well, and this skill's input is an attacker-influenced
diff — a run steered that way could silently dismiss a real security finding.

Flag absorption, the concern that killed the `gh api` rules, does not apply within the granted
tool: an MCP call's arguments are structured parameters validated by the server, not a matched
shell string, so there is no `.*` for an inserted flag to hijack and no last-wins verb to flip.
But that is a footnote next to the scoping point above — naming one read tool and no others is
what makes the grant safe.

The residual risk the grant does carry: `aikido_issues_list` returns third-party content
(finding titles, descriptions) into a context that also holds `Write`, and on the step-1-C
unattended path it runs without a prompt. That is the same exposure the diff itself already
carries, so it adds no new class of risk — and it is why steps 2 and 4 are handed pre-fetched
evidence instead of the tool.

## Why the default-branch lookup does not use `gh api`

The endpoint that answers it is `repos/{owner}/{repo}`, whose `DELETE` deletes the repository,
so candidate 2 uses `gh repo view --json defaultBranchRef` instead. `gh repo view` has no
`--method` or `-X` flag at all, so the last-wins problem cannot arise. This is the general
shape of the fix: prefer a subcommand that cannot express the dangerous operation over a rule
that tries to forbid it.

## Why the `rm` grant went too

`Bash(rm -f /tmp/security-review-*)` was kept at first on the reasoning that a cleanup step
is lower stakes than an API call. That reasoning was wrong in the same way the `gh api` rules
were: the `.*` absorbs flags, not just path characters, so
`rm -f /tmp/security-review-x -rf <any-path>` matches the rule and is a recursive tree delete. The identifiers are chosen per run, so no literal rule can enumerate
them. The grant is gone. Step 7 clears the diff with the granted `Write` tool instead, which is
the better answer anyway: it removes the content without needing a shell at all, and it runs
unattended. The file stays on disk, empty.

## Why the `git` grants stay

`Bash(git diff:*)` and `Bash(git log:*)` both accept `--output=<file>`, verified, so a prefix
rule over either is an arbitrary-file-write primitive. They are kept anyway, and the reason is
specific rather than general: this skill already holds `Write`, so the capability adds nothing
an attacker-steered run could not already do. Removing them would cost the skill its diff and
leave the exposure unchanged. That argument does **not** extend to a grant whose flag reaches a
capability the skill lacks — which is exactly why `gh api` and `rm` went.

`Bash(git branch --show-current:*)` is not in the same class. `git branch --show-current -D <br>`
is a usage error and deletes nothing, so the prefix does not admit branch deletion.

Every future grant here should be reasoned about the same way: by what an inserted flag can do
inside each `*`, never by how specific the pattern looks.
