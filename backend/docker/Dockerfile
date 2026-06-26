# ── Build stage ──────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# System deps needed to compile some Python wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libssl-dev \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.11.8 /uv /uvx /bin/

COPY pyproject.toml uv.lock* ./
COPY modules/web_search/ modules/web_search/
COPY modules/core/ modules/core/
RUN UV_LINK_MODE=copy uv sync --no-dev

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

# Runtime system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl-dev \
    curl \
    libxcb1 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libglib2.0-0 \
    libgl1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Use virtualenv Python and scripts at runtime
ENV PATH=/app/.venv/bin:$PATH

# Copy application source
COPY . .

# Persistent data directories (mounted as volumes at runtime)
RUN mkdir -p \
    data/database \
    data/files \
    data/vector_database/chromadb \
    data/embedding_models \
    data/checkpoints \
    data/ssl_certs

# ── Configuration ─────────────────────────────────────────────────────────────
ENV HOST=0.0.0.0
ENV PORT=8001
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8001

# ── Health check ──────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# ── Entrypoint ────────────────────────────────────────────────────────────────
CMD ["python", "backend/run_server.py"]
