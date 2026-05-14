#!/usr/bin/env bash
set -euo pipefail

DB_HOST="${POSTGRES_HOST:-postgres}"
DB_PORT="${POSTGRES_PORT:-5432}"

echo "==> Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT}..."
MAX_WAIT=60
i=0
until python -c "
import psycopg2, os, sys
try:
    conn = psycopg2.connect(
        host=os.environ.get('POSTGRES_HOST','postgres'),
        port=int(os.environ.get('POSTGRES_PORT','5432')),
        dbname=os.environ.get('POSTGRES_DB','odoo_monitor'),
        user=os.environ.get('POSTGRES_USER','odoo_monitor'),
        password=os.environ.get('POSTGRES_PASSWORD',''),
        connect_timeout=3,
    )
    conn.close()
except Exception:
    sys.exit(1)
" 2>/dev/null; do
    i=$((i + 1))
    if [ "$i" -ge "$MAX_WAIT" ]; then
        echo "ERROR: PostgreSQL not ready after ${MAX_WAIT}s" >&2
        exit 1
    fi
    sleep 1
done
echo "PostgreSQL ready (${i}s)"

echo "==> Running Alembic migrations..."
PYTHONPATH=/app alembic upgrade head

echo "==> Seeding initial admin user..."
PYTHONPATH=/app python /app/scripts/seed.py || echo "Seed skipped or already done"

echo "==> Starting Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
