# Sesión: fix restore backup taller — FK tecnicos → usuarios

**Fecha:** 2026-06-05  
**Problema:** Tras hard-delete de un técnico, restore del backup fallaba:

`ERROR: insert or update on table "tecnicos" violates foreign key constraint "fk_tecnicos_usuario" DETAIL: Key (usuario_id)=(5) is not present in table "usuarios".`

## Causa

1. El backup de taller exportaba `tecnicos.csv` pero **no** las filas de `usuarios` / `usuario_rol` de esos técnicos.
2. Al eliminar un técnico con la nueva acción «Eliminar», también se borra su cuenta en `usuarios`.
3. El restore hacía `COPY tecnicos` referenciando `usuario_id` que ya no existe.

## Solución

- **Export:** incluir `usuarios` y `usuario_rol` de los técnicos del taller en `TALLER_EXPORT_TABLES`.
- **Restore:** `_restore_taller_staff_from_csv` recrea cuentas (DELETE seguro + COPY) **antes** de insertar `tecnicos`.
- **Compatibilidad:** `_restore_table_from_csv` omite filas de `tecnicos` (y asignaciones) cuyo FK no existe — backups antiguos sin `usuarios.csv` ya no rompen el restore (pero no recuperan técnicos eliminados).

## Archivos

- `backend/app/modules/acceso_y_administracion/backup/service.py`

## Prueba manual

1. `docker compose up -d --build backend`
2. Crear **nuevo** backup manual en `/taller/panel/backups`.
3. Eliminar un técnico sin historial.
4. Restaurar el backup recién creado → debe volver el técnico y su cuenta.

**Nota:** backups creados **antes** de este fix (ej. id #9) restauran sin error pero **no** traen de vuelta técnicos cuya cuenta fue borrada (falta `usuarios.csv` en el archivo).
