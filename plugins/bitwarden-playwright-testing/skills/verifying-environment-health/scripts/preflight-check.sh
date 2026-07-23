#!/usr/bin/env bash
#
# preflight-check.sh
#
# Verify environmental preconditions for the bitwarden-playwright-testing
# pipeline. Exits 0 if all preconditions are met; exits non-zero with a
# structured message naming what is missing and how to resolve it.
#
# The Bitwarden dev environment can be started via either the legacy
# Docker Compose workflow (server/dev/docker-compose.yml) or the newer
# .NET Aspire AppHost workflow (server/AppHost). The two workflows use
# different container names for the same logical service, so for each
# required service the script accepts either naming pattern.
#
# Compose names look like:  bitwardenserver-<service>-1
# Aspire names look like:   <service>-<random-suffix>

set -u

# 1. Docker daemon reachable
if ! docker info >/dev/null 2>&1; then
  cat >&2 <<'EOF'
Preflight check failed:
  - Docker daemon is not reachable.
    Resolve: start Docker Desktop (or the docker service), then re-run the pipeline.
EOF
  exit 1
fi

# 2. Required Bitwarden dev containers.
# Each row: <human label>|<compose name regex>|<aspire name regex>
REQUIRED_SERVICES=(
  "MSSQL database|-mssql-|^mssql-"
  "Mailcatcher email|-mail-|^mailcatcher-"
  "Azurite storage|-storage-|^azurite-"
)

RUNNING_NAMES=$(docker ps --format '{{.Names}}')

MISSING=""
for entry in "${REQUIRED_SERVICES[@]}"; do
  IFS='|' read -r label compose_pat aspire_pat <<< "$entry"
  if ! grep -qE -- "${compose_pat}|${aspire_pat}" <<< "${RUNNING_NAMES}"; then
    MISSING+="  - ${label}: no running container matched '${compose_pat}' (Compose) or '${aspire_pat}' (Aspire)."$'\n'
  fi
done

if [[ -n "${MISSING}" ]]; then
  {
    echo "Preflight check failed:"
    printf "%s" "${MISSING}"
    echo "    Resolve: start the Bitwarden dev environment. Either:"
    echo "      Compose: cd <bitwarden-root>/server/dev && docker compose up -d"
    echo "      Aspire:  cd <bitwarden-root>/server/AppHost && dotnet run"
  } >&2
  exit 1
fi

echo "Preflight check passed."
exit 0
