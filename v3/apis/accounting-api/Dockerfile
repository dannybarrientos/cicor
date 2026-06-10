# ============================================================
# CICOR ERP - Accounting API Dockerfile
# Base:    python:3.11-slim
# Build:   Multi-stage para minimizar tamaño de imagen final
# Usuario: non-root (cicor, UID 1000) — cumple PSP cicor-restricted
# ============================================================

# ── Stage 1: Builder ─────────────────────────────────────────
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: Runtime ─────────────────────────────────────────
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

# Crear usuario non-root UID/GID 1000 — requerido por PSP cicor-restricted
RUN groupadd --gid 1000 cicor \
    && useradd --uid 1000 --gid cicor --no-create-home --shell /bin/false cicor

COPY --chown=cicor:cicor . .

USER cicor

EXPOSE 8000

# # #HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
# # #    CMD curl -f http://localhost:8000/health/live || exit 1

CMD ["uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "2", \
     "--log-level", "info", \
     "--access-log"]
