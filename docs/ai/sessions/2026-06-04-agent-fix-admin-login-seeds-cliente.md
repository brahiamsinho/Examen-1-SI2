# Sesión 2026-06-04 — Fix login admin + seeds CLIENTE

## Problema reportado

Usuario no podía entrar a `/admin/login`. UI: **"Tu cuenta no tiene rol de administrador."**

## Causas

1. **Usuario incorrecto:** `luis.rivera@sc-demo.test` tiene rol `TALLER_RESPONSABLE` → el panel admin lo rechaza (correcto).
2. **502 al arrancar:** el backend tardaba ~17 s porque los seeds fallaban 8 veces en loop; nginx devolvía 502 si se intentaba login antes de `Application startup complete`.
3. **Bug seeds:** `dev_cliente.py` llamaba `asignar_roles_usuario()` que bloquea rol `CLIENTE` (regla del panel admin).

## Fix

- `roles/service.py`: `asignar_roles_usuario_seed()` para seeds/CLI (sin bloqueo CLIENTE).
- `dev_cliente.py`, `dev_stress_visual.py`: usan la función seed.

## Credenciales demo (panel admin)

| Email | Password | Rol |
|-------|----------|-----|
| patricio.mendez@sc-demo.test | scdemo1 | ADMIN |

No usar en `/admin/login`: luis.rivera (taller), carlos.vega (cliente móvil).

## Verificación

- Startup backend ~1 s, sin reintentos de seeds.
- `POST /api/auth/login` + `GET /api/auth/me` → `roles: ["ADMIN"]`, `is_platform_superadmin: true`.
