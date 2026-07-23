# Bitwarden Service Dependency Reference

## Resolving `<bitwarden git root>`

`<bitwarden git root>` is the directory containing the Bitwarden `clients/` and `server/` checkouts — typically the current working directory. When resolving a repo path below, first try it relative to the current working directory. If it isn't there, attempt to locate the repo using your own reasoning (e.g. check nearby directories). If it still can't be found, **stop and alert the user that the repository folder could not be located** rather than guessing.

## Service Map

### Web Vault Frontend
- **Port**: 8080
- **URL**: `https://localhost:8080`
- **Technology**: Angular (NX/Webpack)
- **Repo**: `<bitwarden git root>/clients/`
- **Health check**: `https://localhost:8080` (200 response)
- **Required by**: any change to `clients/apps/web/**` or `clients/libs/**`, and any server-side API change that surfaces in the web UI

### Api Service
- **Port**: 4000
- **URL**: `http://localhost:4000`
- **Technology**: .NET
- **Repo**: `<bitwarden git root>/server/src/Api/`
- **Health check**: `http://localhost:4000/alive`
- **Required by**: web vault testing (handles vault data), any `server/src/Api/**` change

### Identity Service
- **Port**: 33656
- **URL**: `http://localhost:33656`
- **Technology**: .NET
- **Repo**: `<bitwarden git root>/server/src/Identity/`
- **Health check**: `http://localhost:33656/alive`
- **Required by**: any flow involving login/authentication, always required alongside Api for web vault

### Bitwarden Portal
- **Port**: 62911
- **URL**: `http://localhost:62911`
- **Technology**: .NET Razor views (NOT Angular)
- **Repo**: `<bitwarden git root>/server/src/Admin/`
- **Health check**: `http://localhost:62911` (200 response)
- **Required by**: `server/src/Admin/**` changes only
- **Note**: The Bitwarden Portal is a standalone .NET web app. No frontend build is needed. Playwright navigates directly to port 62911.

### Billing Service
- **Port**: 44519
- **URL**: `http://localhost:44519`
- **Technology**: .NET
- **Repo**: `<bitwarden git root>/server/src/Billing/`
- **Health check**: `http://localhost:44519/alive`
- **Required by**: `server/src/Billing/**` changes, billing UI flows

### billing-pricing Service
- **Port**: 7088 (HTTPS), 5082 (HTTP)
- **URL**: `https://localhost:7088`
- **Technology**: .NET
- **Repo**: `<bitwarden git root>/billing-pricing/`
- **Health check**: `http://localhost:5082/alive` (200 response) — use HTTP; the HTTPS port (7088) has SSL errors in dev
- **Required by**: `billing-pricing/src/**` changes only — never triggered by routes or pricing UI flows
- **Note**: Separate repo — does not share `Bitwarden.sln`. Does not need the pre-build step and does not use `--no-build`. Most developers use a QA cloud environment for pricing; only require this service when the billing-pricing repo has local code changes on the branch.

---

## Optional Infrastructure Services

These services are **not required to start upfront** but may be needed if tests fail with errors suggesting a dependent service is unavailable. Start them on demand when you observe that failure.

### Notifications Service
- **Port**: 61840
- **URL**: `http://localhost:61840`
- **Technology**: .NET
- **Repo**: `<bitwarden git root>/server/src/Notifications/`
- **Health check**: `http://localhost:61840` (200 response)
- **Start if**: tests fail with real-time sync errors, push notification failures, or vault sync not reflecting changes

### Events Service
- **Port**: 46273
- **URL**: `http://localhost:46273`
- **Technology**: .NET
- **Repo**: `<bitwarden git root>/server/src/Events/`
- **Health check**: `http://localhost:46273` (200 response)
- **Start if**: tests fail involving audit logs, organization event history, or event recording flows

### Icons Service
- **Port**: 50024
- **URL**: `http://localhost:50024`
- **Technology**: .NET
- **Repo**: `<bitwarden git root>/server/src/Icons/`
- **Health check**: `http://localhost:50024` (200 response)
- **Start if**: tests fail involving favicon/icon display for vault items, or icon-related network errors appear in the browser console
