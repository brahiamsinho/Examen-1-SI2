# Sesión — Analítica operacional KPIs §3

**Fecha:** 2026-06-04  
**Rama:** `feature/mobile`

## Objetivo

Implementar los 7 KPIs operacionales del enunciado §3 con datos reales en BD, expuestos en admin y taller web.

## Backend

- Módulo `backend/app/modules/analytics/`:
  - `operational_kpis.py` — consultas SQL agregadas.
  - `schemas.py` — `OperationalKpisRead` y filas auxiliares.
- Config: `SLA_ATENCION_MINUTOS` (default 60) en `app/core/config.py`.
- Integración:
  - `GET /api/admin/panel/kpis` → campo `analitica_operacional`.
  - `GET /api/app/taller/emergencias/reportes/kpis` → mismo campo (filtrado por taller).

## KPIs calculados

1. Tiempo promedio de asignación (reporte → taller asignado).
2. Tiempo promedio de llegada (técnico asignado → en camino/atención).
3. Incidentes por tipo (desde `ai_payload.clasificacion.categoria`).
4. Talleres más eficientes (respuesta + finalización).
5. Zonas con más incidentes (grid lat/lng).
6. Casos cancelados y no atendidos (REGISTRADA).
7. Cumplimiento SLA (% finalizadas dentro del umbral).

## Frontend

- Modelo compartido: `operational-kpis.models.ts`.
- Admin: sección «Analítica operacional» en `/admin/panel/reportes-kpis` + CSV.
- Taller: sección equivalente en `/taller/panel/reportes-kpis` + CSV.

## Tests

- `backend/tests/test_operational_kpis.py` — schemas y `_round_minutes`.

## Pendiente opcional

- E2E Docker con datos seed.
- Mobile: tab Dashboard de reportes con bloque analítica (enunciado cubierto en web).
