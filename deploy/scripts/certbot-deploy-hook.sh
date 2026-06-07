#!/bin/sh
# Recarga nginx del reverse-proxy tras renovar certificados (Certbot deploy hook).
set -eu
if command -v docker >/dev/null 2>&1; then
  docker exec emergencias_reverse_proxy nginx -s reload 2>/dev/null || true
fi
