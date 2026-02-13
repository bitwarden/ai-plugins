# Data Flow Diagram Template

Use Mermaid syntax for text-based DFDs that can be version-controlled.

Bitwarden is moving toward a Structurizr-based approach for persistent
architecture diagrams. For ad-hoc threat modeling, Mermaid or Excalidraw
are acceptable.

## Example

```mermaid
graph LR
    subgraph Trust Boundary: Client
        A[Browser Extension] --> B[Client SDK]
    end

    subgraph Trust Boundary: Network
        B -->|TLS| C[API Gateway]
    end

    subgraph Trust Boundary: Server
        C --> D[Identity Service]
        C --> E[API Service]
        E --> F[(Database)]
        E --> G[Key Management]
    end

    style A fill:#e1f5fe
    style F fill:#fff3e0
```

## Required Elements

Include: components, data stores, external entities, data flows with protocols,
and trust boundaries.
