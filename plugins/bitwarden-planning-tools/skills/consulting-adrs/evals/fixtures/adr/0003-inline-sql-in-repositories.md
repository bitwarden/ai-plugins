# ADR-0003: Inline SQL in repository classes

- Status: Deprecated
- Date: 2025-05-09
- Deprecated: 2025-11-25
- Tags: server

## Context

Early repositories embedded SQL strings directly in C# repository methods for
speed of iteration.

## Decision

Write SQL inline in repository classes rather than in separate stored
procedures or query files.

## Consequences

- Deprecated as of 2025-11-25: inline SQL proved hard to review and test in
  isolation. This decision no longer constrains current work; it is retained
  as historical context only.
