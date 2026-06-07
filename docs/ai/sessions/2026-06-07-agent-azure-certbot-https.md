# Sesión 2026-06-07 — Azure VM HTTPS con Certbot

## Objetivo
Publicar el stack Docker en VM Azure con hostname `oftalmologia-si2.westus3.cloudapp.azure.com` y TLS Let's Encrypt.

## Implementado
- `deploy/docker-compose.azure.yml` — reverse-proxy + certbot; cierra puertos públicos db/backend/mailpit.
- Nginx bootstrap (HTTP + ACME) y HTTPS (redirect + TLS).
- Scripts init/renew + hook reload nginx.
- `docs/ai/DEPLOYMENT_AZURE.md`, `.env.example` ampliado.

## Aclaración
- **DNS** = etiqueta en IP pública Azure (Portal), no Certbot.
- **Certbot** = certificado HTTPS cuando el dominio apunta a la VM y :80 está abierto.

## Pendiente
- Correr `certbot-init.sh` en la VM de producción y validar CORS/URLs en `.env`.
