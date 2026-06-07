# Sesión 2026-06-05 — Notificaciones inmediatas del servicio (reimplementación)

## Backend
- Migración `0020_notificaciones_evento_id.sql`
- `eventos_servicio.py`, `tenant_guard.py`
- Hooks: selección taller, bandeja, asignación, cambio estado
- API taller: `GET/PATCH /api/app/taller/notificaciones`

## Frontend
- `/taller/panel/comunicacion/notificaciones`

## Mobile técnico
- `/tecnico/app/notificaciones`

## Probar
1. Cliente elige taller → taller ve notificación (web, polling 30s)
2. Taller acepta → cliente recibe aviso
3. Asignar técnico → cliente + técnico + taller
4. Técnico cambia estado → los tres actores
