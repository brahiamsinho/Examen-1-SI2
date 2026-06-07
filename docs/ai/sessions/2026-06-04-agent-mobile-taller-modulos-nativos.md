# Sesión 2026-06-04 — Mobile taller módulos nativos

## Problema
El usuario preguntó si el panel del responsable de taller estaba completo. Capturas mostraban placeholders mobile con texto «Abrí http://localhost/taller/panel…» para Comisiones, Disponibilidad, Historial, Reportes, Suscripción, Bitácora y Backups.

## Hallazgo
- **Portal web Angular** (`/taller/panel/*`): ya tenía todos los módulos.
- **App mobile taller**: solo operativo core (inicio, bandeja, técnicos, perfil); los 7 módulos avanzados eran placeholders.

## Implementación
- DTOs: `taller_modulos_models.dart`
- API: métodos en `taller_repository.dart` + endpoints en `api_constants.dart`
- Providers: `taller_injection.dart`
- Pantallas nativas + rutas GoRouter
- Eliminado `taller_placeholder_screen.dart`

## Limitaciones conscientes (mobile)
- Reportes: sin QBE builder, voz ni export Excel/PDF (web).
- Suscripción: lectura de plan; Stripe checkout en web.
- Backups: listar/crear; download/restore en web.

## Verificación
`flutter analyze lib/taller` — sin errores (solo info preexistente en bandeja_detalle).
