# Sesión 2026-06-04 — Fix provision taller (teléfono contacto)

## Problema
Usuario no podía crear taller + cuenta desde `/admin/panel/talleres`.

## Diagnóstico
- Logs: `POST /api/talleres/provision` → **422** (no llegaba a crear usuario).
- Body con `telefono_contacto: "123"` violaba `min_length=5` en `TallerProvisionIn`.
- Mensaje UI genérico no mostraba el detalle de validación.

## Fix
- `backend/.../talleres/schemas.py`: validator que copia teléfono/email del responsable si contacto inválido/vacío.
- `admin-talleres.component.ts`: validación previa, `normalizeProvisionContact()`, `apiErrorMessage()`.
- Label HTML: teléfono contacto mín. 5 dígitos.

## Verificación
- Con `telefono_contacto: "123"` y `responsable_telefono: "10999888"` → **201** y contacto guardado como `10999888`.
- Taller `Angelica` creado en tenant `si2-angelica` (id 4) durante reproducción.
