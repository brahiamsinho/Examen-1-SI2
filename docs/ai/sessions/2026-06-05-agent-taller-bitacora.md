# Sesión 2026-06-05 — Bitácora portal taller

## Pedido

Implementar bitácora en el panel taller, registrando solo lo relevante para **su** taller sin violar privacidad de otros talleres.

## Solución

### Backend

- Migración `0020_taller_bitacora_permiso.sql`: permiso `bitacora_taller:leer` → rol `TALLER_RESPONSABLE`.
- `GET /api/app/taller/bitacora` con filtros opcionales (usuario, módulo, acción, fechas).
- Servicio `taller_responsable/bitacora_service.py`:
  - Fuerza `Usuario.tenant_id == user.tenant_id`.
  - Solo actores: responsable del taller + técnicos de ese `taller_id`.
  - Whitelist de módulos: `auth`, `talleres`, `taller_responsable`, `taller_emergencias`, `tecnico`, `taller_portal`, `usuarios`.
  - Respuesta sin `ip_address`.
- Logging suscripción: checkout y confirm en `subscription_service.py` (módulo `taller_portal`).

### Frontend

- Ruta `/taller/panel/bitacora` con `tallerPermisoGuard` + `bitacora_taller:leer`.
- Nav «Bitácora» en grupo Equipo y taller.
- Componente `taller-bitacora` (OnPush), filtros por miembro del equipo / módulo / acción / fechas.

## Verificación

1. Aplicar migración: `docker compose up -d --build backend` (o ejecutar `0020_*.sql` en BD existente).
2. Login taller → sidebar **Bitácora** → debe listar acciones del responsable y técnicos.
3. No deben aparecer logs de clientes (`emergencias`, `clientes`, `pagos`) ni de otros talleres del mismo tenant.

## Archivos clave

- `backend/app/modules/talleres_y_tecnicos/taller_responsable/bitacora_service.py`
- `backend/app/modules/talleres_y_tecnicos/taller_responsable/router.py`
- `frontend/src/app/taller/features/bitacora/`
