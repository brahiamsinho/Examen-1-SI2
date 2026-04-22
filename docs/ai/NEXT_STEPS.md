# NEXT_STEPS.md
# =========================================================
# Próximos pasos ordenados por prioridad
# Actualizado: 2026-04-22 (Angular CU28 + visión Ciclo 2)
# =========================================================

## ALTA — Entorno listo en 5 min

1. Leer **`AGENTS.md`** (raíz).
2. Copiar **`.env.example` → `.env`** en la raíz del repo y ajustar `SECRET_KEY`, DB si hace falta.
3. **`mobile/.env`** desde `mobile/.env.example` — `API_BASE_URL` (IP/puerto del host desde el dispositivo).
4. **`docker compose up -d`** luego **`docker compose exec backend python -m app.seeds`**.
5. Probar API: `http://localhost:8000/docs` y health `/health`.
6. **BD ya existente (actualización 2026-04-22):** si aparece `tecnico_asignado_at` inexistente, aplicar el SQL de `backend/migrations/0006_tecnico_asignado_at.sql` (p. ej. con `psql` en el contenedor `db`). Init de Postgres no vuelve a correr en un volumen ya poblado.

## MEDIA — Producto (Ciclo 1 y transversal)

### Angular
- [ ] Auth (login/guard/interceptor) y layout admin
- [ ] Pantallas CRUD alineadas al backend (más allá del portal taller emergencias)

### Flutter
- [ ] Tests (unit/widget), refresh token si se expone en API
- [ ] Pulir UX y mensajes de error en red

### Backend
- [ ] Endpoint refresh / recuperación de contraseña real si producto lo exige
- [ ] Paginación y tests pytest ampliados

## MEDIA — Dominio emergencias (Ciclo 2; parte ya implementada en repo)

- [x] Backend: `emergencias`, `portal_taller_emergencias` (incl. CU28 asignar técnico), `portal_tecnico_emergencias`
- [x] Flutter cliente: flujo reporte / listado / seguimiento
- [x] Portal web taller: bandeja, detalle, aceptar/rechazar, asignar técnico (CU28), disponibilidad
- [ ] Notificaciones push y geolocalización en tiempo real (mejoras)

## BAJA

- [ ] CI/CD, despliegue documentado

## Obsoleto (ya hecho)

- ~~`flutter create` / `ng new`~~ — proyectos ya inicializados.
- ~~Alembic baseline~~ — configurado; usar `alembic stamp` / `upgrade` según doc del README raíz.
