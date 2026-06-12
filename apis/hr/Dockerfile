# ============================================================
# CICOR ERP - HR API (Recursos Humanos)
# Imagen: Python 3.11 slim | Puerto: 8000 (interno)
# ============================================================

FROM python:3.11-slim AS base

# ── Seguridad: usuario no-root ─────────────────────────────
RUN groupadd -r cicor && useradd -r -g cicor -u 1000 cicor

WORKDIR /app

# ── Dependencias del sistema ───────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev \
        gcc \
        curl \
    && rm -rf /var/lib/apt/lists/*

# ── Dependencias Python ────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── Código fuente ──────────────────────────────────────────
COPY --chown=cicor:cicor . .

# ── Cambiar a usuario no-root ──────────────────────────────
USER cicor

# ── Health Check ───────────────────────────────────────────
# # #HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
# # #    CMD curl -f http://localhost:8000/health/live || exit 1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
