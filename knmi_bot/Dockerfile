# Use official Python slim image based on Debian
FROM python:3.12-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # pip
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Create a non-privileged user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# Install security updates and required packages
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN pip install --no-cache-dir --upgrade pip

# Copy only requirements file first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Multi-stage build for smaller final image
FROM python:3.12-slim AS runtime

# Copy virtual environment from builder
COPY --from=builder /app /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Set work directory
WORKDIR /app

# Create non-privileged user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set ownership and permissions
RUN chown -R appuser:appuser /app && \
    chmod -R 550 /app

# Switch to non-root user
USER appuser

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD ps aux | grep python | grep -v grep || exit 1

# Start application
CMD ["python", "bot.py"]
