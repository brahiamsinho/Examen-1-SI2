# Sesión 2026-06-05 — Módulo backups (adaptación Oftalmología)

## Objetivo

Implementar respaldos automáticos y manuales adaptando el módulo `backup` del proyecto Oftalmología (Django + docker scheduler) al stack EmergenciasViales (FastAPI + shared schema multi-tenant).

## Diferencia clave de arquitectura

| Oftalmología | EmergenciasViales |
|--------------|-------------------|
| django-tenants, schema por clínica | PostgreSQL shared schema + `tenant_id` + RLS |
| `pg_dump --schema=clinica_x` | Export CSV filtrado por `tenant_id` |
| App Django `apps/backup` | `app/modules/acceso_y_administracion/backup/` |

## Implementación

- Migración `0021_backup_modulo.sql`
- Servicio: `pg_dump` (PLATAFORMA), CSV+tar (TENANT), tar evidencias (EVIDENCIAS)
- API: `/api/admin/backups` (superadmin + `backup:gestionar`)
- Docker: `backup-scheduler`, volumen `backup_data`, `postgresql-client` en imagen
- Frontend: `/admin/panel/backups`

## Verificación sugerida

```bash
docker compose up -d --build backend backup-scheduler frontend
# Admin → Backups → crear PLATAFORMA → descargar
docker compose logs backup-scheduler --tail 30
```

## Pendiente

- Restore lógico tenant desde CSV
- Tests pytest
- UI configuración automática (`PATCH /admin/backups/config`)
