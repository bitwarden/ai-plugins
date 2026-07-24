---
name: assessing-jira-issue-relevance
description: Use when the user provides a single Jira issue key and asks whether it is still relevant, still applicable, still pending, still a bug, has been fixed, or can be closed. Trigger phrases include "Is [TICKET] still relevant?", "Is this still an issue?", "Is PM-123 still pending?", "Has this been fixed?", "Can we close this?", "Is this ticket still valid?", "Is this still applicable?", "Does this bug still exist?". Fetches the ticket and verifies the described problem against the current codebase to return a verdict with evidence. This skill assesses a single ticket at a time; invoke it iteratively for multiple tickets.
allowed-tools: Read, Grep, Glob, AskUserQuestion, Bash(git log:*), Bash(git -C * log:*), Bash(git -C * rev-parse:*), Bash(git clone:*), mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_remote_links, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page
---

# Assessing a Jira Issue for Relevance

Determine whether a Jira issue still applies to the current codebase. Fetch the ticket, locate the specific code path it describes, compare current behavior against the ticket's description, and return a verdict with evidence.

## Workflow

### Step 1: Fetch the Ticket and Its Context

Use `get_issue` with `expand: ["renderedFields", "names"]`. Extract:

- **The specific problem or task**: Read beyond the summary. The description, acceptance criteria, and replication steps are more precise. For bugs: what is the actual broken behavior and what is expected? For tasks: what specific code change is required?
- **Technical identifiers**: Method names, class names, file paths, API endpoint routes, UI strings that appear in source, config keys, feature flag names — anything named in the ticket that can be searched in code. Note these explicitly before moving on.
- **Filed date**: Used to scope `git log` searches.
- **Repo scope evidence**: Gather what the ticket says about where the code lives, and note how strong that evidence is. Do not settle on a repo here — Step 2 decides.
  - _Strong_: a literal repo name, a `github.com/bitwarden/<repo>` URL, or a linked PR/commit.
  - _Weaker_: team field, component labels, language or platform keywords, file paths in the description.

Also note these **staleness signals** from the ticket fields before moving on:

- **Age**: How many months since the ticket was filed?
- **Priority and assignee**: Is it Low/Lowest priority? Unassigned?
- **Parent epic**: Does the ticket have a parent epic? If so, fetch it (`get_issue`) and check whether all other child tickets are resolved. A lone surviving task in an otherwise-completed epic is a strong signal that the work may have been intentionally deferred or forgotten — not that it's still needed.

After fetching the ticket, always do both of the following:

**Fetch issue comments** (`get_issue_comments`): Comments often contain decisions that never made it back into the description — root cause findings, "we decided not to fix this", priority calls, or pointers to where the fix landed. Read them before building search targets.

**Fetch linked issues** (`get_issue_remote_links` and the `issuelinks` field): Look specifically for blocking relationships — issues this ticket blocks or is blocked by. A ticket blocked by unresolved work may not be actionable yet; a blocker that has since been resolved may mean this ticket is now ready. Fetch (`get_issue`) any directly linked issues to check their current status and extract additional technical context. Do not traverse more than one level deep.

### Step 2: Establish Repo Scope

Settle which repositories are in scope and confirm they are readable **before** searching anything. Do not begin Step 3 until all three checks below pass.

Bitwarden has many repositories — `clients`, `server`, `sdk-internal`, `sdk-sm`, `android`, `ios`, `mcp-server`, and others. Treat the candidate set as open; never assume a ticket must belong to one of the repos you have seen before.

**1. Determine the repos.**

If the ticket carries strong evidence (a literal repo name, a `github.com/bitwarden/<repo>` URL, or a linked PR/commit), use it and move on.

Otherwise, infer the most likely repo(s) from the weaker signals and **present that inference for confirmation** with `AskUserQuestion`. State what you inferred and the signal it rests on, offer the plausible alternatives you considered, and allow multiple selections — tickets legitimately span repos. Never search a repo the user has not confirmed.

**2. Resolve each repo to a path.**

Use the current working directory if it is that repo; otherwise look for a sibling directory of the same name; otherwise ask for the path. Confirm each resolved path is a real checkout:

```
git -C <path> rev-parse --show-toplevel
```

**3. Verify the repo is cloned, and stop if it is not.**

If a repo in scope has no checkout on disk, ask whether to clone it. On approval, clone it and continue.

**If the user declines to clone, stop immediately.** Return no verdict. State which repo was unavailable and that the assessment could not be completed. This halt applies even when other repos in scope are present — do not assess the available half and do not downgrade to a weaker verdict. Searching a repo that is not on disk returns no matches, which is indistinguishable from the code having been removed; proceeding would produce a confident "No longer relevant" on a ticket that is still live.

This halt is distinct from the **Cannot determine** verdict in Step 5. "Cannot determine" means the ticket was too vague to trace. This means the evidence was never accessible.

### Step 3: Build Search Targets

From the ticket, identify 2–5 specific identifiers to search for in code. Prioritize:

- Method or function names mentioned in the ticket (e.g., `ValidateLegacyMigrationAsync`, `unlockViaBiometrics`, `validateCanManagePermission`)
- Class or component names (e.g., `BaseRequestValidator`, `LockComponent`, `CollectionDialog`)
- API route strings (e.g., `"trial/send-verification-email"`, `"verify-email-token"`)
- UI strings that appear in source or i18n JSON (e.g., `"managePermissionRequired"`)
- Config or feature flag keys (e.g., `DenyLegacyUserMinimumVersion`)

If the ticket names no specific identifiers, derive them from the described behavior: what function would implement this, what component would render this UI, what endpoint would serve this request?

### Step 4: Search the Code

Run searches in the repo(s) confirmed in Step 2.

First, **orient yourself in each repo**: read its `CLAUDE.md` and `README` to find the source roots, module layout, and test locations. Do this rather than relying on remembered directory names — layouts differ per repo and change over time.

Then:

1. **Grep for each identifier** in the relevant source directories. Don't stop at confirming existence — read the surrounding code to understand current behavior. A symbol that still exists but now behaves differently may mean the bug is already fixed.

2. **Read the actual implementation** at each match. The grep result shows where; the file content shows what it currently does. Confirm whether the behavior the ticket describes is still present, partially changed, or gone.

3. **Check git history on affected files** since the ticket was filed:

   ```
   git log --oneline --since="<filed-date>" -- <file-path>
   ```

   Look for commits that might have silently addressed the issue — refactors, renames, feature flag removals, component rewrites. If a commit looks relevant, read its diff on the affected lines.

4. **Trace refactored paths**: If a named symbol no longer exists, find what replaced it. A deleted method does not mean the bug is fixed — the logic may have moved. Search for the behavior, not just the original name.

### Step 5: Deliver Verdict

Compare what the ticket describes against what the code does today. Reach a conclusion.

**Verdict options**:

- **Still relevant** — The described problem exists unchanged in the current code. Show the specific `file:line` that proves it.
- **Partially addressed** — Some part of the described problem was fixed, but a gap remains. State precisely what was fixed and what remains open, with evidence for each.
- **No longer relevant** — The problem no longer exists. Explain what changed and cite the current code or commit that proves it. Note whether the ticket is safe to close.
- **Technically relevant, but question whether still needed** — The gap exists in code, but staleness signals are strong enough that the work should be confirmed with the reporter or PM before picking it up. Use this when multiple signals combine: ticket is significantly old (> ~9 months), unassigned, low priority, and/or is the lone surviving task in an otherwise-completed epic. State the code evidence and the staleness signals separately so the reader can weigh both.
- **Cannot determine** — The ticket description is too vague to trace to specific code, and `git log` provides no signal. State what you searched and why it was inconclusive. Only use this after exhausting the search targets.

**Format**: Lead with the verdict and its justification in plain prose. Cite `file:line` references as evidence. If still relevant, state what specifically remains to be done — do not just restate the ticket. If staleness signals are present even for a "Still relevant" verdict, note them at the end: ticket age, epic completion state, priority, and assignee. Keep it tight; a verdict paragraph with supporting evidence is sufficient.

## What NOT to Do

- Don't traverse linked issues more than one level — fetch directly linked issues (blocks, is blocked by, parent epic) but do not follow their links further
- Don't skip the parent epic check for task tickets — one extra `get_issue` call often changes the recommendation from "build this" to "confirm whether this is still wanted"
- Don't read Confluence pages unless the ticket has no description and a Confluence link is the only available context
- Don't return "cannot determine" without first checking both the named symbols AND `git log` on the relevant files
- Don't treat "symbol still exists" as "bug still present" — read the current behavior, not just the name
- Don't restate the ticket description as the verdict — the verdict must reflect what the code says today

## Examples

### examples/relevance_assessment_workflow.md

Four worked examples: a bug where the described code path was silently refactored away, a task whose implementation gap is confirmed present, a spike made obsolete by later work, and a ticket whose repo is not cloned locally, where the skill halts without a verdict.
