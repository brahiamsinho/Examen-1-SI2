# Sesión 2026-06-05 — Fix bitácora admin loading

## Problema
`/admin/panel/bitacora` — "Cargando…" permanente con `GET /api/bitacora/` 200 OK.

## Causa
Tras refactor Fase 1, `admin-shell` usa `ChangeDetectionStrategy.OnPush`. `admin-bitacora` seguía con detección clásica sin `markForCheck` tras el HTTP; el estado cambiaba pero Angular no repintaba.

## Fix
`admin-bitacora.component.ts`:
- `ChangeDetectionStrategy.OnPush`
- `finalize` + `takeUntilDestroyed`
- `cdr.markForCheck()` en fetch, modal detalle y validación local

## Verificación
```powershell
cd frontend && npm run build
docker compose up -d --build frontend
# /admin/panel/bitacora → tabla o "Sin registros", no Cargando infinito
```
