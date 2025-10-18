#!/bin/bash
set -e

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Non-interactive admin creation for CI/hosted environments (Railway)
# Will run only if ADMIN_USERNAME and ADMIN_PASSWORD are set in env
if [ -n "${ADMIN_USERNAME:-}" ] && [ -n "${ADMIN_PASSWORD:-}" ]; then
    echo "Creating admin user (non-interactive)..."
    # Run the script which supports non-interactive mode via env vars
    python create_admin.py || echo "Admin creation script exited with non-zero status; continuing."
else
    echo "ADMIN_USERNAME/ADMIN_PASSWORD not set; skipping admin creation."
fi

echo "Starting Gunicorn on port ${PORT:-8000}..."
exec gunicorn backend.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
