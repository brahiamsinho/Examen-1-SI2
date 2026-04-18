# syntax=docker/dockerfile:1
# Backend FastAPI — multi-stage, slim bookworm, pip cache mount
# Deps: wheels only (asyncpg/crypto have manylinux wheels) → no apt build chain

FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.11-slim-bookworm AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY --from=builder /install /usr/local
COPY . .

RUN useradd -m -u 1001 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

ENV UVICORN_PORT=8000
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${UVICORN_PORT:-8000}"]
