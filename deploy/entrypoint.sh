#!/usr/bin/env bash
set -euo pipefail

echo "==> Waiting for PostgreSQL..."
python3 <<'PY'
import os
import sys
import time

url = os.environ.get("DATABASE_URL", "").strip()
if not url or not url.startswith("postgres"):
    print("==> No DATABASE_URL (postgres) — skip wait")
    sys.exit(0)

import psycopg

for i in range(30):
    try:
        with psycopg.connect(url) as conn:
            conn.execute("SELECT 1")
        print("==> DB ready")
        break
    except Exception as exc:
        print(f"==> DB not ready ({i + 1}/30): {exc}")
        time.sleep(2)
else:
    print("FATAL: DB not ready")
    sys.exit(1)
PY

echo "==> Django migrate + legal pages + hero guard + collectstatic"
python3 manage.py migrate --noinput
python3 manage.py ensure_legal
python3 manage.py fix_hero_image
python3 manage.py collectstatic --noinput

_static_count=$(find "${STATIC_ROOT:-/app/staticfiles}" -type f 2>/dev/null | wc -l | tr -d ' ')
echo "==> static files: ${_static_count}"
if [ "${_static_count:-0}" -lt 10 ]; then
  echo "WARN: staticfiles count low — перевір STATIC_ROOT і collectstatic"
fi

exec "$@"
