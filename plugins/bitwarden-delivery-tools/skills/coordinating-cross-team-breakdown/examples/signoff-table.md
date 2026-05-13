# Example: A Worked Part 3 Signoff Table

This is a worked example of the Part 3 cross-team signoff table for an illustrative Bitwarden feature. It shows the kind of detail each column needs, how to distinguish blocking from advisory signoffs, and what an in-flight breakdown looks like versus a fully-signed-off one.

The example feature is fictitious — used here for shape, not as canonical guidance for any real product surface.

## Scenario

The team is adding a new "Vault Sharing Audit Log" feature: every time a user shares a vault item with a member of another organization, the action is recorded in an audit log visible to both organization admins. The feature touches database, server APIs, web UI, mobile UI, and the Component Library.

The team is at the `PROPOSED` status and has just walked the cross-team checklist.

## In-flight signoff table (mid-coordination)

| Team                  | Describe interface                                                                                                                                                                                                  | Blocking? | Associated Other Team Breakdown                                       | Signoff                                                   |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | --------------------------------------------------------------------- | --------------------------------------------------------- |
| **Mobile**            | Mobile parity for the audit log viewer screen (read-only list, filter by date and actor). Separate Jira stories will be created and moved to the Mobile board for the screen implementation and design system work. | Yes       | [Mobile Vault Sharing Audit Log breakdown](https://example/mobile-bd) | _Pending — DM sent to mobile TL on 2026-05-13_            |
| **Component Library** | New `bit-audit-log-row` component contributed to the library (timestamp, actor, action verb, target item). API designed for reuse beyond this feature; coordinated with Design System team during Part 2 drafting.  | Yes       | _None — DSE will review the API in this breakdown_                    | **Approved — @design-system-tl, 2026-05-11**              |
| **Identity**          | Read dependency on `IUserService.GetOrganizationMembership` to resolve the recipient organization for each audit entry. No interface change on their side.                                                          | No        | _None — read-only dependency_                                         | _Pending — advisory; FYI thread posted in #team-identity_ |
| **Platform**          | New audit-event topic published to the existing event bus the platform team owns. They've confirmed the topic naming convention but want to see the event schema before signing off.                                | Yes       | _None_                                                                | _Pending — schema review scheduled 2026-05-15_            |
| **Billing**           | None — informed because the new feature surface might affect future enterprise-tier metrics they care about. No code change required.                                                                               | No        | _None_                                                                | **Acknowledged — @billing-tl, 2026-05-12**                |

## What this table demonstrates

### Specific, codable interface descriptions

The "Describe interface" column names the actual contract: a specific component (`bit-audit-log-row`), a specific service method (`IUserService.GetOrganizationMembership`), a specific event-bus topic. The other team's tech lead can react to these without re-reading the whole breakdown.

### Honest Blocking? assignment

- **Mobile (Yes)** — the change touches their codebase; their signoff is a hard gate. Note that the row also explicitly mentions Jira-story handoff to the Mobile board, matching the template's "mobile changes need separate Jira stories" rule.
- **Component Library (Yes)** — the team is contributing a new public component to the library; the Design System team owns the library's API. Their signoff is structurally required.
- **Identity (No)** — purely a read dependency on an existing, stable service method. They're informed (advisory) because their service is touched, but the work doesn't change anything on their side.
- **Platform (Yes)** — a new event topic on infrastructure they own. They've not yet confirmed the schema, so Blocking is correct. (If the schema were already published as a known pattern, this might be advisory.)
- **Billing (No)** — they're being informed because the feature might affect their downstream metrics, not because their code is changing. Advisory.

### Named-human signoffs with dates

Approved rows show specific people and dates (`@design-system-tl, 2026-05-11`), not "the team." Pending rows describe the current state of the conversation, not just "waiting."

### "Associated Other Team Breakdown" is selectively filled

Only the Mobile row has an associated sibling breakdown — because the mobile work is structurally separate (new Jira stories, new sprint allocation). The Identity and Platform interfaces are scoped within this breakdown, so no sibling exists. The Billing row is informational and doesn't need one.

## When the breakdown is ready to move to ACCEPTED

Same table after coordination completes:

| Team                  | Describe interface                                | Blocking? | Associated Other Team Breakdown                                       | Signoff                                      |
| --------------------- | ------------------------------------------------- | --------- | --------------------------------------------------------------------- | -------------------------------------------- |
| **Mobile**            | _(unchanged)_                                     | Yes       | [Mobile Vault Sharing Audit Log breakdown](https://example/mobile-bd) | **Approved — @mobile-tl, 2026-05-16**        |
| **Component Library** | _(unchanged)_                                     | Yes       | _None — DSE will review the API in this breakdown_                    | **Approved — @design-system-tl, 2026-05-11** |
| **Identity**          | _(unchanged)_                                     | No        | _None — read-only dependency_                                         | **Acknowledged — @identity-tl, 2026-05-14**  |
| **Platform**          | _(schema approved as documented in Part 4 child)_ | Yes       | _None_                                                                | **Approved — @platform-tl, 2026-05-17**      |
| **Billing**           | _(unchanged)_                                     | No        | _None_                                                                | **Acknowledged — @billing-tl, 2026-05-12**   |

Every Blocking row has a named human and date in the Signoff column. Every advisory row has been acknowledged (closed) rather than left silent. The breakdown is ready to transition `PROPOSED → ACCEPTED`.

## Common shapes to look out for

- **A Blocking row outstanding for more than a sprint** — see the Platform row in the in-flight table above. If the schema review keeps slipping, this is a contested interface, not a patience problem. Escalate via the shepherd or the team's EM. See the "Shepherd-Mediated Escalation" section in the parent SKILL.md.
- **All rows marked Blocking** — usually a sign of over-marking. Re-evaluate which signoffs are genuinely gating versus FYI-level. Half-blocking, half-advisory is the healthy mix on most cross-team breakdowns.
- **A conditional signoff captured as "Approved"** — if a signoff is genuinely contingent ("yes, with these caveats"), the caveats belong in Part 5 as open questions before the breakdown moves to ACCEPTED. Don't paper over conditional signoffs in the table.
- **An empty "Describe interface" cell** — the other team's tech lead can't react to a row that doesn't name what's being asked of them. If the interface is genuinely unclear, that's a Part 5 open question, not an empty cell.
