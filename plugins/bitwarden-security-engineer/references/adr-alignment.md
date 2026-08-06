# Architecture Decision Alignment

Bitwarden's accepted architecture decisions are catalogued separately from the security principles in `bitwarden-security-context`. Security assessments must check alignment against these — a design can satisfy P01-P06 in the abstract while still contradicting a specific, already-decided architectural direction.

- Before assessing a system or change, check whether an existing ADR covers the component or pattern under review.
- A design that conflicts with an accepted ADR is a finding, not a style preference — surface it explicitly rather than silently reviewing against general best practice instead.
- A significant architectural choice with no corresponding ADR is a gap worth flagging, not something to silently wave through.
- Confirm an ADR's status before citing it — superseded or deprecated decisions are historical context, not current constraints.

Full documentation: [Architecture Decision Records](https://contributing.bitwarden.com/architecture/adr/)
