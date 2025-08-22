# Enhanced Video Dubbing Tool with Lip Sync - Docker Image
# Multi-stage build for optimized production image

# Stage 1: Build stage with all build dependencies
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libffi-dev \
    libssl-dev \
    libsndfile1-dev \
    libasound2-dev \
    portaudio19-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Stage 2: Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    FLASK_APP=app_lipsync.py \
    FLASK_ENV=production

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    libasound2 \
    portaudio19-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create application user for security
RUN groupadd -r appuser && useradd -r -m -g appuser appuser

# Create application directory and required subdirectories
WORKDIR /app
RUN mkdir -p uploads outputs temp static/css static/js templates && \
    chown -R appuser:appuser /app

# Copy application files
COPY app_working.py .
COPY app_lipsync.py .
COPY templates/ templates/
COPY static/ static/
COPY requirements.txt .
#COPY LIPSYNC_IMPROVEMENTS.md .
#COPY LIPSYNC_SOLUTION_SUMMARY.md .

# Copy health check script
COPY docker/healthcheck.py .

# Set proper permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python healthcheck.py

# Default command
CMD ["python", "app_lipsync.py"]
