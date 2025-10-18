#!/usr/bin/env bash
set -euo pipefail

# Default to 0 workers on low memory; Railway sets PORT
: "${PORT:=8000}"
: "${WEB_CONCURRENCY:=2}"
: "${GUNICORN_TIMEOUT:=60}"

# Ensure database is ready (Postgres)
python - <<'PY'
import os, time, psycopg2
from urllib.parse import urlparse

db_url = os.environ.get('DATABASE_URL')
if not db_url:
    # Fall back to individual env vars (local dev or alt config)
    host = os.environ.get('DB_HOST', 'localhost')
    port = os.environ.get('DB_PORT', '5432')
    user = os.environ.get('DB_USER', 'postgres')
    password = os.environ.get('DB_PASSWORD', '')
    name = os.environ.get('DB_NAME', 'postgres')
    dsn = f"dbname='{name}' user='{user}' host='{host}' port='{port}' password='{password}' sslmode='prefer'"
else:
    # Railway provides DATABASE_URL
    u = urlparse(db_url)
    sslmode = 'require'
    dsn = f"dbname='{u.path.lstrip('/')}' user='{u.username}' host='{u.hostname}' port='{u.port or 5432}' password='{u.password or ''}' sslmode='{sslmode}'"

for i in range(30):
    try:
        conn = psycopg2.connect(dsn)
        conn.close()
        print('Database is ready')
        break
    except Exception as e:
        print(f'Waiting for database... ({i+1}/30):', e)
        time.sleep(1)
else:
    print('Database is not ready after waiting, continuing anyway...')
PY

# Run database migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Start server via Gunicorn
exec gunicorn backend.wsgi:application \
  --bind 0.0.0.0:"${PORT}" \
  --workers "${WEB_CONCURRENCY}" \
  --timeout "${GUNICORN_TIMEOUT}" \
  --access-logfile '-' \
  --error-logfile '-'