---
name: writing-release-notes
description: Write user-facing release notes for a Bitwarden release from a Jira release tag and the #release Slack thread. Use when asked to "write release notes", "draft release notes", "generate release notes", "write app store notes", or any request to produce external-facing release copy for a given version.
allowed-tools: mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_issues, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_comments
---

# Writing Release Notes

Produce concise, user-facing release notes for a Bitwarden release. The output is what customers read — on GitHub, in the App Store, or in Google Play — so every word should be benefit-oriented, jargon-free, and accurate about what users will actually experience.

## Prerequisites

Automated Jira lookups require the `bitwarden-atlassian-tools` plugin (its MCP server exposes `search_issues`, `get_issue`, and `get_issue_comments`). Without it, or when running in a Claude.ai Project (MCP tools are unavailable there), fall back to asking the user to paste the release page content and the Slack thread text directly — the rest of this skill works identically either way. There is no Slack MCP integration in this marketplace; the Slack thread is always gathered by asking the user to paste it.

## Step 1: Gather Inputs

Gather two inputs before writing anything:

### 1a. Jira Release Page

Ask the user for the Jira release page URL (e.g. `https://bitwarden.atlassian.net/projects/CL/versions/12345/tab/release-report-all-issues`) or the release version name (e.g. `2025.7.0`).

If `search_issues` is available, resolve the query:

- From a URL, extract the numeric version ID (the segment after `/versions/`) and query by ID: `fixVersion = 12345 ORDER BY issuetype ASC`
- From a version name, quote it: `fixVersion = "2025.7.0" ORDER BY issuetype ASC`

Call `search_issues` with `fields: ["summary", "issuetype", "labels", "components", "status", "description"]`, and page through results using the returned `nextPageToken` until none is returned. For each issue, capture summary, issue type, labels, components, status, and any feature flag references found in the description. Feature flag references usually surface more completely in the Slack thread (Step 1b); only call `get_issue_comments` for individual issues where the flag is ambiguous after checking both sources.

If MCP tools are not available (web app context), ask the user to paste the release page content or a list of ticket summaries directly into the conversation.

### 1b. #release Slack Thread

The #release Slack thread is posted weekly and specifies which feature flags are toggled for the release. This is critical for two reasons:

- **Include**: Only user-facing changes whose feature flag is being enabled in this release (or that have no flag) should appear in the notes.
- **Flags enabled with no matching issue in this release**: A flag being enabled is almost always because the feature it guards is going generally available. Often all the engineering work behind that flag already shipped in earlier releases, so this release's Jira list may contain zero issues for it — the enablement itself, not any ticket in the current `fixVersion`, is the user-facing event. Never let "no matching issue in this release" be a reason to drop a flag that the thread lists as enabled; instead resolve what it guards (see Step 3) and write a bullet for it.
- **Server releases — flag removals**: When a feature flag is being fully removed from the server codebase, this signals that self-hosted users are gaining access to the feature. These must appear in the release notes.

Ask the user to paste the thread content.

Parse the thread to extract:

- Release version and date
- List of flags being **enabled** for this release (per platform if specified)
- List of flags being **removed** (for server releases — capture both the flag identifier and any associated feature description from the ticket or thread)
- Any PM or engineering notes about what to highlight or suppress

For every flag in the **enabled** list, check it against the issues gathered in Step 1a. If none of those issues reference the flag, do not assume there is nothing to report — flag this for the lookup described in Step 3 before writing the notes.

## Step 2: Determine Release Scope

Identify:

- **Which repo/product** is being released (clients, server, mobile, browser extension, CLI, desktop)
- **Which platforms** are covered (web app, desktop, browser extension, mobile iOS, mobile Android, CLI)
- **Release version** number

If the release covers multiple repos with separate release notes (e.g., clients and server each have their own GitHub release), confirm with the user whether they want notes for all or one.

## Step 3: Filter to User-Facing Changes

Go through every issue in the release and classify it. Only items that pass the filter appear as named bullet points.

### Include as a named bullet point

- New user-visible features or capabilities
- UI or UX changes users will notice
- Policy and admin setting changes (including new enforcement options)
- Performance improvements users will perceive
- Significant accessibility improvements
- New onboarding flows, product tours, or setup wizards
- Checkout, billing, or subscription flow changes
- Items whose feature flag is confirmed **enabled** in this release's Slack thread
- Flags confirmed **enabled** in the Slack thread even when no issue in this release's Jira list references them — resolve what the flag guards (see below) rather than skipping it

### Collapse into the catch-all line

- Internal refactors, code cleanup, or architecture changes with no user-visible effect
- Dependency upgrades with no user-visible change
- Test coverage additions
- Logging, telemetry, or analytics instrumentation
- Items behind a feature flag that is **not** being enabled in this release
- Minor copy or label tweaks not worth their own bullet
- Bug fixes that are too narrow or edge-case to be meaningful to most users

### Always include (never collapse) — server releases only

Feature flags that are **fully removed** from the server codebase in this release. Flag removal is the moment self-hosted users gain access to a feature. Write each removal as a user-facing line describing what the feature does — not the internal flag identifier. See Step 4 for format.

### Always include (never collapse) — flags enabled without a matching release issue

For every flag the Slack thread lists as **enabled**, check whether any issue gathered in Step 1a references it. If none do, the work behind the flag almost certainly shipped in an earlier release and is only now going live — this is still a reportable, user-facing event and must not be silently dropped just because it has no ticket in the current release.

Resolve what the flag guards, in this order:

1. Search Jira for the flag identifier as free text, without restricting to this release's `fixVersion` (e.g. `text ~ "flag-identifier" ORDER BY created ASC`), to find the ticket(s) that originally implemented the feature.
2. If a ticket is found, use its summary/description to write a plain-language, user-facing line about the feature going live.
3. If nothing turns up, ask the user for a one-line description of what the flag enables — do not guess or invent functionality.

Write the resulting line the same way any other named bullet is written (Step 4 format rules), and never include the flag identifier itself.

### Exclude entirely

- Security fixes, unless the Slack thread or the user explicitly approves specific wording for one (default to excluding all security fixes from named bullets)
- Internal tooling changes with zero user impact
- Duplicate or reverted changes

## Step 4: Write the Release Notes

### Format rules

- **Plain text only** — no markdown, no asterisks, no headers, no bullet characters
- One line per notable change
- Begin each line with a past-tense action verb: `Added`, `Updated`, `Fixed`, `Improved`, `Removed`
- Write from the **user's perspective** — what did they gain, lose, or notice?
- No Jira ticket numbers, no internal terminology, and critically: **no feature flag identifiers**
- Keep each line under ~12 words
- Aim for **3–7 notable bullet points** maximum, followed by one catch-all line
- End with: `Various under-the-hood improvements and minor bug fixes`

### Tone

Informative, brief, benefit-forward. Avoid marketing superlatives ("exciting", "powerful"). Avoid engineering jargon ("refactored", "migrated", "scaffolded", "deprecated"). Write for a non-technical user who wants to know if anything changed that affects them.

### Server flag removals

Flag removal lines describe **the feature the flag was guarding**, in plain user-facing language. Look up the associated Jira ticket, Confluence page, or Slack thread description to find the right framing. The internal flag name is a lookup key only — it never appears in the output.

Use the format:

```
Removed feature flag for [user-facing description of what the feature does]
```

Example: a flag named `pm-36859-refactor-org-collections-vault-component` becomes:

```
Removed feature flag for organization vault collection management improvements
```

Self-hosted users are the primary audience for this line — they are receiving the feature for the first time when the flag is removed, so the description should communicate the benefit clearly.

### Flags enabled for previously-shipped work

When a flag in the Slack thread's **enabled** list has no matching issue in this release (resolved per Step 3), write a normal named bullet describing the feature going live — phrased the same as any other `Added`/`Updated` line. Do not call out that it was "previously shipped" or reference the flag mechanics; users only care that the feature is now available to them.

Example: the Slack thread lists `pm-40021-item-share-preview` as enabled, but every issue tagged with that flag shipped two releases ago and none appear in this release's Jira list. A Jira search for the flag identifier turns up the original ticket, "Add preview before sharing vault items." The resulting line:

```
Added a preview step before sharing vault items
```

### Example output (clients release)

```
Updated UI for centralized ownership policy
Added a product tour for access intelligence
Added information banner to SCIM setup page
Added a checkout success page following Stripe payment flows
Various under-the-hood improvements and minor bug fixes
```

### Example output (server release with flag removals)

```
Added support for flexible collection permissions for enterprise plans
Improved admin console filtering for large organizations
Removed feature flag for flexible collection permission management
Removed feature flag for bulk collection management improvements
Various under-the-hood improvements and minor bug fixes
```

## Step 5: Review and Calibrate

Before presenting the final output, check:

- [ ] Every named bullet has its corresponding feature flag enabled in the Slack thread (or has no flag)
- [ ] Every flag in the Slack thread's enabled list has been checked against this release's Jira issues; any with no matching issue was resolved via lookup (not dropped) and has a bullet
- [ ] No internal or infrastructure-only changes appear as named bullets
- [ ] Server releases include a line for every flag removal mentioned in the Slack thread, written in user-facing language
- [ ] No internal flag identifiers appear anywhere in the output
- [ ] Total named bullets are between 3 and 7 (if more than 7 are equally important, consolidate similar items)
- [ ] The catch-all line is present
- [ ] No markdown formatting in the output text
