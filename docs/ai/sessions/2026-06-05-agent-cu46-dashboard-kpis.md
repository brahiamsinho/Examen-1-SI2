# Sesión 2026-06-05 — CU46 Visualizar dashboard de KPIs

## Objetivo
Implementar CU46: panel web con métricas agregadas (solicitudes, tiempos, comisiones, pagos) para **Administrador** y **Taller**.

## Backend (ya en rama)
- Migración `0023_reportes_kpis_cu46.sql`: permiso `reportes:leer` → ADMIN, TALLER_RESPONSABLE.
- `GET /api/admin/panel/kpis` — agregación en `admin_dashboard/kpis.py`.
- `GET /api/app/taller/emergencias/reportes/kpis` — reutiliza reporte dashboard del taller (aislamiento por taller autenticado).

## Frontend (esta sesión)
- `admin/features/kpis/admin-kpis.component.*` → `/admin/panel/reportes-kpis`.
- `taller/features/kpis/taller-kpis.component.*` → `/taller/panel/reportes-kpis`.
- Nav en shells admin y taller; rutas lazy.
- Filtros fecha; tarjetas, tablas, gráfico serie (admin); empty state; error + reintento; export CSV.

## Excepciones CU46 cubiertas
1. Rol sin permiso → 403 + mensaje (`reportes:leer`).
2. Taller solo ve KPIs de su taller (backend `require_taller_responsable`).
3. Sin datos en periodo → empty state informativo.
4. Error consulta/timeout → mensaje + botón Reintentar.
5. Sesión expirada → interceptor/guard existente → CU2 login.

## Verificación manual
1. Aplicar migración 0023 en Docker.
2. Login admin → Reportes KPIs → cambiar fechas/tenant → ver métricas.
3. Login taller responsable → Reportes KPIs → export CSV.
4. Usuario sin `reportes:leer` → 403 en UI.

## Pendiente opcional
- Tests pytest integración CU46.
- Artefacto PUDS comunicación/diagrama CU46.
- Export PDF.
