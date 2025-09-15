# BharatLawAI Backend Dockerfile - Railway Optimized
# Multi-stage build for optimized image size and Railway deployment

# ===========================================
# Stage 1: Builder stage for dependencies
# ===========================================
FROM python:3.11-slim as builder

# Set environment variables for Railway optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies needed to build wheels
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY langchain_rag_engine/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r /tmp/requirements.txt && \
    rm -f /tmp/requirements.txt

# ===========================================
# Stage 2: Runtime stage - Railway Optimized
# ===========================================
FROM python:3.11-slim

# Railway-specific environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/ \
    PORT=8000 \
    DEBIAN_FRONTEND=noninteractive

# Install minimal runtime system dependencies
RUN apt-get update && apt-get install -y \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for Railway security
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /

# Copy application code with proper structure
COPY langchain_rag_engine/ /.

# Create all necessary __init__.py files for proper Python package structure
RUN touch /__init__.py && \
    touch /api/__init__.py && \
    touch /db/__init__.py && \
    touch /rag/__init__.py && \
    touch /tools/__init__.py

# Copy essential data files (optimize for Railway - only copy what you need)
# For Railway, consider using Railway Volumes for large data files
COPY data/annotatedCentralActs/ /data/annotatedCentralActs/

RUN mkdir /app

# Create necessary directories with proper permissions
RUN mkdir -p /uploads/avatars /logs /data && \
    chown -R appuser:appuser /app

# Copy .env file if it exists (for Railway deployment)
# Note: Railway will inject environment variables automatically

# Switch to non-root user
USER appuser

# Railway-optimized health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Expose port (Railway will override this)
EXPOSE ${PORT:-8000}

# Railway-optimized startup command with better configuration

CMD ["sh", "-c", "echo '🚀 Starting BharatLawAI Backend...' && echo '📊 Port: '${PORT:-8000} && echo '🌍 Environment: '${ENVIRONMENT:-production} && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --loop uvloop --http h11 --access-log --log-level ${LOG_LEVEL:-info}"]

