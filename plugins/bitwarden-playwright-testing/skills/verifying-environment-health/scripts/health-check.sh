#!/bin/bash
# health-check.sh — Poll Bitwarden local dev services until all are ready.
#
# Usage:   ./health-check.sh <Service1> [Service2] ...
# Example: ./health-check.sh Api Identity Web
#
# Available service names:
#   Api, Identity, Billing, billing-pricing, Web, Admin,
#   Notifications, Events, Icons
#
# Override timeout (default 360s):
#   HEALTH_CHECK_TIMEOUT=60 ./health-check.sh Api
#
# Exit 0: all services ready.
# Exit 1: timeout or unknown service name.

get_url() {
  case "$1" in
    Api)             echo "http://localhost:4000/alive" ;;
    Identity)        echo "http://localhost:33656/alive" ;;
    Billing)         echo "http://localhost:44519/alive" ;;
    billing-pricing) echo "http://localhost:5082/alive" ;;
    Web)             echo "https://localhost:8080" ;;
    Admin)           echo "http://localhost:62911" ;;
    Notifications)   echo "http://localhost:61840" ;;
    Events)          echo "http://localhost:46273" ;;
    Icons)           echo "http://localhost:50024" ;;
    *)               echo "" ;;
  esac
}

TIMEOUT="${HEALTH_CHECK_TIMEOUT:-360}"

if [ $# -eq 0 ]; then
  echo "Usage: $0 <Service1> [Service2] ..."
  echo "Available: Api, Identity, Billing, billing-pricing, Web, Admin (Bitwarden Portal), Notifications, Events, Icons"
  echo "Override timeout: HEALTH_CHECK_TIMEOUT=60 $0 Api"
  exit 1
fi

# Validate all names upfront and build a deduplicated space-separated list
SERVICES=""
for svc in "$@"; do
  url=$(get_url "$svc")
  if [ -z "$url" ]; then
    echo "Unknown service: $svc"
    echo "Available: Api, Identity, Billing, billing-pricing, Web, Admin (Bitwarden Portal), Notifications, Events, Icons"
    exit 1
  fi
  case " $SERVICES " in
    *" $svc "*) ;;  # already in list, skip
    *) SERVICES="$SERVICES $svc" ;;
  esac
done
SERVICES="${SERVICES# }"  # trim leading space

TOTAL=$(echo "$SERVICES" | wc -w | tr -d ' ')
READY=""
READY_COUNT=0
START=$SECONDS

echo "Waiting for $TOTAL service(s): $SERVICES (timeout: ${TIMEOUT}s)"

while true; do
  for svc in $SERVICES; do
    # Skip if already marked ready
    case " $READY " in
      *" $svc "*) continue ;;
    esac

    URL=$(get_url "$svc")
    STATUS=$(curl -k -s -o /dev/null -w "%{http_code}" --max-time 3 "$URL" 2>/dev/null)

    if [ "$STATUS" = "200" ] || [ "$STATUS" = "302" ]; then
      READY="$READY $svc"
      READY_COUNT=$((READY_COUNT + 1))
      echo "  ✅ $svc ready ($(( SECONDS - START ))s elapsed)"
    fi
  done

  # All services ready — exit immediately
  if [ "$READY_COUNT" -ge "$TOTAL" ]; then
    break
  fi

  # Timed out — report failures and exit
  if [ $((SECONDS - START)) -ge "$TIMEOUT" ]; then
    echo "⚠️  Timeout after ${TIMEOUT}s. Not ready:"
    for svc in $SERVICES; do
      case " $READY " in
        *" $svc "*) ;;
        *)
          URL=$(get_url "$svc")
          STATUS=$(curl -k -s -o /dev/null -w "%{http_code}" --max-time 3 "$URL" 2>/dev/null)
          echo "  ❌ $svc — HTTP $STATUS"
          ;;
      esac
    done
    exit 1
  fi

  # Print which services are still pending before sleeping
  PENDING=""
  for svc in $SERVICES; do
    case " $READY " in
      *" $svc "*) ;;
      *) PENDING="$PENDING $svc" ;;
    esac
  done
  echo "  ⏳ Still waiting: ${PENDING# } ($(( SECONDS - START ))s elapsed)"
  sleep 5
done

echo "✅ All $TOTAL service(s) ready ($(( SECONDS - START ))s total)"
