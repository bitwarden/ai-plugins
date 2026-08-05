---
adr: "9004"
status: Accepted
date: 2025-06-12
tags: [clients, server]
---

# 9004 - Cross-client DTOs live in the shared common package

<AdrTable frontMatter={frontMatter}></AdrTable>

## Context and problem statement

Request and response DTOs shared across clients were duplicated per client,
drifting over time and breaking the version matrix (server must support clients
up to two major versions behind).

## Decision

Cross-client DTOs live in a single shared `common` package. New fields on
existing DTOs are optional, so a client that has not updated still deserializes
responses. Required fields are never added to an existing shared DTO.

## Consequences

- One source of truth for shared contracts.
- Adding a required field to an existing shared DTO, or forking a per-client
  copy of a shared DTO, is a deviation from this decision.
