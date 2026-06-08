# Confirming the Model with the Owning Team

Load this reference when walking through Step 5 of the parent SKILL.md — confirming the proposed collaboration model with the owning team during cross-team signoff. The parent SKILL.md keeps the rule ("the model is a joint decision"); this file carries the four-step flow and the counter-proposal patterns.

## The flow

**The collaboration model is a joint decision, not a unilateral driving-team call.** The driving team proposes; the owning team confirms or counter-proposes during cross-team signoff.

1. **Driving team proposes the model** during breakdown drafting, based on the change shape and the inputs from Step 3. Capture it in the signoff-table row's `Interface` cell with the reasoning ("Model: Internal Open-Source — driving team writes the PR following library conventions; UIF reviews").
2. **Owning team confirms (or counter-proposes) during signoff.** Signoff implicitly endorses the proposed model. If the owning team objects, that's a Clarifications Log entry or a Coordination notes update, not a silent signoff with a different model in mind.
3. **Counter-proposals are material design changes.** Re-circulate to anyone who's already signed off; bump `Last substantive update` on the breakdown.
4. **Mark the model as confirmed in the signoff table** once both teams have agreed. The breakdown reads `Model: Internal Open-Source (confirmed @platform-tl, 2026-05-15)` instead of just `Model: Internal Open-Source` once signoff lands.

## Common counter-proposal patterns

- **Driving team proposed Internal Open-Source → owning team counter-proposes File a Ticket** because the change is deeper than the driving team realized, or because conventions aren't documented enough for an outside PR.
- **Driving team proposed File a Ticket → owning team counter-proposes Internal Open-Source** because they don't have sprint capacity but the conventions are documented enough that a PR will land cleanly.
- **Driving team proposed Internal Open-Source → owning team counter-proposes File a Ticket** because the area is in active flux and they'd rather sequence the change into their own work than absorb a parallel PR.
- **Driving team requested reviewers via Step 1's escape hatch → owning team counter-proposes Embedded Expert** because the change is high enough risk that they want an engineer inside the integration during the build, not just at review. This is the path Embedded Expert most often arrives by: as a counter-proposal from the owning team, not a unilateral pick by the driving team.

When a counter-proposal happens, the breakdown is the right place to capture the negotiation — both teams need the record for later.
