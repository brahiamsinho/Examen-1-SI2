# Sesión 2026-06-05 — Reportes QBE + voz + export

## Objetivo
Implementar reportes personalizados en portal taller con consulta por voz/texto y exportación Excel, PDF, CSV.

## Referencia
- `Oftalmologia-Si2/backend/apps/reportes/` — QBE engine, export engine, export intent, plantillas predefinidas.

## Implementación
- Módulo `backend/app/modules/acceso_y_administracion/reportes/`
- Migración `0025_reportes_modulo.sql`
- Router `/api/app/taller/reportes/*`
- Frontend `/taller/panel/reportes`

## Decisiones
- QBE solo modelos whitelist (no SQL libre).
- Scope automático por `tenant_id` y `taller_id` del responsable.
- NL por reglas en español (MVP); voz navegador + endpoint `/voice` opcional con Whisper.

## Verificación
- `docker compose up -d --build backend`
- Log: `Aplicando migración SQL: 0025_reportes_modulo.sql`
- Re-login taller → `/taller/panel/reportes`
