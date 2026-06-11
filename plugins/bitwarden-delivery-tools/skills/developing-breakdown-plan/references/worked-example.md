# Worked example: Cross-team impact characterization

This example illustrates Activity 4 (Identify cross-team impacts and surface them) from `SKILL.md`. It walks through the (A) → (B) → (C) characterization for a realistic cross-team touch.

## Scenario

Auth wants to add a new push-notification type to alert clients when a security key is registered.

## Walkthrough

**(A) Ownership crossing.** The push-notification dispatch lives under Platform's `CODEOWNERS`. Yes, this crosses an ownership boundary.

**(B1) Domain-overlap depth.** _Mid_ — Auth needs to follow Platform's established push-type contract (enum extension, payload shape, client-side handler registration). No deep invariants touched.

**(B2) Owning-team churn.** Grep `bitwarden/tech-breakdowns/platform/` for `push-notification` returns one in-flight breakdown about delivery retry semantics, but not about the push-type registry. `git log --since="3 months ago" -- src/notifications/` shows two recent merges, both bug fixes. No material churn in the area Auth is touching.

**(C) Captured as.**

- Owning team: Platform
- Interface: "Add new push type `SECURITY_KEY_REGISTERED` to the existing registry; payload follows the standard envelope (Mid depth, no churn in this area)"
- Associated breakdown: link to Platform's retry-semantics breakdown for context
- Model and Signoff columns: left empty
- Add a Coordination note flagging the adjacent retry-semantics work in case sequencing matters.

## Interpretation

The Mid + no-churn cell typically points to a standard signoff row and a self-service PR by Auth — no proactive Slack alignment needed before review. If churn had been _Yes_, a Slack heads-up to Platform's public channel would be the right call before drafting.
