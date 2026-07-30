# ADR-0004: Cross-client DTOs live in the shared common package

- Status: Accepted
- Date: 2025-06-12
- Tags: clients, server

## Context

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
