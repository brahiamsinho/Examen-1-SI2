# Sesión 2026-06-04 — Optimización Docker

## Objetivo

Aplicar mejoras de buenas prácticas y rendimiento en build/arranque del stack Docker.

## Cambios

| Área | Antes | Después |
|------|--------|---------|
| SMTP dev | Mailhog ~572 MB | Mailpit `v1.22`, alias `mailhog` |
| Initdb | hasta 0017 | +0018, +0019, +99_register_sql_migrations |
| Bootstrap | re-ejecutaba SQL idempotente | salta archivos ya en `app_sql_migrations` |
| frontend | `depends_on: backend` | `condition: service_healthy` |
| Stripe | warnings Compose si vacío | `${STRIPE_*:-}` |
| ai-inference | single-stage, root | multi-stage, `aiuser`, sin `git` |
| override dev | sin nota Windows | aviso OneDrive + bind mount lento |

## Archivos tocados

- `docker-compose.yml`
- `docker-compose.override.yml`
- `backend/migrations/99_register_sql_migrations.sql` (nuevo)
- `services/ai-inference/Dockerfile`
- `.env.example`
- `docs/ai/DOCKER_BUILD_OPTIMIZATION.md`

## Cómo probar

```powershell
docker compose down
docker compose pull mailpit
docker compose up -d --build
docker compose ps
```

BD **existente** (volumen `emergencias_postgres_data`): initdb no se re-ejecuta; bootstrap sigue aplicando solo SQL no registrado en `app_sql_migrations`.

## Pendiente opcional

- Clonar repo fuera de OneDrive si `--reload` va lento.
- Fase B BuildKit cache en CI (`DOCKER_BUILD_OPTIMIZATION.md`).
