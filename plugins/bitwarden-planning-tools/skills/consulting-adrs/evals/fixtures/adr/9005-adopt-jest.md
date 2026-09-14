---
adr: "9005"
status: Accepted
date: 2025-07-02
tags: [clients]
---

# 9005 - Adopt Jest as the unit test runner

<AdrTable frontMatter={frontMatter}></AdrTable>

> Supersedes ADR-9002.

## Context and problem statement

ADR-9002 adopted Vitest, but the shared client mocking utilities and CI cache
tooling standardized on Jest, creating friction. A single runner aligned with
those utilities was needed.

## Decision

Adopt Jest as the standard unit test runner for all client packages,
superseding ADR-9002. New unit tests are written for Jest.

## Consequences

- Alignment with the shared mocking utilities.
- ADR-9002 (Vitest) is superseded and no longer in force.
