# =========================================================
# Dockerfile — Backend FastAPI
# Multi-stage: builder + runtime slim
# =========================================================

# ---- Stage 1: Builder ----
FROM python:3.11-slim AS builder

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar y pre-instalar dependencias (cache layer)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt

# ---- Stage 2: Runtime ----
FROM python:3.11-slim AS runtime

WORKDIR /app

# Instalar curl para el healthcheck de Docker
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Copiar librerías instaladas desde builder
COPY --from=builder /install /usr/local

# Copiar código fuente
COPY . .

# Usuario no-root por seguridad
RUN useradd -m -u 1001 appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

# uvicorn con reload en dev (sobreescrito por docker-compose.override.yml en prod)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
