# Bitwarden Service Dependency Reference

## About `<bitwarden git root>`

In the `Repo` fields below, `<bitwarden git root>` denotes the directory containing the Bitwarden `clients/` and `server/` checkouts. The mapping procedure receives an explicit `<repo-path>` for each affected repo, so it never resolves this itself; the notation only documents where each service's code lives.

The `Required by (paths):` globs are keyed to each repo's **canonical name** (`clients`, `server`, `billing-pricing`), e.g. `server/src/Admin/**`. The mapping skill prefixes each repo-relative diff path with its canonical name before matching, so a path carrying any other prefix — for example a non-canonical checkout directory such as `bw-server` — matches none of these globs and would silently under-report the path-based services.

## Service Map

### Web Vault Frontend

- **Health-check name**: `Web`
- **Port**: 8080
- **URL**: `https://localhost:8080`
- **Technology**: Angular (NX/Webpack)
- **Repo**: `<bitwarden git root>/clients/`
- **Health check**: `https://localhost:8080` (200 response)
- **Required by (paths)**: any change to `clients/apps/web/**` or `clients/libs/**`
- **Required by (routes)**: any test whose routes include a web vault URL (`https://localhost:8080`); a server-side API change that surfaces in the web UI is covered here, since it is exercised through a web vault route

### Api Service

- **Health-check name**: `Api`
- **Port**: 4000
- **URL**: `http://localhost:4000`
- **Technology**: .NET
- **Repo**: `<bitwarden git root>/server/src/Api/`
- **Health check**: `http://localhost:4000/alive`
- **Required by (paths)**: any `server/src/Api/**` change
- **Required by (routes)**: web vault testing — any web vault route requires Api, which handles vault data

### Identity Service

- **Health-check name**: `Identity`
- **Port**: 33656
- **URL**: `http://localhost:33656`
- **Technology**: .NET
- **Repo**: `<bitwarden git root>/server/src/Identity/`
- **Health check**: `http://localhost:33656/alive`
- **Required by (paths)**: `server/src/Identity/**`
- **Required by (routes)**: any flow involving login/authentication; always required alongside Api for web vault

### Bitwarden Portal

- **Health-check name**: `Admin`
- **Port**: 62911
- **URL**: `http://localhost:62911`
- **Technology**: .NET Razor views (NOT Angular)
- **Repo**: `<bitwarden git root>/server/src/Admin/`
- **Health check**: `http://localhost:62911` (200 response)
- **Required by (paths)**: `server/src/Admin/**` changes
- **Required by (routes)**: any test whose routes include an Admin portal URL (`http://localhost:62911`)
- **Note**: The Bitwarden Portal is a standalone .NET web app. No frontend build is needed. Playwright navigates directly to port 62911.

### Billing Service

- **Health-check name**: `Billing`
- **Port**: 44519
- **URL**: `http://localhost:44519`
- **Technology**: .NET
- **Repo**: `<bitwarden git root>/server/src/Billing/`
- **Health check**: `http://localhost:44519/alive`
- **Required by (paths)**: `server/src/Billing/**` changes
- **Required by (routes)**: any test whose routes include `/billing/` or `/organizations/:organizationId/billing/**` (e.g. `/organizations/:organizationId/billing/subscription`)

### billing-pricing Service

- **Health-check name**: `billing-pricing`
- **Port**: 7088 (HTTPS), 5082 (HTTP)
- **URL**: `https://localhost:7088`
- **Technology**: .NET
- **Repo**: `<bitwarden git root>/billing-pricing/`
- **Health check**: `http://localhost:5082/alive` (200 response) — use HTTP; the HTTPS port (7088) has SSL errors in dev
- **Required by (paths)**: `billing-pricing/src/**` changes only
- **Required by (routes)**: none — never triggered by routes or pricing UI flows
- **Note**: Separate repo — does not share `Bitwarden.sln`. Does not need the pre-build step and does not use `--no-build`. Most developers use a QA cloud environment for pricing; only require this service when the billing-pricing repo has local code changes on the branch.

---

## Optional Infrastructure Services

These services are **not required to start upfront** but may be needed if tests fail with errors suggesting a dependent service is unavailable. Start them on demand when you observe that failure.

### Notifications Service

- **Health-check name**: `Notifications`
- **Port**: 61840
- **URL**: `http://localhost:61840`
- **Technology**: .NET
- **Repo**: `<bitwarden git root>/server/src/Notifications/`
- **Health check**: `http://localhost:61840` (200 response)
- **Start if**: tests fail with real-time sync errors, push notification failures, or vault sync not reflecting changes

### Events Service

- **Health-check name**: `Events`
- **Port**: 46273
- **URL**: `http://localhost:46273`
- **Technology**: .NET
- **Repo**: `<bitwarden git root>/server/src/Events/`
- **Health check**: `http://localhost:46273` (200 response)
- **Start if**: tests fail involving audit logs, organization event history, or event recording flows

### Icons Service

- **Health-check name**: `Icons`
- **Port**: 50024
- **URL**: `http://localhost:50024`
- **Technology**: .NET
- **Repo**: `<bitwarden git root>/server/src/Icons/`
- **Health check**: `http://localhost:50024` (200 response)
- **Start if**: tests fail involving favicon/icon display for vault items, or icon-related network errors appear in the browser console
