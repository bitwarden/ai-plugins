# Sample Evaluation

A worked walkthrough of evaluating a Bug that's been moved to Ready for QA. It shows three judgment calls: a PR found through the Development field, a single named flag whose state is inferred, and a short QA note accepted as enough.

## Input

User: "Is PM-4821 ready for QA?"

## Gathering

1. `get_issue("PM-4821")` returns a Bug: _"Don't leave orphaned attachment files in storage."_
   - **Description**: "When a cipher, user, or org is deleted, also delete its attachment files and Send files from blob storage." Names the flag: `pm-4821-attachment-cleanup`.
   - **Additional Fields → QA testing notes**: "Adds a scheduled job that deletes orphaned attachment files after a cipher/user/org is deleted. Test by deleting each and confirming the files are gone from storage. Deletion runs in batches, so large orgs take a while. Should work on cloud and self-hosted."
   - **Additional Fields → Development**: `Pull requests: 2 (MERGED); Branches: 1`
   - **Components**: Server. No acceptance criteria field or section.
2. `get_issue_comments("PM-4821")` returns a comment from April: _"The description isn't accurate. Send files are already cleaned up by PM-4790, so they shouldn't be in scope here."_ A reply agrees the scope needs discussing. No later comment settles it, and the description still mentions Sends. No earlier comment starts with `QA readiness check:`, so this gap hasn't been raised yet.
3. `get_issue_remote_links("PM-4821")` returns a Confluence page on data retention.

## Reasoning

- **Testing notes** → Present. The QA note says what to test (delete each entity type, confirm files are gone), and it calls out the non-obvious parts: batching and cloud vs. self-hosted. No numbered steps, no storage query, no timing, and none are needed.
- **Implementation notes** → Present. "Adds a scheduled job that deletes orphaned attachment files" tells QA the surface area.
- **Settled scope** → Unclear. The April comment says Sends shouldn't be in scope, nobody resolved it, and the description still lists them. A tester doesn't know whether to test Send files.
- **Feature flag** → Present. One flag is named, so "enable it to test" is the reasonable default. Cloud vs. self-hosted is mentioned, but only as "should work on both," not as a question about the flag, so this doesn't make the state ambiguous.
- **Acceptance criteria** → Missing. No testable "done" statement. The QA note covers some of it, but AC is evaluated separately.
- **Affected clients/platforms** → Present. Server component, cloud and self-hosted named.
- **Linked PR/build** → Present. Two merged PRs in the Development field.

Blocking: settled scope is unclear, so this is **Not ready** with one blocking gap. Missing AC is also worth raising, since fixing the scope question naturally produces AC.

## Output

```
## QA Readiness: PM-4821 — Don't leave orphaned attachment files in storage

**Verdict:** Not ready — 1 blocking gap

| Criterion                  | Status     | Notes                                                                                              |
| -------------------------- | ---------- | -------------------------------------------------------------------------------------------------- |
| Testing notes              | ✅ Present | QA testing notes field: what to test, plus callouts for batching and cloud/self-hosted.            |
| Implementation notes       | ✅ Present | QA notes describe the new scheduled cleanup job.                                                   |
| Settled scope              | ⚠️ Unclear | April comment says Sends are out of scope (handled by PM-4790); description still includes them.   |
| Feature flag               | ✅ Present | `pm-4821-attachment-cleanup` named in description; assuming enabled to test.                       |
| Acceptance criteria        | ❌ Missing | No testable "done" statement.                                                                      |
| Affected clients/platforms | ✅ Present | Server; cloud and self-hosted.                                                                     |
| Linked PR/build            | ✅ Present | 2 merged PRs in the Development panel.                                                             |
```

## Posting

The skill posts the ask with `add_issue_comment`:

```
add_issue_comment(
  issueIdOrKey: "PM-4821",
  dryRun: false,
  body: "QA readiness check: before this is ready for QA, could you settle the scope?

The April comment says Send files are already handled by PM-4790, but the description still includes them. Updating the description, or adding AC for what's in scope, would cover it."
)
```

The body is plain text. The blank line splits it into two paragraphs on the ticket, and there's no Markdown to show up literally.

Then, below the table:

> Posted a comment on PM-4821 (comment id 10432):
>
> QA readiness check: before this is ready for QA, could you settle the scope?
>
> The April comment says Send files are already handled by PM-4790, but the description still includes them. Updating the description, or adding AC for what's in scope, would cover it.

Note what the comment leaves out: no request for step-by-step instructions, no question about what state the flag should be in, and no PR question. The ticket already answers or lets the tester infer all of those. Missing AC isn't a separate ask either, since settling the scope naturally produces it.

If this install had no `ATLASSIAN_JIRA_WRITE_TOKEN`, the tool would refuse the post. The skill would then show the same text as a draft for the user to paste, and say that setting the token lets it post comments itself.
