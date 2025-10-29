# Multi-stage build for production optimization
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Toggle full vs slim requirements at build time
ARG USE_FULL_REQS=0

# Copy both requirements sets
COPY requirements-server.txt ./requirements-server.txt
COPY requirements.txt ./requirements-full.txt

# Select which requirements to install
RUN if [ "$USE_FULL_REQS" = "1" ]; then \
      cp requirements-full.txt requirements.txt ; \
    else \
      cp requirements-server.txt requirements.txt ; \
    fi && \
    pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder to appuser's home
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY app ./app

# Copy scripts for DB initialization and seeding
COPY scripts ./scripts

# Copy entrypoint script
COPY docker-entrypoint.sh ./docker-entrypoint.sh
RUN chmod +x ./docker-entrypoint.sh

# Copy alembic.ini for database migrations
COPY app/alembic.ini ./alembic.ini

# Create necessary directories
RUN mkdir -p /app/data/vectorstore /app/logs /app/models && \
    chown -R appuser:appuser /app

# Add local bin to PATH for pip packages (use appuser's home)
ENV PATH=/home/appuser/.local/bin:$PATH

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check (using Python to avoid curl permission issues)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run application with production settings using entrypoint
CMD ["/app/docker-entrypoint.sh"]



