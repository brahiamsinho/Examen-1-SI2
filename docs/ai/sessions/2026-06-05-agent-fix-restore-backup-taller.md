# Sesión: fix restore backup taller

**Fecha:** 2026-06-05  
**Problema:** POST `/api/app/taller/backups/1/restore` → 500, `COPY talleres` PK duplicate.

## Causa

El restore de taller borraba datos operativos (técnicos, bandeja, etc.) pero luego intentaba **insertar** de nuevo el registro en `talleres`. Ese taller ya existe (id=1), por eso PostgreSQL rechazaba el `COPY`.

## Solución

- `talleres` ya no entra en `TALLER_RESTORE_INSERT_ORDER`.
- Nueva función `_restore_taller_row_from_csv`: parsea el CSV y ejecuta `UPDATE talleres SET ... WHERE id = ?`.
- `runner.py`: `import app.db_metadata` para registrar modelos ORM (fix scheduler `Cliente`).

## Archivos

- `backend/app/modules/acceso_y_administracion/backup/service.py`
- `backend/app/modules/acceso_y_administracion/backup/runner.py`
- `backend/app/db_metadata.py`

## Despliegue local

Tras cambios en scheduler: `docker compose build backup-scheduler && docker compose up -d backup-scheduler`.
