# Example: A Worked Cross-team Signoff Table

This is a worked example of the cross-team signoff table for an illustrative Bitwarden feature. It shows the kind of detail each column needs, how to distinguish blocking from advisory signoffs, and what an in-flight breakdown looks like versus a fully-signed-off one.

The example feature is fictitious — used here for shape, not as canonical guidance for any real product surface.

## Scenario

The team is adding a new "Vault Sharing Audit Log" feature: every time a user shares a vault item with a member of another organization, the action is recorded in an audit log visible to both organization admins. The feature touches database, server APIs, web UI, mobile UI, and the component library.

The team is at the `Proposed` status and has just walked the cross-team checklist.

## In-flight signoff table (mid-coordination)

| Team              | Interface                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Blocking? | Associated breakdown                                                  | Signoff                                               |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | --------------------------------------------------------------------- | ----------------------------------------------------- |
| **Mobile**        | Mobile parity for the audit log viewer screen (read-only list, filter by date and actor). Separate Jira stories created on the Mobile board for the screen implementation and design system work. **Model: File a Ticket.** Mobile owns the codebase, the driving team has no native iOS/Android engineers, and the work fits Mobile's sprint cadence. Knowledge transfer isn't a goal — Mobile UI parity is a recurring pattern they're equipped to absorb.                                                                                  | Yes       | [Mobile Vault Sharing Audit Log breakdown](https://example/mobile-bd) | _Pending — DM sent to mobile TL on 2026-05-13_        |
| **UI Foundation** | New `bit-audit-log-row` component (timestamp, actor, action verb, target item). API designed for reuse beyond this feature. **Model: Internal Open-Source.** Driving team uses the library every day and has frontend bandwidth, so they write the PR following the library's conventions; UIF reviews the API for reuse fit and merges. File a Ticket was considered but rejected because UIF doesn't carry feature-team component work in their sprint.                                                                                     | Yes       | _None — UIF will review the API in this breakdown_                    | **Approved — @uif-tl, 2026-05-11**                    |
| **Auth**          | Read dependency on `IUserService.GetOrganizationMembership` to resolve the recipient organization for each audit entry. No interface change on their side. **Model: none** — pure consumption of an existing, stable service method.                                                                                                                                                                                                                                                                                                          | No        | _None — read-only dependency_                                         | _Pending — advisory; FYI thread posted in #team-auth_ |
| **Platform**      | New audit-event topic on the existing event bus. Schema-only addition; the topic-registration path is a documented Platform contribution pattern. **Model: Internal Open-Source.** Driving team writes the topic registration and event schema PR following Platform's documented pattern; Platform reviews the schema for downstream-impact concerns (consumer compatibility, retention, PII) and merges. File a Ticket was considered, but Platform's pattern is mature enough that they prefer reviewing schemas rather than writing them. | Yes       | _None_                                                                | _Pending — schema review scheduled 2026-05-15_        |
| **Billing**       | Informational only — the new feature surface might affect future enterprise-tier metrics Billing cares about. No code change required. **Model: none** — advisory.                                                                                                                                                                                                                                                                                                                                                                            | No        | _None_                                                                | **Acknowledged — @billing-tl, 2026-05-12**            |

## What this table demonstrates

### Specific, codable interface descriptions

The "Interface" column names the actual contract: a specific component (`bit-audit-log-row`), a specific service method (`IUserService.GetOrganizationMembership`), a specific event-bus topic. An engineer on the other team can react to these without re-reading the whole breakdown.

### Named collaboration model per impact

Every row that involves work names a model with reasoning that traces to the change shape:

- **Mobile — File a Ticket.** The Mobile codebase is owned by Mobile, the driving team has no native engineers, and mobile UI parity is a recurring pattern Mobile is equipped to absorb. The change is in Mobile's domain, so Mobile writes its own breakdown (linked in the `Associated breakdown` column) and creates its own epic and stories on the Mobile board. File a Ticket here means a real transfer of planning and execution work onto Mobile's roadmap — it isn't free for the driving team.
- **UI Foundation — Internal Open-Source.** The change is adding a new component following the library's documented conventions — a "build on top of" extension, not a change to how the library works. The driving team uses the library every day and has frontend bandwidth, so they write the PR; UIF reviews the API for reuse fit and merges. The rejected alternative (File a Ticket) was wrong because UIF doesn't carry feature-team component work in their sprint.
- **Platform — Internal Open-Source.** Adding a new event topic follows Platform's documented contribution pattern, so the driving team writes the topic registration and schema PR; Platform reviews the schema for downstream impact and merges. File a Ticket would have been overkill — there's no domain-deep change to the event-bus mechanism itself, and Platform's pattern is mature enough to absorb an outside PR cleanly.
- **Auth — none.** Read-only dependency on an existing, stable service method. No code change Auth-side; no model required.
- **Billing — none.** Advisory FYI only; no work to coordinate.

Note that the rows without work name "none" explicitly so the absence is intentional, not forgotten. And no row defaults to Embedded Expert — that model is reserved for critical periods on the driving team's codebase where the driving team needs owning-team expertise inside their code, not a first-interaction pick.

The Internal Open-Source choices here both involve the driving team writing code in another team's repo. The split between File a Ticket and Internal Open-Source isn't about urgency or preference — it's about whether the change is **adding an instance of an established pattern** (Internal Open-Source) or **changing how the pattern works** (File a Ticket). The Mobile parity work is firmly in "another stack with its own conventions and its own sprint" territory, which is why it's File a Ticket even though the driving team is faster than waiting on Mobile.

### Honest Blocking? assignment

- **Mobile (Yes)** — the change touches their codebase; their signoff is a hard gate. Note that the row also explicitly mentions Jira-story handoff to the Mobile board, matching the template's "mobile changes need separate Jira stories" rule.
- **UI Foundation (Yes)** — the team is contributing a new public component to the library; the UI Foundation team owns the library's API. Their signoff is structurally required.
- **Auth (No)** — purely a read dependency on an existing, stable service method. They're informed (advisory) because their service is touched, but the work doesn't change anything on their side.
- **Platform (Yes)** — a new event topic on infrastructure they own. They've not yet confirmed the schema, so Blocking is correct. (If the schema were already published as a known pattern, this might be advisory.)
- **Billing (No)** — they're being informed because the feature might affect their downstream metrics, not because their code is changing. Advisory.

### Named-human signoffs with dates

Approved rows show specific people and dates (`@uif-tl, 2026-05-11`), not "the team." Pending rows describe the current state of the conversation, not just "waiting."

### "Associated breakdown" is selectively filled

Only the Mobile row has an associated sibling breakdown — because the mobile work is structurally separate (new Jira stories, new sprint allocation). The Auth and Platform interfaces are scoped within this breakdown, so no sibling exists. The Billing row is informational and doesn't need one.

## When the breakdown is ready to move to Accepted

Same table after coordination completes:

| Team              | Interface                                            | Blocking? | Associated breakdown                                                  | Signoff                                    |
| ----------------- | ---------------------------------------------------- | --------- | --------------------------------------------------------------------- | ------------------------------------------ |
| **Mobile**        | _(unchanged)_                                        | Yes       | [Mobile Vault Sharing Audit Log breakdown](https://example/mobile-bd) | **Approved — @mobile-tl, 2026-05-16**      |
| **UI Foundation** | _(unchanged)_                                        | Yes       | _None — UIF will review the API in this breakdown_                    | **Approved — @uif-tl, 2026-05-11**         |
| **Auth**          | _(unchanged)_                                        | No        | _None — read-only dependency_                                         | **Acknowledged — @auth-tl, 2026-05-14**    |
| **Platform**      | _(schema approved as documented in Plan subsection)_ | Yes       | _None_                                                                | **Approved — @platform-tl, 2026-05-17**    |
| **Billing**       | _(unchanged)_                                        | No        | _None_                                                                | **Acknowledged — @billing-tl, 2026-05-12** |

Every Blocking row has a named human and date in the Signoff column. Every advisory row has been acknowledged (closed) rather than left silent. The breakdown is ready to transition `Proposed → Accepted`.

## Common shapes to look out for

- **A Blocking row outstanding for more than a sprint** — see the Platform row in the in-flight table above. If the schema review keeps slipping, this is a contested interface, not a patience problem. Escalate via the initiative owner or the team's EM. See the "Owner-Mediated Escalation" section in the parent SKILL.md.
- **All rows marked Blocking** — usually a sign of over-marking. Re-evaluate which signoffs are genuinely gating versus FYI-level. Half-blocking, half-advisory is the healthy mix on most cross-team breakdowns.
- **A conditional signoff captured as "Approved"** — if a signoff is genuinely contingent ("yes, with these caveats"), the caveats belong in the Clarifications Log as open entries before the breakdown moves to `Accepted`. Don't paper over conditional signoffs in the table.
- **An empty "Interface" cell** — the other team can't react to a row that doesn't name what's being asked of them. If the interface is genuinely unclear, that's a Clarifications Log entry, not an empty cell.
