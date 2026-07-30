# ADR-0002: Adopt Vitest as the unit test runner

- Status: Superseded by ADR-0005
- Date: 2025-04-18
- Tags: clients

## Context

The client codebase needed a single, fast unit test runner with native ESM and
TypeScript support.

## Decision

Adopt Vitest as the standard unit test runner for all client packages. New unit
tests are written for Vitest.

## Consequences

- One runner across client packages.
- Superseded: ADR-0005 later reversed this in favor of Jest for alignment with
  the shared mocking utilities. Do not write new tests against this decision;
  see ADR-0005.
