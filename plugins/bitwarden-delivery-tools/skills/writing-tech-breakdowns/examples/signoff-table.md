# Example: A Worked Cross-team Signoff Table

This is a worked example of the cross-team signoff table for an illustrative Bitwarden feature. It shows the kind of detail each column needs, who belongs in the table vs. who belongs in Coordination notes, and what an in-flight breakdown looks like versus a fully-signed-off one.

The example feature is fictitious — used here for shape, not as canonical guidance for any real product surface.

## Scenario

The team is adding a new "Vault Sharing Audit Log" feature: every time a user shares a vault item with a member of another organization, the action is recorded in an audit log visible to both organization admins. The feature touches database, server APIs, web UI, mobile UI, and the component library.

The team is at the `Proposed` status and has just walked the cross-team checklist.

## In-flight signoff table (mid-coordination)

| Team              | Interface                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Associated breakdown                                                  | Signoff                                                                  |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| **Mobile**        | Mobile parity for the audit log viewer screen (read-only list, filter by date and actor). Separate Jira stories created on the Mobile board for the screen implementation and design system work. **Model: File a Ticket.** Mobile owns the codebase, the driving team has no native iOS/Android engineers, and the work fits Mobile's sprint cadence. Knowledge transfer isn't a goal — Mobile UI parity is a recurring pattern they're equipped to absorb.                                                                                  | [Mobile Vault Sharing Audit Log breakdown](https://example/mobile-bd) | _Pending — posted in #team-mobile on 2026-05-13, tagging @mobile-tl_     |
| **UI Foundation** | New `bit-audit-log-row` component (timestamp, actor, action verb, target item). API designed for reuse beyond this feature. **Model: Internal Open-Source.** Driving team uses the library every day and has frontend bandwidth, so they write the PR following the library's conventions; UIF reviews the API for reuse fit and merges. File a Ticket was considered but rejected because UIF doesn't carry feature-team component work in their sprint.                                                                                     | _None — UIF will review the API in this breakdown_                    | **Approved — @uif-tl, 2026-05-11**                                       |
| **Platform**      | New audit-event topic on the existing event bus. Schema-only addition; the topic-registration path is a documented Platform contribution pattern. **Model: Internal Open-Source.** Driving team writes the topic registration and event schema PR following Platform's documented pattern; Platform reviews the schema for downstream-impact concerns (consumer compatibility, retention, PII) and merges. File a Ticket was considered, but Platform's pattern is mature enough that they prefer reviewing schemas rather than writing them. | _None_                                                                | _Pending — schema review scheduled 2026-05-15, posted in #team-platform_ |

## What stays out of the signoff table

Every row in the table is a team whose signoff the breakdown needs to move to `Accepted`. Teams that only need to be informed — read-only dependencies, downstream-impact FYIs, adjacent areas that might want to know — don't belong in the table; they belong in the breakdown's **Coordination notes** subsection, with an FYI post on their public Slack channel.

Two impacts from this scenario stay out of the table:

- **Auth** — the audit-log entries call `IUserService.GetOrganizationMembership` to resolve recipient organizations. No interface change on Auth's side, no design they need to evaluate. Captured in Coordination notes as "read dependency on `IUserService.GetOrganizationMembership`; FYI posted in `#team-auth` on 2026-05-12, no signoff required."
- **Billing** — the new feature surface might shift future enterprise-tier metrics Billing cares about. No code change, no design they need to evaluate. Captured in Coordination notes as "downstream metrics impact for future enterprise tiers; FYI posted in `#team-billing` on 2026-05-12, no signoff required."

If either team came back with concerns the design needed to address, the row would move from Coordination notes into the signoff table — but until then, naming them in the table inflates the gating set and dilutes what signoffs mean.

## What this table demonstrates

### Specific, codable interface descriptions

The "Interface" column names the actual contract: a specific component (`bit-audit-log-row`), a specific event-bus topic, a concrete Mobile screen with filter affordances. An engineer on the other team can react to these without re-reading the whole breakdown.

### Named collaboration model per impact

Every row names a model with reasoning that traces to the change shape:

- **Mobile — File a Ticket.** The Mobile codebase is owned by Mobile, the driving team has no native engineers, and mobile UI parity is a recurring pattern Mobile is equipped to absorb. The change is in Mobile's domain, so Mobile writes its own breakdown (linked in the `Associated breakdown` column) and creates its own epic and stories on the Mobile board. File a Ticket here means a real transfer of planning and execution work onto Mobile's roadmap — it isn't free for the driving team, and it doesn't mean "file and forget"; the driving team is still on the hook for alignment, refinement, and follow-up.
- **UI Foundation — Internal Open-Source.** The change is adding a new component following the library's documented conventions — a "build on top of" extension, not a change to how the library works. The driving team uses the library every day and has frontend bandwidth, so they write the PR; UIF reviews the API for reuse fit and merges. The rejected alternative (File a Ticket) was wrong because UIF doesn't carry feature-team component work in their sprint.
- **Platform — Internal Open-Source.** Adding a new event topic follows Platform's documented contribution pattern, so the driving team writes the topic registration and schema PR; Platform reviews the schema for downstream impact and merges. File a Ticket would have been overkill — there's no domain-deep change to the event-bus mechanism itself, and Platform's pattern is mature enough to absorb an outside PR cleanly.

No row defaults to Embedded Expert — that model is reserved for critical periods on the driving team's codebase where the driving team needs owning-team expertise inside their code, not a first-interaction pick.

The Internal Open-Source choices here both involve the driving team writing code in another team's repo. The split between File a Ticket and Internal Open-Source isn't about urgency or preference — it's about whether the change is **adding an instance of an established pattern** (Internal Open-Source) or **changing how the pattern works** (File a Ticket). The Mobile parity work is firmly in "another stack with its own conventions and its own sprint" territory, which is why it's File a Ticket even though the driving team is faster than waiting on Mobile.

### Named-human signoffs with dates

Approved rows show specific people and dates (`@uif-tl, 2026-05-11`), not "the team." Pending rows describe the current state of the conversation, not just "waiting."

### "Associated breakdown" is selectively filled

Only the Mobile row has an associated sibling breakdown — because the mobile work is structurally separate (new Jira stories, new sprint allocation on the Mobile board). The UI Foundation and Platform interfaces are scoped within this breakdown, so no sibling exists.

## When the breakdown is ready to move to Accepted

Same table after coordination completes:

| Team              | Interface                                            | Associated breakdown                                                  | Signoff                                       |
| ----------------- | ---------------------------------------------------- | --------------------------------------------------------------------- | --------------------------------------------- |
| **Mobile**        | _(unchanged)_                                        | [Mobile Vault Sharing Audit Log breakdown](https://example/mobile-bd) | **Approved — Mobile Tech Lead, 2026-05-16**   |
| **UI Foundation** | _(unchanged)_                                        | _None — UIF will review the API in this breakdown_                    | **Approved — @uif-tl, 2026-05-11**            |
| **Platform**      | _(schema approved as documented in Plan subsection)_ | _None_                                                                | **Approved — Platform Tech Lead, 2026-05-17** |

Every signoff row has a named human and date. The Coordination notes entries for Auth and Billing carry their FYI posts so the awareness trail exists even though those teams aren't gating the transition. The breakdown is ready to move `Proposed → Accepted`.
