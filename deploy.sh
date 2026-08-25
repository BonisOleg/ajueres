#!/usr/bin/env bash
# AJERES production deploy (VDS / Docker Compose).
# Usage on server: cd /var/www/ajeres && ./deploy.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

COMPOSE=(docker compose -f docker-compose.yml)
if [[ "${DEPLOY_SSL:-0}" == "1" ]]; then
  COMPOSE=(docker compose -f docker-compose.yml -f docker-compose.prod.yml)
fi

echo "==> $(date -Is) deploy start in $ROOT"

if [[ -d .git ]]; then
  echo "==> git pull"
  git fetch --all --prune
  git pull --ff-only origin "$(git rev-parse --abbrev-ref HEAD)"
fi

if [[ ! -f .env ]]; then
  echo "FATAL: missing .env — copy from .env.example and fill secrets"
  exit 1
fi

# shellcheck disable=SC1091
set -a
source .env
set +a

: "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD required in .env}"
: "${SECRET_KEY:?SECRET_KEY required in .env}"
: "${ALLOWED_HOSTS:?ALLOWED_HOSTS required in .env}"

echo "==> docker compose up --build -d"
"${COMPOSE[@]}" up -d --build --remove-orphans

echo "==> wait for web health"
for i in $(seq 1 60); do
  if "${COMPOSE[@]}" exec -T web python3 -c \
    "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz/', timeout=3)" \
    2>/dev/null; then
    echo "==> healthz OK"
    break
  fi
  if [[ "$i" -eq 60 ]]; then
    echo "FATAL: healthz timeout"
    "${COMPOSE[@]}" logs --tail=80 web
    exit 1
  fi
  sleep 3
done

echo "==> ensure superuser (idempotent)"
"${COMPOSE[@]}" exec -T web python3 - <<'PY'
from apps.core.ensure_superuser import ensure_default_superuser
ensure_default_superuser()
print("superuser ok")
PY

echo "==> status"
"${COMPOSE[@]}" ps
curl -sf -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1/healthz/ || true
echo "==> $(date -Is) deploy done"
