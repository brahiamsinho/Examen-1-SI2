# Inferencia IA (Whisper + Silero VAD + OpenCV). Perfil Docker Compose: `ai`.
# Build: `context` = este directorio (ver docker-compose.yml).
FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.11-slim-bookworm AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    libheif1 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1001 aiuser

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    WHISPER_MODEL_SIZE=small \
    HOME=/home/aiuser

COPY --from=builder /install /usr/local
COPY --chown=aiuser:aiuser app /app/app

USER aiuser

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
