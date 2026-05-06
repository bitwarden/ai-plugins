---
name: triaging-jira-issues
description: Use when the user provides a single Jira issue key and asks whether it is still relevant, still applicable, still pending, still a bug, has been fixed, or can be closed. Trigger phrases include "Is [TICKET] still relevant?", "Is this still an issue?", "Is PM-123 still pending?", "Has this been fixed?", "Can we close this?", "Is this ticket still valid?", "Is this still applicable?", "Does this bug still exist?". Fetches the ticket and verifies the described problem against the current codebase to return a verdict with evidence. For bulk triage of multiple tickets or a JQL filter, use the bulk-triaging-jira-issues skill instead.
---

# Triaging a Jira Issue for Relevance

Determine whether a Jira issue still applies to the current codebase. Fetch the ticket, locate the specific code path it describes, compare current behavior against the ticket's description, and return a verdict with evidence.

This skill is distinct from `researching-jira-issues`. That skill synthesizes context to *understand* a ticket. This skill verifies whether the described problem or task still exists in code — the answer should be a clear verdict, not a summary.

## Workflow

### Step 1: Fetch the Ticket and Its Context

Use `get_issue` with `expand: ["renderedFields", "names"]`. Extract:

- **The specific problem or task**: Read beyond the summary. The description, acceptance criteria, and replication steps are more precise. For bugs: what is the actual broken behavior and what is expected? For tasks: what specific code change is required?
- **Technical identifiers**: Method names, class names, file paths, API endpoint routes, UI strings that appear in source, config keys, feature flag names — anything named in the ticket that can be searched in code. Note these explicitly before moving on.
- **Filed date**: Used to scope `git log` searches.
- **Repo scope signal**: Determine whether this applies to `clients`, `server`, `sdk-internal`, or a combination. Use the team field, component labels, and description content (see Scope Notes below).

Also note these **staleness signals** from the ticket fields before moving on:

- **Age**: How many months since the ticket was filed?
- **Priority and assignee**: Is it Low/Lowest priority? Unassigned?
- **Parent epic**: Does the ticket have a parent epic? If so, fetch it (`get_issue`) and check whether all other child tickets are resolved. A lone surviving task in an otherwise-completed epic is a strong signal that the work may have been intentionally deferred or forgotten — not that it's still needed.

After fetching the ticket, always do both of the following:

**Fetch issue comments** (`get_issue_comments`): Comments often contain decisions that never made it back into the description — root cause findings, "we decided not to fix this", priority calls, or pointers to where the fix landed. Read them before building search targets.

**Fetch linked issues** (`get_issue_remote_links` and the `issuelinks` field): Look specifically for blocking relationships — issues this ticket blocks or is blocked by. A ticket blocked by unresolved work may not be actionable yet; a blocker that has since been resolved may mean this ticket is now ready. Fetch (`get_issue`) any directly linked issues to check their current status and extract additional technical context. Do not traverse more than one level deep.

### Step 2: Build Search Targets

From the ticket, identify 2–5 specific identifiers to search for in code. Prioritize:

- Method or function names mentioned in the ticket (e.g., `ValidateLegacyMigrationAsync`, `unlockViaBiometrics`, `validateCanManagePermission`)
- Class or component names (e.g., `BaseRequestValidator`, `LockComponent`, `CollectionDialog`)
- API route strings (e.g., `"trial/send-verification-email"`, `"verify-email-token"`)
- UI strings that appear in source or i18n JSON (e.g., `"managePermissionRequired"`)
- Config or feature flag keys (e.g., `DenyLegacyUserMinimumVersion`)

If the ticket names no specific identifiers, derive them from the described behavior: what function would implement this, what component would render this UI, what endpoint would serve this request?

### Step 3: Search the Code

Run searches in the relevant repo(s):

1. **Grep for each identifier** in the relevant source directories. Don't stop at confirming existence — read the surrounding code to understand current behavior. A symbol that still exists but now behaves differently may mean the bug is already fixed.

2. **Read the actual implementation** at each match. The grep result shows where; the file content shows what it currently does. Confirm whether the behavior the ticket describes is still present, partially changed, or gone.

3. **Check git history on affected files** since the ticket was filed:
   ```
   git log --oneline --since="<filed-date>" -- <file-path>
   ```
   Look for commits that might have silently addressed the issue — refactors, renames, feature flag removals, component rewrites. If a commit looks relevant, read its diff on the affected lines.

4. **Trace refactored paths**: If a named symbol no longer exists, find what replaced it. A deleted method does not mean the bug is fixed — the logic may have moved. Search for the behavior, not just the original name.

### Step 4: Deliver Verdict

Compare what the ticket describes against what the code does today. Reach a conclusion.

**Verdict options**:

- **Still relevant** — The described problem exists unchanged in the current code. Show the specific `file:line` that proves it.
- **Partially addressed** — Some part of the described problem was fixed, but a gap remains. State precisely what was fixed and what remains open, with evidence for each.
- **No longer relevant** — The problem no longer exists. Explain what changed and cite the current code or commit that proves it. Note whether the ticket is safe to close.
- **Technically relevant, but question whether still needed** — The gap exists in code, but staleness signals are strong enough that the work should be confirmed with the reporter or PM before picking it up. Use this when multiple signals combine: ticket is significantly old (> ~9 months), unassigned, low priority, and/or is the lone surviving task in an otherwise-completed epic. State the code evidence and the staleness signals separately so the reader can weigh both.
- **Cannot determine** — The ticket description is too vague to trace to specific code, and `git log` provides no signal. State what you searched and why it was inconclusive. Only use this after exhausting the search targets.

**Format**: Lead with the verdict and its justification in plain prose. Cite `file:line` references as evidence. If still relevant, state what specifically remains to be done — do not just restate the ticket. If staleness signals are present even for a "Still relevant" verdict, note them at the end: ticket age, epic completion state, priority, and assignee. Keep it tight; a verdict paragraph with supporting evidence is sufficient.

## Scope Notes

Use these to determine which repo and directories to search:

**Server repo** (`server/src/`):
- Team field (including but not limited to): Billing, Auth (server-side), Admin Console (server-side)
- Keywords in description: C#, .NET, API endpoint, stored procedure, Stripe, webhook, IdentityServer, database
- Key directories: `src/Identity/IdentityServer/` (auth/token flow), `src/Core/Billing/` and `src/Identity/Billing/` (billing), `src/Core/Services/Implementations/` (user/org services), `src/Api/` (REST controllers)

**Clients repo** (`clients/`):
- Team field (including but not limited to): Key Management, Browser, Desktop, Admin Console (frontend), Vault
- Keywords in description: Angular, TypeScript, browser extension, desktop app, web vault, UI component, form
- Key directories: `apps/browser/src/` (extension), `apps/desktop/src/` (desktop), `apps/web/src/` (web vault), `libs/key-management-ui/src/lock/` (shared lock/unlock UI), `libs/key-management/src/` and `libs/auth/src/` (shared auth)

**SDK repo** (`sdk-internal/crates/`):
- Team field (including but not limited to): SDK, Platform
- Keywords in description: Rust, crate, SDK, FFI, bitwarden-crypto, bitwarden-auth, bitwarden-core
- Key crates: `bitwarden-crypto/` (encryption), `bitwarden-auth/` (authentication), `bitwarden-core/` (core types), `bitwarden-ffi/` (cross-platform bindings)

**Multiple repos**: Auth and key management tickets often span clients and server. Vault timeout, biometrics, and unlock flow bugs commonly touch both `clients` and `sdk-internal`. Start with the repo the team field suggests, then check the other if the first shows only half the picture.

## What NOT to Do

- Don't traverse linked issues more than one level — fetch directly linked issues (blocks, is blocked by, parent epic) but do not follow their links further
- Don't skip the parent epic check for task tickets — one extra `get_issue` call often changes the recommendation from "build this" to "confirm whether this is still wanted"
- Don't read Confluence pages unless the ticket has no description and a Confluence link is the only available context
- Don't return "cannot determine" without first checking both the named symbols AND `git log` on the relevant files
- Don't treat "symbol still exists" as "bug still present" — read the current behavior, not just the name
- Don't restate the ticket description as the verdict — the verdict must reflect what the code says today

## Examples

### examples/triage_workflow.md

Three worked examples: a bug where the described code path was silently refactored away, a task whose implementation gap is confirmed present, and a spike made obsolete by later work.
