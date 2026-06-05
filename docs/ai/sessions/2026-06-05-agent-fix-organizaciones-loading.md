# Sesión 2026-06-05 — Fix organizaciones y planes-precios admin loading

## Problema
- `/admin/panel/organizaciones` — "Cargando…" con `GET /api/admin/tenants` 200 OK.
- `/admin/panel/planes-precios` — "Cargando planes…" con `GET /api/admin/pricing-plans` 200 OK.

## Causa
Tras refactor Fase 1, `admin-shell` usa OnPush y `markForCheck`, pero `admin-organizaciones` seguía con change detection clásica sin signals ni `markForCheck` tras HTTP. La UI no se actualizaba al recibir datos.

## Cambios
- `admin-organizaciones` — OnPush, signals, `finalize`, `takeUntilDestroyed`, `markForCheck`.
- `admin-planes-precios` — mismo patrón.
- `admin-api.service.ts` — `shareReplay` + invalidate para tenants y pricing-plans.
- `docker_bootstrap.py` — excluir `99_*.sql` del bootstrap.

## Verificación
```powershell
docker compose build frontend
docker compose up -d frontend
# Login: patricio.mendez@sc-demo.test / scdemo1
# Organizaciones y Planes y precios deben mostrar datos sin quedarse en Cargando
```
