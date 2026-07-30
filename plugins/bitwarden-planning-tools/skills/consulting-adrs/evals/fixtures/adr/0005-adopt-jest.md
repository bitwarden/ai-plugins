# ADR-0005: Adopt Jest as the unit test runner

- Status: Accepted
- Date: 2025-07-02
- Supersedes: ADR-0002
- Tags: clients

## Context

ADR-0002 adopted Vitest, but the shared client mocking utilities and CI cache
tooling standardized on Jest, creating friction. A single runner aligned with
those utilities was needed.

## Decision

Adopt Jest as the standard unit test runner for all client packages,
superseding ADR-0002. New unit tests are written for Jest.

## Consequences

- Alignment with the shared mocking utilities.
- ADR-0002 (Vitest) is superseded and no longer in force.
