# Renders the classifier's result as the evaluation-mode PR comment described in the README.
# Input: the result JSON, or null when the agent printed none.
# Args:  $teams    team check from the workflow: {token, checks: [{owner, name, resolved, permission, status}]}
#        $repo     owner/name of the pull request's repository
#        $pr       pull request number, as a string
#        $head     head SHA the context was built from
#        $version  plugin version
#        $run_url  link to the workflow run

# Agent text is escaped so it cannot add HTML, mentions, links, or table cells.
def safe:
  tostring
  | gsub("&"; "&amp;") | gsub("<"; "&lt;") | gsub(">"; "&gt;")
  | gsub("@"; "@​") | gsub("\\["; "\\[") | gsub("\\]"; "\\]") | gsub("\\|"; "\\|")
  | gsub("://"; ":\u200b//")
  | gsub("[\r\n]+"; " ");

def count($noun): "\(.) \($noun)\(if . == 1 then "" else "s" end)";

def valid_path: type == "string" and test("^[A-Za-z0-9._@+/-]+$") and (startswith("-") | not) and (contains("..") | not);
def valid_owner: type == "string" and test("^@[A-Za-z0-9-]+(/[A-Za-z0-9._-]+)?$");
def code_path: if valid_path then "`\(.)`" else "(invalid path)" end;
def code_owner: if valid_owner then "`\(.)`" else "(unrecognized owner)" end;

def kind_name:
  {
    "fix": "Fix", "pattern-following": "Pattern-following", "debt-extending": "Debt-extending",
    "pattern-breaking": "Pattern-breaking", "special-case": "Special case", "structural": "Structural",
    "api-additive": "API-additive", "api-breaking": "API-breaking"
  }[. // ""] // "No kind";

def team_name($owner):
  ([$teams.checks[]? | select(.owner == $owner and .resolved == true) | .name] | first) as $n
  | if $n != null then "\($n | safe) (\($owner | code_owner))" else ($owner | code_owner) end;

def owner_label: if length == 0 then "Unowned" else map(team_name(.)) | join(", ") end;

def evidence_links:
  [.evidence[]? | select((.file | valid_path) and (.line | type == "number") and .line > 0)
   | "[\(.file | split("/") | last):\(.line)](https://github.com/\($repo)/blob/\($head)/\(.file)#L\(.line))"]
  | if length > 0 then " (" + join(", ") + ")" else "" end;

def why:
  (.change_kind | kind_name) as $k
  | (if .rule then "\"\(.rule | safe)\"" else null end) as $rule
  | {
      "change-trigger": "\($k). Matches a change trigger in the module's intent: \($rule)",
      "intent-conflict": "\($k). Conflicts with the module's intent: \($rule)",
      "do-not-need": "\($k). Listed in the module's \"do not need\" entries: \($rule)",
      "kind-default": "\($k). The kind's default applies.",
      "ambiguous": "\($k). The evidence did not settle the kind, so the more serious kind applies.",
      "unreadable-path": "The file path could not be read safely.",
      "malformed-intent": "The module's INTENT.md could not be parsed."
    }[.signal // ""] // "\($k). Unrecognized signal.";

def feedback:
  "<details><summary>Was this classification right?</summary>\n\n"
  + "- [ ] Correct\n"
  + "- [ ] Didn't need us: this was routine for our module\n"
  + "- [ ] Should have needed us: we'd want to see this kind of change\n\n"
  + "</details>";

def files_block: "<details><summary>\(.files | length | count("file"))</summary>\n\n" + ([.files[] | "- " + code_path] | join("\n")) + "\n\n</details>";

def required_entry:
  "**Why:** \(why)\(evidence_links)\n\n"
  + (if .explanation then "\(.explanation | safe)\n\n" else "" end)
  + (if .next_step then "**For the author:** \(.next_step | safe)\n\n" else "" end)
  + (if (.review_focus | length) > 0 then "**For the reviewer, check:**\n\n" + ([.review_focus[] | "- " + safe] | join("\n")) + "\n\n" else "" end)
  + files_block;

def routine_entry: "\(.change_kind | kind_name): \(.reason | safe)\n\n" + files_block;

def team_check_section:
  if $teams.token != "ok" then
    "### Reviewer request check\n\nThe workflow could not get a GitHub App token with organization Members read access, so it could not check whether the App can request these teams. Requesting team reviewers needs that permission."
  elif ($teams.checks | length) == 0 then ""
  else
    "### Reviewer request check\n\nWhether the workflow's GitHub App can resolve each owner and whether the owner has access to this repository. Nothing was requested.\n\n"
    + "| Owner | App can resolve | Repository permission | Status |\n| --- | --- | --- | --- |\n"
    + ([$teams.checks[] | "| \(.owner | code_owner) | \(if .resolved == true then "yes" elif .resolved == false then "no" else "not checked" end) | \(.permission // "none") | \(.status | safe) |"] | join("\n"))
  end;

def footer($result):
  "<sub>bitwarden-owning-team-review \($version | safe)"
  + (if $result then ", base `\($result.base_sha[0:7])`, head `\($head[0:7])`" else "" end)
  + ". [Run log](\($run_url)).</sub>";

def valid_result:
  type == "object" and .schema == 1 and (.result | IN("owning-team-review", "any-engineer", "no-verdict"))
  and .head_sha == $head and (.pr | tostring) == $pr and (.entries | type == "array")
  and (.base_sha | type == "string" and test("^[0-9a-f]{40}$"));

def banner: "## Owning-team review\n\n> [!NOTE]\n> Evaluation mode, owning-team review is still required by CODEOWNERS. This comment does not block the merge or request reviewers.";

if valid_result | not then
  [banner,
   "**No verdict.** The classifier did not return a usable result for this head commit, so every owning team stays required.",
   team_check_section,
   footer(null)] | map(select(. != "")) | join("\n\n")
else
  . as $result
  | [.entries[] | .owners |= (if type == "array" then sort else [] end)] as $entries
  | ($entries | map(select(.required and (.owners | length) > 0)) | group_by(.owners)) as $needed
  | ($entries | map(select(.required and (.owners | length) == 0))) as $unowned
  | ($entries | map(select(.required | not)) | group_by(.owners)) as $routine
  | [banner,
     (if .result == "no-verdict" then
        "**No verdict.** The classifier stopped early, so every owning team stays required."
      elif ($needed | length) > 0 then
        "This PR needs review from **\($needed | length | count("team"))**: \([$needed[] | .[0].owners | owner_label] | join("; "))."
      else
        "No owning team is needed. Any engineer can approve this PR."
      end),
     ($needed[] | "---\n\n### \(.[0].owners | owner_label): needed\n\n" + (map(required_entry) | join("\n\n")) + "\n\n" + feedback),
     (if ($unowned | length) > 0 then
        "---\n\n### Unowned files\n\nNo CODEOWNERS entry covers these files on the base or head commit, so no team can be required.\n\n"
        + ($unowned | map(required_entry) | join("\n\n"))
      else empty end),
     ($routine[] | "<details><summary>Any engineer: \(map(.files | length) | add | count("file")) owned by \(.[0].owners | owner_label)</summary>\n\n"
        + (map(routine_entry) | join("\n\n")) + "\n\n" + feedback + "\n\n</details>"),
     (if ((.notes // []) | length) > 0 then "<details><summary>Classifier notes</summary>\n\n" + ([.notes[] | "- " + safe] | join("\n")) + "\n\n</details>" else empty end),
     team_check_section,
     footer($result)]
  | map(select(. != "")) | join("\n\n")
end
