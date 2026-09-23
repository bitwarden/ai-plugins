---
adr: "9001"
status: Accepted
date: 2025-03-04
tags: [server]
---

# 9001 - Return Result types for expected service errors

<AdrTable frontMatter={frontMatter}></AdrTable>

## Context and problem statement

Service methods historically threw exceptions for expected, non-exceptional
outcomes (a record not found, a validation failure). Throwing for control flow
is expensive, hides the failure in the type signature, and pushes error
handling to a distant catch block.

## Decision

Service methods return a `Result<T>` type for expected error conditions.
Exceptions are reserved for genuinely exceptional, unrecoverable states. The
`Result<T>` carries either the value or a typed error, and callers must handle
both arms explicitly.

## Consequences

- Expected failures are visible in the method signature.
- Callers cannot ignore the error arm without a compiler warning.
- Throwing for an expected "not found" or validation failure is a deviation
  from this decision.
