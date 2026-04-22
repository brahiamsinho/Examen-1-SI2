# DECISIONS_LOG.md
# =========================================================
# Decisiones técnicas tomadas y su justificación
# =========================================================

## DEC-001 — SQLAlchemy async con asyncpg
**Fecha:** 2026-04-11
**Decisión:** Usar SQLAlchemy 2.0 con asyncio + asyncpg (no psycopg2)
**Por qué:** FastAPI es async. Usar un driver síncrono bloquearía el event loop en
cada query, eliminando el beneficio de async. asyncpg es el driver PostgreSQL
async nativo más rápido para Python.

## DEC-002 — JWT con JTI en tabla sesiones
**Fecha:** 2026-04-11
**Decisión:** Almacenar el JTI (JWT ID) de cada refresh token en la tabla `sesiones`
**Por qué:** JWT puro es stateless y no se puede revocar. Al almacenar el JTI en BD
podemos marcar tokens individuales como REVOCADOS sin invalidar toda la sesión del usuario.

## DEC-003 — Soft delete para usuarios
**Fecha:** 2026-04-11
**Decisión:** No eliminar usuarios físicamente — cambiar estado a INACTIVO
**Por qué:** 
1. La bitácora referencia usuarios (FK ON DELETE SET NULL)
2. Los vehículos referencian clientes — eliminar el usuario rompería la cadena
3. El historial de auditoría debe mantenerse intacto

## DEC-004 — init.sql vs Alembic
**Fecha:** 2026-04-11
**Decisión:** Usar `init.sql` en `docker-entrypoint-initdb.d/` para el schema inicial
**Por qué:** Para el Ciclo 1 es más directo. PostgreSQL ejecuta este script solo cuando
el volumen está vacío (primera vez). Para Ciclo 2+, agregar Alembic para migraciones incrementales.

## DEC-005 — Angular standalone (sin NgModules)
**Fecha:** 2026-04-11
**Decisión:** Usar Angular 17 standalone components y functional guards/interceptors
**Por qué:** NgModules son legacy en Angular 17+. Standalone reduce boilerplate,
mejora tree-shaking y es el camino oficial de Angular desde v17.

## DEC-006 — Función centralizada de bitácora
**Fecha:** 2026-04-11
**Decisión:** Crear `bitacora/service.py::registrar_accion()` como único punto de escritura
**Por qué:** Si cada módulo escribe directamente a la tabla, es difícil cambiar
el esquema de auditoría sin tocar todos los módulos. Centralizar facilita
agregar campos, cambiar transporte (ej: a cola de mensajes) o formatear logs.

## DEC-007 — Flutter con Dio (no http)
**Fecha:** 2026-04-11
**Decisión:** Usar Dio sobre el paquete `http` estándar
**Por qué:** Dio tiene interceptors nativos (para JWT), timeout configurable,
FormData, y mejor manejo de errores. Para una app con autenticación,
es la opción estándar de la comunidad Flutter.

## DEC-008 — Config móvil con `.env` (flutter_dotenv) + sesión técnica separada
**Fecha:** 2026-04-19
**Decisión:** Cargar `mobile/.env` en arranque con `flutter_dotenv`; URLs y nombre de app vía `AppEnv` / `ApiConstants`. Segundo cliente HTTP (`TecnicoApiClient`) con claves `tecnico_access_token` / `tecnico_refresh_token` en `flutter_secure_storage` para no mezclar sesión con el flujo cliente.
**Por qué:** Evita hardcodear `API_BASE_URL` y permite probar en dispositivo físico sin recompilar con `--dart-define`. Dos actores en la misma app requieren aislar tokens si el usuario alterna modo sin cerrar sesión global única.

## DEC-009 — Columna `tecnico_asignado_at` en `solicitudes_emergencia` (migraciones Docker)
**Fecha:** 2026-04-22
**Decisión:** Incluir `tecnico_asignado_at TIMESTAMP` (nullable) en el mismo `ALTER` de fase 2 (`0003_ciclo2_fase2_seguimiento.sql`) y además en un parche idempotente `0006_tecnico_asignado_at.sql` montado en `docker-compose` como script `05` (después de comunicaciones) para BDs creadas con un `0003` antiguo sin la columna.
**Por qué:** El ORM y `portal_taller_emergencias` dependen de esa marca de tiempo al asignar técnico; sin columna, cualquier `INSERT`/`SELECT` a la tabla falla y el cliente móvil no puede registrar emergencias. Init de Postgres solo corre en volumen vacío: los entornos existentes requieren `ADD COLUMN IF NOT EXISTS` manual o ejecutar `0006` contra la instancia.
