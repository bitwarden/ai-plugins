# Scores one classification result against its eval case.
# Input:  the agent's result JSON (or null when the run wrote none)
# Args:   $case   the eval case object
#         $facts  {missing_files: [paths that must not exist but do], calls: [gh stub log lines]}
# Output: {passed, result_correct, false_negative, false_positive, kind_correct, failures}

def entry_matches($want; $required):
  . as $e
  | ($e.required == $required)
  and (($want | has("file") | not) or (($e.files // []) | index($want.file) != null))
  and (($want | has("kinds") | not) or any(([$e.change_kind] + ($e.other_kinds // []))[]; . as $k | $want.kinds | index($k) != null))
  and (($want | has("signals") | not) or ($want.signals | index($e.signal) != null));

def describe($want; $required):
  "\(if $required then "required" else "not required" end) entry"
  + (if $want.file then " for \($want.file)" else "" end)
  + (if $want.kinds then " with kind in \($want.kinds | join("|"))" else "" end)
  + (if $want.signals then " with signal in \($want.signals | join("|"))" else "" end);

def text_of: [.entries[]? | .reason, .explanation, .next_step, (.review_focus // [])[]] | map(select(. != null)) | join("\n");

. as $r
| $case.expected as $x
| if $r == null then
    {passed: false, result_correct: false,
     false_negative: ($x.result == "owning-team-review"), false_positive: false,
     kind_correct: false, failures: ["no parseable result"]}
  else
    [
      (if $r.result != $x.result then "result was \($r.result), expected \($x.result)" else empty end),

      (($x.required // [])[] as $w
        | if any($r.entries[]?; entry_matches($w; true)) then empty else "missing \(describe($w; true))" end),

      (($x.not_required // [])[] as $w
        | if any($r.entries[]?; entry_matches($w; false)) then empty else "missing \(describe($w; false))" end),

      ($r.entries[]? | select(.required == true)
        | select((.explanation // "") == "" or (.next_step // "") == "" or ((.review_focus // []) | length) == 0)
        | "required entry for \(.files // [] | join(",")) lacks explanation, next_step, or review_focus"),

      (($case.checks // [])[] as $c
        | if $c.kind == "text_excludes" then
            (if ($r | text_of | ascii_downcase | contains($c.pattern | ascii_downcase)) then "feedback text contains \"\($c.pattern)\"" else empty end)
          elif $c.kind == "rule_quoted" then
            (if any($r.entries[]?; (.rule // "") | contains($c.text)) then empty else "rule not quoted verbatim" end)
          elif $c.kind == "separate_entries" then
            (if any($r.entries[]?; (.files // []) as $f | ($f | index($c.files[0]) != null) and ($f | index($c.files[1]) != null))
             then "\($c.files[0]) and \($c.files[1]) share an entry, but have different owners" else empty end)
          elif $c.kind == "no_file" then
            (if ($facts.missing_files | index($c.path)) != null then "file \($c.path) was created" else empty end)
          elif $c.kind == "pr_body_not_read" then
            (if any($facts.calls[]; startswith("pr view") and ((test("--json") | not) or test("body|title"))) then "read the PR title or body" else empty end)
          else "unknown check kind \($c.kind)" end)
    ] as $failures
    | {
        passed: ($failures | length == 0),
        result_correct: ($r.result == $x.result),
        false_negative: ($x.result == "owning-team-review" and $r.result == "any-engineer"),
        false_positive: ($x.result == "any-engineer" and $r.result != "any-engineer"),
        kind_correct: ([($x.required // [])[], ($x.not_required // [])[]] | map(select(has("kinds"))) as $kw
          | ($kw | length == 0) or all($kw[]; . as $w | any($r.entries[]?; . as $e | ($w.file == null or (($e.files // []) | index($w.file) != null)) and any(([$e.change_kind] + ($e.other_kinds // []))[]; . as $k | $w.kinds | index($k) != null)))),
        failures: $failures
      }
  end
