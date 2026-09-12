---
adr: "9002"
status: Superseded
date: 2025-04-18
tags: [clients]
---

# 9002 - Adopt Vitest as the unit test runner

<AdrTable frontMatter={frontMatter}></AdrTable>

> Superseded by ADR-9005.

## Context and problem statement

The client codebase needed a single, fast unit test runner with native ESM and
TypeScript support.

## Decision

Adopt Vitest as the standard unit test runner for all client packages. New unit
tests are written for Vitest.

## Consequences

- One runner across client packages.
- Superseded: ADR-9005 later reversed this in favor of Jest for alignment with
  the shared mocking utilities. Do not write new tests against this decision;
  see ADR-9005.
