# Backend Dockerfile for Django + DRF + Channels (ASGI)
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
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files (works whether build context is repo root or backend directory)
COPY . .

# Install Python dependencies from whichever requirements file is available
RUN pip install --upgrade pip && \
    if [ -f backend/requirements.txt ]; then \
        pip install --no-cache-dir -r backend/requirements.txt; \
    else \
        pip install --no-cache-dir -r requirements.txt; \
    fi

# Ensure entrypoint is executable
RUN chmod +x /app/entrypoint.sh

# Create staticfiles and media directories
RUN mkdir -p staticfiles media

# Expose port
EXPOSE 8000

# Run the entrypoint script
CMD ["/app/entrypoint.sh"]

