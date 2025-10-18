# Backend Dockerfile for Django + DRF
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn psycopg2-binary

# Copy project files
COPY . .

# Create staticfiles directory
RUN mkdir -p staticfiles

# Create entrypoint script
COPY <<EOF /app/entrypoint.sh
#!/bin/bash
set -e

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn on port \${PORT:-8000}..."
exec gunicorn backend.wsgi:application --bind 0.0.0.0:\${PORT:-8000} --workers 4 --timeout 120 --access-logfile - --error-logfile -
EOF

RUN chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 8000

# Run the entrypoint script
CMD ["/app/entrypoint.sh"]
