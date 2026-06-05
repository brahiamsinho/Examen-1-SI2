# Sesión 2026-06-04 — Refactor rendimiento Fase 1

## Rama

`feature/optimizando`

## Cambios

### Landing
- `OnPush` + `markForCheck` en acciones de UI.
- Scroll con `fromEvent` + `throttleTime(100)` (sin `@HostListener` en cada pixel).
- `forkJoin` para Stripe config + planes en un solo round-trip.
- `takeUntilDestroyed` en subscripciones.

### Dashboard admin
- Gráfico de barras: precálculo `barWidthPct` y `serieComisionTotal` al cargar datos (evita O(n²) en template).
- `format-money.util.ts` — `Intl.NumberFormat` reutilizable.
- Quick links actualizados (planes/talleres, sin roles/permisos).

### Listados (signals + computed)
- Reemplazado `get filtered()` por `computed()` + `filterRowsByQuery` en:
  - admin/taller permisos, roles, usuarios, talleres
  - taller usuarios
- `OnPush` en componentes migrados.

### Shells
- `admin-shell` y `taller-shell`: `ChangeDetectionStrategy.OnPush`.
- Taller shell: una sola `rebuildNavGroups` inicial + refresh tras `/auth/me`.

### Utilidades nuevas
- `frontend/src/app/core/utils/list-filter.util.ts`
- `frontend/src/app/core/utils/format-money.util.ts`

## Backend (misma rama, fase complementaria)

### `admin_dashboard/service.py`
- `get_panel_overview`: 4 consultas en **paralelo** con `asyncio.gather` + `AsyncSessionLocal` (patrón finanzas).
- Router ya no inyecta `get_db` para overview.

### `pricing_plans`
- Cache en memoria TTL 5 min (`list_public_plans_cached`).
- Invalidación al `PATCH` admin.
- `GET /api/public/pricing/bootstrap` → `{ plans, stripe }` + `Cache-Control: max-age=300`.
- Landing usa bootstrap (1 HTTP en lugar de 2).

## Pendiente Fase 2
- Partir SCSS landing (budget 20 kB).
- Migrar bandeja/historial/técnicos/clientes/taller-roles.
- Componentes shared admin/taller accesos.

## Verificación

`docker compose build frontend` — OK (warning budget SCSS landing +264 bytes).
