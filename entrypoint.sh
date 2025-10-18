#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Starting Django Backend with ASGI (WebSocket support)..."

# Default settings
: "${PORT:=8000}"
: "${WEB_CONCURRENCY:=2}"
: "${GUNICORN_TIMEOUT:=120}"
: "${USE_ASGI:=true}"

echo "📡 Port: $PORT"
echo "👷 Workers: $WEB_CONCURRENCY"
echo "⚡ ASGI Mode: $USE_ASGI"

# Check if DATABASE_URL is set
if [ -z "${DATABASE_URL:-}" ]; then
    echo "⚠️  WARNING: DATABASE_URL is not set!"
    echo "   Using default SQLite database for development."
fi

# Wait for database if using PostgreSQL
if [ -n "${DATABASE_URL:-}" ]; then
    echo "⏳ Waiting for database connection..."
    python - <<'PY'
import os, time
from urllib.parse import urlparse
import psycopg2

db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print('Using SQLite')
    raise SystemExit(0)

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
fi

# Wait for Redis if REDIS_URL is set
if [ -n "${REDIS_URL:-}" ]; then
    echo "⏳ Waiting for Redis connection..."
    for i in {1..30}; do
        if python -c "import redis; r = redis.from_url('${REDIS_URL}'); r.ping()" 2>/dev/null; then
            echo "✅ Redis is ready!"
            break
        fi
        echo "⏳ Waiting for Redis... ($i/30)"
        sleep 1
    done
fi

echo "📦 Running database migrations..."
python manage.py migrate --noinput

echo "🛠️  Fixing class levels (auto-mapping old to new)..."
python manage.py fix_class_levels || echo "⚠️  fix_class_levels command failed or not needed. Continuing..."

echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

# Start server based on USE_ASGI flag
if [ "$USE_ASGI" = "true" ]; then
    echo "🚀 Starting Daphne ASGI server (WebSocket support)..."
    exec daphne -b 0.0.0.0 -p "${PORT}" backend.asgi:application
else
    echo "🚀 Starting Gunicorn WSGI server (no WebSocket)..."
    exec gunicorn backend.wsgi:application \
      --bind 0.0.0.0:"${PORT}" \
      --workers "${WEB_CONCURRENCY}" \
      --timeout "${GUNICORN_TIMEOUT}" \
      --access-logfile '-' \
      --error-logfile '-' \
      --log-level info
fi
