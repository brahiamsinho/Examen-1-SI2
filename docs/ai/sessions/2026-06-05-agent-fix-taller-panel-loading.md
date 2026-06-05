# Sesión 2026-06-05 — Fix panel taller atascado en "Cargando…"

## Problema

Tras el refactor Fase 1 (OnPush en shells admin/taller), casi todas las vistas del sidebar del **panel taller** quedaban en "Cargando…" aunque las APIs respondían 200 OK en milisegundos.

Rutas afectadas (entre otras):
- `/taller/panel` (Resumen)
- `/taller/panel/emergencias/solicitudes`
- `/taller/panel/emergencias/mis-solicitudes`
- `/taller/panel/emergencias/historial`
- Mi taller, Técnicos, Roles, Clientes, Disponibilidad, Comisiones, detalle incidente

## Causa raíz

Mismo bug que en admin organizaciones/planes: el **shell** usa `ChangeDetectionStrategy.OnPush` + `markForCheck`, pero los **componentes hijos lazy-loaded** seguían con detección por defecto y `loading = true` (propiedad plana). Al terminar el HTTP, el estado cambiaba pero Angular no repintaba la vista.

## Solución aplicada

Patrón unificado en todos los componentes taller pendientes:

1. `changeDetection: ChangeDetectionStrategy.OnPush`
2. `readonly loading = signal(true)` (y `loadingAsignData` en detalle incidente)
3. `ChangeDetectorRef.markForCheck()` en callbacks HTTP
4. `takeUntilDestroyed` + `finalize(() => loading.set(false))`
5. Templates: `loading()` en lugar de `loading`

## Archivos modificados

### TypeScript
- `taller/features/dashboard/taller-dashboard.component.ts` (sesión previa)
- `taller/features/emergencias/bandeja/taller-emergencias-bandeja.component.ts`
- `taller/features/emergencias/historial-list/taller-emergencias-historial-list.component.ts`
- `taller/features/emergencias/disponibilidad/taller-emergencias-disponibilidad.component.ts`
- `taller/features/emergencias/comisiones/taller-emergencias-comisiones.component.ts`
- `taller/features/emergencias/incidente-detalle/taller-emergencias-incidente-detalle.component.ts`
- `taller/features/mi-taller/taller-mi-taller.component.ts`
- `taller/features/tecnicos/taller-tecnicos.component.ts`
- `taller/features/accesos/roles/taller-roles.component.ts`
- `taller/features/accesos/clientes/taller-clientes.component.ts`

### HTML (loading → loading())
- Todos los `.html` correspondientes a los componentes anteriores.

## Verificación

```bash
docker compose build frontend
docker compose up -d frontend
```

Probar con **Ctrl+Shift+R** como `luis.rivera@sc-demo.test` (rol TALLER_RESPONSABLE).

## Pendiente menor

- Admin: `admin-bitacora`, `admin-roles` aún con patrón viejo (menor prioridad).
- Opcional: `markForCheck` explícito en `taller-permisos` por consistencia (signals suelen bastar).
