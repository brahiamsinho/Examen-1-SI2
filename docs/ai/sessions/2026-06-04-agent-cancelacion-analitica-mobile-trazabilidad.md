# Sesión — Cancelación solicitud + mobile analítica + trazabilidad

**Fecha:** 2026-06-04

## Objetivo

Cerrar gaps prioritarios post-analítica §3: cancelación con WS, paridad mobile reportes, trazabilidad PUDS.

## Backend — cancelación

- `POST /api/app/cliente/emergencias/{id}/cancelar`
- Permiso: `incidentes:actualizar`
- Estados cancelables: REGISTRADA → EN_CAMINO (no EN_ATENCION ni cerrados)
- Acciones: historial, bandeja EXPIRADA, libera cupo taller si aplica, notificaciones, WS

## Mobile

- Cliente: botón en `emergencia_seguimiento_screen.dart`
- Taller reportes: `OperationalKpis` en `taller_modulos_models.dart` + UI dashboard

## Documentación

- `docs/ai/TRACEABILITY_MATRIX.md`

## Tests

- `backend/tests/test_cancelacion_solicitud.py` — 5 tests OK
