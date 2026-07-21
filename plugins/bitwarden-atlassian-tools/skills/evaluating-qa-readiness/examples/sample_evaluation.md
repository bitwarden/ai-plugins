# Sample Evaluation

A worked walkthrough of evaluating a Story that's been moved to Ready for QA.

## Input

User: "Is PM-4821 ready for QA?"

## Gathering

1. `get_issue("PM-4821")` returns a Story: _"Add per-item reprompt toggle to vault item edit view."_
   - **Description**: Explains the feature and lists acceptance criteria ("User can toggle master-password reprompt on an individual item; setting persists after sync").
   - **Custom fields**: A "Feature Flag" field exists but is empty. An "Affected Clients" field lists _Web, Browser Extension_.
   - No implementation summary in the description.
2. `get_issue_comments("PM-4821")` returns one comment from the developer: _"To test: create a login item, open edit, flip the new 'Require master password re-prompt' switch, save, refresh — switch state should persist. Also confirm reprompt is enforced on view."_
3. `get_issue_remote_links("PM-4821")` returns a linked GitHub PR.

## Reasoning

- **Testing instructions** → Present. Clear steps and an expected result in the developer's comment.
- **Implementation notes** → Missing. There's a PR link but no summary of what changed; QA would have to read the diff.
- **Feature flag** → Unclear. A "Feature Flag" field exists but is empty — so it's ambiguous whether the feature is flagged and, if so, what state to test in. Flag by name.
- **Acceptance criteria** → Present. Stated in the description and testable.
- **Affected clients/platforms** → Present. Web and Browser Extension named in the custom field.
- **Linked PR/build** → Present. PR linked via remote links.

Blocking criteria: testing instructions (pass), implementation notes (fail), feature flag (unclear → fail). Two blocking gaps → **Not ready**.

## Output

## QA Readiness: PM-4821 — Add per-item reprompt toggle to vault item edit view

**Verdict:** Not ready — 2 blocking gaps

| Criterion                  | Status     | Notes                                                                                                   |
| -------------------------- | ---------- | ------------------------------------------------------------------------------------------------------- |
| Testing instructions       | ✅ Present | Steps + expected result in developer comment (persist after refresh; reprompt enforced on view).        |
| Implementation notes       | ❌ Missing | PR is linked but there's no summary of what changed/where — QA shouldn't have to read the diff.         |
| Feature flag               | ⚠️ Unclear | "Feature Flag" field exists but is empty. Can't tell if the toggle is flagged or what state to test in. |
| Acceptance criteria        | ✅ Present | Stated and testable in description.                                                                     |
| Affected clients/platforms | ✅ Present | Web, Browser Extension (custom field).                                                                  |
| Linked PR/build            | ✅ Present | GitHub PR linked via remote links.                                                                      |

**Draft comment for the developer:**

> Nearly there — before this moves to Ready for QA, could you add:
>
> - **Feature flag:** the "Feature Flag" field is empty. Is the reprompt toggle behind a flag? If so, which flag and what state should QA set it to? If it's not flagged, a quick "not behind a flag" works.
> - **Implementation notes:** a one-line summary of what changed and which areas it touches, so QA knows the surface to exercise (the PR link alone means reading the diff).
>
> Testing steps, AC, affected clients, and the PR link all look good — thanks!
