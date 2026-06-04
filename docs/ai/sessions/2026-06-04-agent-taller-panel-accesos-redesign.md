# Sesión 2026-06-04 — Rediseño panel taller + accesos

## Objetivo

Rediseñar UI/UX del panel web `/taller/panel` para reflejar gestión de técnicos **y** cuentas/usuarios, clientes, roles y permisos.

## Backend

- Migración `0018_taller_acceso_permisos.sql`: permiso `clientes:leer` + asignación a `TALLER_RESPONSABLE` de `usuarios:leer|crear|actualizar`, `clientes:leer`, `roles:gestionar`.
- `GET /api/clientes/` enriquecido (`ClienteListRead`) y filtrado por tenant vía `AuthContext`.
- Dashboard taller: KPIs `usuarios_activos`, `clientes_registrados`.

## Frontend

- **Shell taller** alineado con admin: sidebar agrupada, iconos SVG, colapsable, drawer móvil, breadcrumb, acento verde.
- **Rutas nuevas:** `/taller/panel/accesos/{usuarios,clientes,roles,permisos}` con `tallerPermisoGuard`.
- **Interceptor:** token taller para APIs compartidas (`/usuarios`, `/clientes`, `/roles`, `/permisos`, `/especialidades`) cuando la ruta activa es `/taller/panel`.
- **Dashboard:** tarjetas y chips de accesos rápidos.
- **Componentes:** `taller-usuarios`, `taller-clientes`, `taller-roles`, `taller-permisos` + mixin `_taller-accesos-page.scss`.

## Probar

1. Reiniciar backend (migración 0018) o `docker compose up -d --build backend`.
2. Cerrar sesión y volver a entrar en `/taller` (refrescar permisos en JWT) — ej. `angelica@gmail.com`.
3. Ver sidebar **Accesos y cuentas** y pantallas CRUD/consulta.

## Notas

- Roles `ADMIN` / `CLIENTE`: edición de permisos limitada en UI taller (solo TECNICO y TALLER_RESPONSABLE).
- Clientes: solo lectura (alta vía app móvil).
