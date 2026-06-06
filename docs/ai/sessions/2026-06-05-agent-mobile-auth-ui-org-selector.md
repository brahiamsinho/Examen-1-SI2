# Sesión — Mobile auth UI + selector organización (2026-06-05)

## Cambios
- Rediseño pantalla `/modo` (actor select): gradiente Paleta A, cards con acento, org selector arriba.
- `OrgSlugSelector` bottom sheet con 7 orgs demo + persistencia `TenantSlugStorage`.
- Login cliente/técnico/taller y registro cliente usan selector (no texto libre).
- Widgets compartidos: `core/widgets/auth/`, `MobileAuthTheme`, `demo_tenant_options.dart`.

## Probar
1. Hot restart app → `/modo` → elegir org → perfil → login.
2. Cliente demo-sc: `carlos.vega@sc-demo.test` / `scdemo1`.
3. Técnico multi-org: `tecnico1@org-pro-anillo.demo.test` / `scdemo1` + org `org-pro-anillo`.
