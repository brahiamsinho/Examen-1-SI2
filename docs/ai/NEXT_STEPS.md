# NEXT_STEPS.md
# =========================================================
# Próximos pasos ordenados por prioridad
# Actualizado: 2026-04-23 — módulo IA 100% validado, stack operativo
# =========================================================

## ALTA — Entorno listo en 5 min

1. Leer **`AGENTS.md`** (raíz).
2. Copiar **`.env.example` → `.env`** en la raíz del repo y ajustar `SECRET_KEY`, DB si hace falta. **IA:** definir **una sola vez** `AI_ENABLED` y `AI_INFERENCE_BASE_URL` (no duplicar bloques al pegar comentarios). Para Docker con worker en la misma red: `AI_ENABLED=true`, `AI_INFERENCE_BASE_URL=http://ai-inference:8080`.
3. **`mobile/.env`** desde `mobile/.env.example` — `API_BASE_URL` (IP/puerto del host desde el dispositivo).
4. **Docker — solo DB + backend + frontend + Mailhog:**  
   `docker compose up -d --build`  
   **Docker — incluir worker de inferencia (Whisper + YOLO):**  
   `docker compose --profile ai up -d --build`  
   **Docker — además modelo de clasificación propio** (archivo local `backend/incidentes_emergencias_v1.pt`):  
   `docker compose -f docker-compose.yml -f docker-compose.ai-custom-model.yml --profile ai up -d --build`
5. Luego **`docker compose exec backend python -m app.seeds`** (mismo proyecto; el perfil `ai` no afecta `exec`).
6. Probar API: `http://localhost:8000/docs` y health `/health`. Probar IA: `POST /api/ai/images/analyze` con Bearer de un usuario con permiso `ai:inferir` (p. ej. admin tras seeds).
7. **BD ya existente (actualización 2026-04-22):** si aparece `tecnico_asignado_at` inexistente, aplicar el SQL de `backend/migrations/0006_tecnico_asignado_at.sql` (p. ej. con `psql` en el contenedor `db`). Init de Postgres no vuelve a correr en un volumen ya poblado.
8. **Tras cambiar código de `services/ai-inference/`:** reconstruir el contenedor, p. ej.  
   `docker compose -f docker-compose.yml -f docker-compose.ai-custom-model.yml --profile ai up -d --build --force-recreate ai-inference`

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
- [x] **Módulo IA completo** — 6 endpoints validados con respuestas 200 correctas (audio, imagen, clasificar, resumen estructurado, priorizar, rankear talleres)
- [ ] Notificaciones push y geolocalización en tiempo real (mejoras)

## BAJA

- [ ] CI/CD, despliegue documentado

## Obsoleto (ya hecho)

- ~~`flutter create` / `ng new`~~ — proyectos ya inicializados.
- ~~Alembic baseline~~ — configurado; usar `alembic stamp` / `upgrade` según doc del README raíz.
