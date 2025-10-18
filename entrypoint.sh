#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Starting Django Backend Deployment on Railway..."

# Default to 0 workers on low memory; Railway sets PORT
: "${PORT:=8000}"
: "${WEB_CONCURRENCY:=2}"
: "${GUNICORN_TIMEOUT:=120}"

echo "📡 Port: $PORT"
echo "👷 Workers: $WEB_CONCURRENCY"

# Check if DATABASE_URL is set (Railway provides this)
if [ -z "${DATABASE_URL:-}" ]; then
    echo "❌ ERROR: DATABASE_URL is not set!"
    echo "   Please add PostgreSQL database to your Railway project."
    echo "   Railway Dashboard → + New → Database → Add PostgreSQL"
    exit 1
fi

echo "✅ DATABASE_URL found"

# Ensure database is ready (Postgres)
echo "⏳ Waiting for database connection..."
python - <<'PY'
import os, time
from urllib.parse import urlparse
import psycopg2

db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print('❌ ERROR: DATABASE_URL not set')
    raise SystemExit(1)

u = urlparse(db_url)
sslmode = 'require'
print(f"🔗 Connecting to database at {u.hostname}:{u.port or 5432}")

for i in range(30):
    try:
        conn = psycopg2.connect(
            dbname=u.path.lstrip('/'),
            user=u.username,
            password=u.password or '',
            host=u.hostname,
            port=u.port or 5432,
            sslmode=sslmode,
        )
        conn.close()
        print('✅ Database is ready!')
        break
    except Exception as e:
        print(f"⏳ Waiting for database... ({i+1}/30): {str(e)[:100]}")
        time.sleep(1)
else:
    print('⚠️  Database is not ready after 30 seconds, continuing anyway...')
PY

echo "📦 Running database migrations..."
python manage.py migrate --noinput

echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

echo "🚀 Starting Gunicorn server..."
exec gunicorn backend.wsgi:application \
  --bind 0.0.0.0:"${PORT}" \
  --workers "${WEB_CONCURRENCY}" \
  --timeout "${GUNICORN_TIMEOUT}" \
  --access-logfile '-' \
  --error-logfile '-' \
  --log-level info