#!/usr/bin/env bash
# Renovación manual (también corre en el contenedor certbot). Opcional: cron diario en la VM.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

COMPOSE=(docker compose -f docker-compose.yml -f deploy/docker-compose.azure.yml)

"${COMPOSE[@]}" run --rm --entrypoint certbot certbot renew --webroot -w /var/www/certbot
docker exec emergencias_reverse_proxy nginx -s reload

echo "Renovación completada."
