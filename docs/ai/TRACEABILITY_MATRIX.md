# TRACEABILITY_MATRIX.md
# Matriz RF/CU → implementación (Examen-1-SI2)
# Actualizado: 2026-06-04

| ID | Requerimiento / CU | Módulo backend | Endpoint / artefacto | Frontend / Mobile |
|----|-------------------|----------------|----------------------|-------------------|
| §3 KPI-1 | Tiempo prom. asignación | `analytics/operational_kpis.py` | `analitica_operacional` en KPIs admin/taller | `/admin/panel/reportes-kpis`, `/taller/panel/reportes-kpis`, mobile reportes dashboard |
| §3 KPI-2 | Tiempo prom. llegada | `analytics/operational_kpis.py` | idem | idem |
| §3 KPI-3 | Incidentes por tipo | `analytics/operational_kpis.py` | idem | idem |
| §3 KPI-4 | Talleres eficientes | `analytics/operational_kpis.py` | idem (admin) | Admin KPIs |
| §3 KPI-5 | Zonas incidentes | `analytics/operational_kpis.py` | idem | idem |
| §3 KPI-6 | Cancelados / no atendidos | `analytics/operational_kpis.py` | idem | idem |
| §3 KPI-7 | SLA cumplimiento | `analytics/operational_kpis.py` + `SLA_ATENCION_MINUTOS` | idem | idem |
| CU36 | Ubicación técnico | `tecnico/service/ubicaciones.py` | `GET .../ubicacion-tecnico` | `emergencia_ubicacion_tecnico_screen.dart` |
| CU37 | Elegir taller | `emergencias/service/seleccion_taller.py` | `POST .../seleccionar-taller` | `emergencia_seleccion_taller_screen.dart` |
| CU38 | Pago servicio | `pagos_y_comisiones/pagos/` | pagos cliente | `solicitud_pago_*` mobile |
| CU41 | Notificaciones | `notificaciones/eventos_servicio.py` | FCM + in-app | campana taller/admin, mobile FCM |
| CU42 | Cotización taller | `taller_emergencias/service/presupuesto.py` | PATCH presupuesto | detalle incidente taller web |
| CU43 | Sync offline | `emergencias/service/solicitudes.py` | `client_request_id` | `SyncOrquestador` mobile |
| CU44 | ETA reparación | `emergencias/service/seguimiento_eta.py` | `GET .../seguimiento/eta` | `EtaReparacionCu44Card` |
| CU45 | Borrador offline | mobile Hive | POST crear idempotente | wizard + borradores |
| CU46 | Dashboard KPIs | `admin_dashboard/kpis.py`, `taller_emergencias/reportes.py` | KPIs + `reportes:leer` | reportes-kpis admin/taller |
| — | Cancelar solicitud | `emergencias/service/cancelacion.py` | `POST .../cancelar` + WS | seguimiento mobile (botón cancelar) |
| — | Tiempo real | `tiempo_real/` | `WS /api/ws/solicitudes/{id}` | providers `solicitud_realtime_*` |

## Artefactos PUDS relacionados

- Secuencia CU41–CU46: `docs/diagrams/uml/` + EA diagramIDs 67–72
- Flujos portal taller: `docs/ai/FLOWS_PORTAL_TALLER.md`
- Sesiones de implementación: `docs/ai/sessions/`

## Pendiente académico opcional

- Diagrama secuencia cancelación cliente → bandeja → WS
- Tests integración pytest con BD para cancelación y KPIs agregados
