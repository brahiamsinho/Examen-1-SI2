# Sesión 2026-06-05 — Mobile panel responsable de taller

## Objetivo
Tercer actor en app Flutter: **responsable de taller** (no admin plataforma).

## Implementado
- `mobile/lib/taller/` — auth Riverpod, `TallerApiClient`, repositorios, pantallas.
- Rutas go_router bajo `/taller/*` integradas en `cliente_go_router.dart`.
- Selector `/modo`: tarjeta «Responsable de taller».
- Pantallas: splash, login, inicio (dashboard), bandeja + detalle (aceptar/rechazar/asignar), técnicos (lista), perfil, más módulos.
- Técnico mobile: solo rol `TECNICO` (responsable redirigido al módulo taller).

## Probar
1. `cd mobile && flutter run`
2. `/modo` → Responsable de taller
3. Login demo: org `demo-sc`, `luis.rivera@sc-demo.test` / contraseña seed
4. Bandeja → detalle → aceptar → asignar técnico

## Siguiente
- CRUD técnicos en mobile; disponibilidad toggle; comisiones resumen.
- Reportes voz (Gemini) reutilizando endpoint `/app/taller/reportes/voice`.
