# Enterprise Flask Authorization Server - Production Dockerfile
# Multi-stage build for optimized image size and security

# Build stage
FROM python:3.13-slim-bookworm AS builder

# Set build arguments
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

# Add metadata labels
LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="Enterprise Flask Authorization Server" \
      org.label-schema.description="Enterprise-grade Flask API with JWT authentication and RBAC" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/soorajnraju/flask-auth-server" \
      org.label-schema.vendor="Enterprise Solutions" \
      org.label-schema.version=$VERSION \
      org.label-schema.schema-version="1.0"

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements first for better caching
COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Production stage
FROM python:3.13-slim-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    FLASK_APP=app \
    FLASK_ENV=production

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r flask && useradd -r -g flask flask

# Create application directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY --chown=flask:flask . .

# Create directories for logs and uploads
RUN mkdir -p /app/logs /app/uploads && \
    chown -R flask:flask /app/logs /app/uploads

# Install netcat for health checks
RUN apt-get update && apt-get install -y --no-install-recommends netcat && \
    rm -rf /var/lib/apt/lists/*

# Set proper permissions
RUN chmod -R 755 /app && \
    chmod +x /app/docker-entrypoint.sh

# Switch to non-root user
USER flask

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Use entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]