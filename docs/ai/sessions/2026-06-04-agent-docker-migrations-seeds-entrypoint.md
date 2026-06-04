# Sesión 2026-06-04 — Migraciones y seeds automáticos en Docker entrypoint

## Objetivo

Automatizar migraciones (Alembic + SQL) y seeds al levantar el contenedor `backend`, sin pasos manuales `alembic stamp` / `python -m app.seeds`.

## Implementación

- `backend/Dockerfile` ENTRYPOINT → `python -m app.db.docker_bootstrap` → `exec uvicorn`.
- `backend/app/db/docker_bootstrap.py`:
  - Espera Postgres.
  - Si hay esquema (`roles`) sin `alembic_version` → `alembic stamp head` (BD creada por initdb).
  - Si no → `alembic upgrade head`.
  - Aplica `backend/migrations/*.sql` (excepto `init.sql`) con tabla `app_sql_migrations` (idempotente).
- `backend/app/seeds/runner.py` — lógica compartida seeds (entrypoint, lifespan, CLI).
- Variables: `RUN_MIGRATIONS_ON_START`, `RUN_SEEDS_ON_START`, `RUN_SEEDS_IN_LIFESPAN`.
- `docker-compose.yml`: migraciones on, seeds en entrypoint (`RUN_SEEDS_IN_LIFESPAN=false`).
- `docker-compose.override.yml`: `SEED_*_ON_START=true` para demo dev.

## Probar

```bash
docker compose up -d --build backend
docker compose logs backend | head -40
docker compose exec backend alembic current
```

Login admin: `patricio.mendez@sc-demo.test` / `scdemo1`.
