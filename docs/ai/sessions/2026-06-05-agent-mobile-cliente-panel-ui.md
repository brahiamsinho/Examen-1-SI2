# Sesión — Mobile panel cliente UI Paleta A

**Fecha:** 2026-06-05  
**Agente:** redesign panel autenticado cliente mobile

## Objetivo

Alinear todo el panel `/cliente/app/*` con la Paleta A del login (gradiente oscuro, cards, action tiles, bottom nav pill) y selector compacto de organización.

## Entregables

| Archivo | Rol |
|---------|-----|
| `mobile/lib/cliente/presentation/widgets/cliente_panel_ui.dart` | Design system panel (background, bottom nav, tiles, banners, subpage scaffold) |
| `mobile/lib/core/widgets/auth/cliente_org_chip.dart` | Chip org + bottom sheet |
| `mobile/lib/core/widgets/auth/org_slug_selector.dart` | `showOrgSlugPicker()` reutilizable |
| `cliente_app_shell.dart` | Gradiente + `ClientePanelBottomNav` |
| `cliente_home_screen.dart` | Home rediseñado + org chip |
| `cliente_perfil_screen.dart` | Form en `AuthFormCard` |
| `cliente_vehiculos_flow.dart` | Lista/cards/detalle/form |
| Emergencias + notificaciones | `ClienteSubpageScaffold` en sub-flujos |

## Validación manual

1. Login `carlos.vega@sc-demo.test` / `scdemo1` org `demo-sc`.
2. Home: gradiente, banner vehículos, tiles acción, chip org arriba-derecha.
3. Bottom nav: pill activo en Inicio / Vehículos / Perfil.
4. Perfil: formulario card + logout.
5. Emergencia → selección vehículo → wizard (6 pasos) con header oscuro.
6. Mis solicitudes / Notificaciones: back + filtros chips.

## Pendiente opcional

- Chat solicitud, selección taller, ubicación técnico, pantallas de pago: mismo scaffold si se desea paridad total.
- Splash/onboarding mobile.
