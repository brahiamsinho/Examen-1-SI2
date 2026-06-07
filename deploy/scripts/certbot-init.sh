#!/usr/bin/env bash
# Obtiene el primer certificado Let's Encrypt y activa HTTPS en el reverse-proxy.
# Ejecutar EN LA VM Azure (Ubuntu), desde la raíz del repo, con .env configurado.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  echo "ERROR: copiá .env.example → .env y configurá PUBLIC_DOMAIN y CERTBOT_EMAIL." >&2
  exit 1
fi

# shellcheck disable=SC1091
set -a && source .env && set +a

: "${PUBLIC_DOMAIN:?Definí PUBLIC_DOMAIN en .env (ej. oftalmologia-si2.westus3.cloudapp.azure.com)}"
: "${CERTBOT_EMAIL:?Definí CERTBOT_EMAIL en .env (email para Let's Encrypt)}"

chmod +x deploy/scripts/certbot-deploy-hook.sh deploy/scripts/certbot-renew.sh

COMPOSE=(docker compose -f docker-compose.yml -f deploy/docker-compose.azure.yml)

echo "==> Fase 1: stack HTTP (bootstrap) para desafío ACME..."
export NGINX_AZURE_CONF_TEMPLATE=./deploy/nginx/azure-http-bootstrap.conf.template
"${COMPOSE[@]}" up -d --build

echo "==> Esperando reverse-proxy..."
sleep 5

echo "==> Fase 2: Certbot certonly (webroot) para ${PUBLIC_DOMAIN}..."
"${COMPOSE[@]}" run --rm --entrypoint certbot certbot certonly \
  --webroot -w /var/www/certbot \
  -d "${PUBLIC_DOMAIN}" \
  --email "${CERTBOT_EMAIL}" \
  --agree-tos \
  --non-interactive \
  --no-eff-email

echo "==> Fase 3: activar plantilla HTTPS..."
export NGINX_AZURE_CONF_TEMPLATE=./deploy/nginx/azure-https.conf.template
"${COMPOSE[@]}" up -d --force-recreate reverse-proxy

echo ""
echo "Listo. Probá: https://${PUBLIC_DOMAIN}/"
echo "Renovación automática: contenedor emergencias_certbot (cada 12 h)."
