# Sesión 2026-06-05 — CU42 Registrar cotización del servicio

## Backend
- Migración `0021_presupuesto_taller_cu42.sql`: columna `presupuesto_detalle`, permiso `presupuestos:registrar`.
- `service/presupuesto.py`: validación tenant/taller/estado, no reemplazo si ya existe cotización.
- Endpoints:
  - `GET /api/app/taller/emergencias/solicitudes/{id}/presupuesto`
  - `PATCH /api/app/taller/emergencias/solicitudes/{id}/presupuesto`
- `eventos_servicio.on_presupuesto_registrado` → notificación in-app al cliente.
- Detalle bandeja expone `presupuesto_bob`, `presupuesto_detalle`, `presupuesto_registrado_at`.

## Frontend taller
- Formulario en `taller-emergencias-incidente-detalle` (bloque Cotización del servicio).
- API: `TallerEmergenciasApiService.registrarPresupuesto`.

## Estados que admiten cotización
`TALLER_ASIGNADO`, `TECNICO_ASIGNADO`, `EN_CAMINO`, `EN_ATENCION` (bandeja ACEPTADA).

## Convivencia CU39
El técnico puede registrar/actualizar monto al pasar a EN_ATENCION; el taller no puede reemplazar una cotización ya registrada (409).

## Pendiente
- Tests pytest integración CU42.
- Diagrama PUDS / trazabilidad PKG02.
- Mostrar `presupuesto_detalle` en app cliente mobile.
