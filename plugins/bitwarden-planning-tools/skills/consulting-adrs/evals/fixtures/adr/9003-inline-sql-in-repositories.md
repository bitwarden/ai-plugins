---
adr: "9003"
status: Deprecated
date: 2025-05-09
tags: [server]
---

# 9003 - Inline SQL in repository classes

<AdrTable frontMatter={frontMatter}></AdrTable>

:::warning Deprecated

Deprecated as of 2025-11-25: inline SQL proved hard to review and test in
isolation. This decision no longer constrains current work; it is retained
as historical context only.

:::

## Context and problem statement

Early repositories embedded SQL strings directly in C# repository methods for
speed of iteration.

## Decision

Write SQL inline in repository classes rather than in separate stored
procedures or query files.

## Consequences

- Contributors reviewing this ADR should follow the deprecation notice above
  rather than the original decision.
