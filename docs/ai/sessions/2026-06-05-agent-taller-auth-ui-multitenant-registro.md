# Sesión 2026-06-05 — Portal taller login/registro UI + multi-tenant registro

## UI/UX
- Design system compartido `_taller-auth-ui.scss` (Paleta A: `#0B1020`, cyan `#38BDF8`, CTA ámbar).
- Login y registro modernizados: card glass, labels con espaciado correcto, secciones en registro.
- Fix labels superpuestos: gap label→input 0.55rem (antes 0.4rem + estilos inconsistentes).

## Multi-tenant SaaS (registro)
- **Antes:** `POST /app/taller/registro` no asignaba `tenant_id` (usuarios/talleres huérfanos).
- **Ahora:** campo obligatorio `tenant_slug` en API + selector de organización en `/taller/registro`.
- Backend valida org `ACTIVO`; unicidad email/tel por tenant vía `create_usuario`.
- Login enlaza a registro con `?org=` y viceversa.

## Archivos clave
- `frontend/src/app/taller/features/auth/_taller-auth-ui.scss`
- `taller-login/*`, `taller-register/*`
- `backend/.../taller_responsable/schemas.py` (`tenant_slug`)
- `backend/.../taller_responsable/service.py` (`registro_taller_publico`)

## Verificación
```powershell
docker compose up -d --build backend frontend
# /taller/registro → org demo-sc → crear taller → login con misma org
```
