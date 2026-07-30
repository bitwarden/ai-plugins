---
name: consulting-adrs
description: Check a design, change, plan, or threat model against Bitwarden's Architecture Decision Records (ADRs), or locate and summarize the ADR catalog. Use when assessing whether an approach conflicts with, is governed by, or lacks an accepted ADR, or when someone needs to find or summarize ADRs. Produces structured findings (conflict, gap, aligned) with cited ADRs, or an ADR summary when that is the ask.
allowed-tools: Skill, WebFetch(domain:contributing.bitwarden.com), Read, Grep
---

# Validate against ADRs

Check the design, diff, plan, or threat model under review against Bitwarden's Architecture Decision Records. Return findings; the caller decides what to do with them.

Source: https://contributing.bitwarden.com/architecture/adr/ (fetch the index, then the ADR). If `bitwarden/contributing` is checked out locally, Grep/Read it instead.

If the ask is to locate or summarize ADRs rather than validate a specific change, skip the finding format: use Steps 1-2 to find the relevant ADRs and confirm status, then return them as a concise list of title and status. Include a URL only if you verified it from the source; otherwise cite the local path. Never construct or guess an ADR URL.

## Steps

1. Map what the change touches (domain; new contract, field, trust boundary, dependency, or cross-client pattern). Search the ADR catalog for those terms. Nothing relevant is a valid result: report it, do not invent one.
2. Confirm each candidate ADR's status. Only **Accepted** binds. Follow **Superseded** to its replacement and evaluate that. Ignore **Deprecated** and **Rejected**. Flag **Proposed** as not-yet-ratified.
3. Classify each in-force ADR against the change:
   - **Aligned**: conforms. One line, no restatement.
   - **Conflict**: contradicts the decision. Cite the ADR, quote the decision text, name the contradicting element.
   - **Gap**: a significant decision with no ADR. Significant = defines a contract, costly to reverse (data model, service boundary, protocol, auth), sets a new precedent, has cross-team/client blast radius, or is external-facing. Otherwise it is an implementation detail: do not flag it.
   - **Stale-reference**: relies on or cites a superseded/deprecated ADR. Point to the current one.

## Output

Per finding:
`[CONFLICT|GAP|STALE-REFERENCE] <summary> — ADR <n> <title> (<status>, <url>); decision: "<text>" (omit for GAP); in change: <element>.`

End with a roll-up: counts per type, or one line stating no in-force ADR was relevant.

## Rules

- Never invent an ADR number, title, or URL. Unverified means report none found.
- Best practice is not an ADR. Only a recorded decision creates a conflict.
- Match effort to blast radius. Skip changes with no architectural surface.
