# Sesión 2026-05-28 — Landing Paleta A (Dark Pro Soft)

## Objetivo

Implementar la recomendación del plan `LANDING_REDESIGN_PLAN.md`: **Paleta A** + fases 1–3 (tokens, nav/hero, bento/pricing/accesos).

## Motivo

El tema claro anterior generaba fatiga visual (“demasiado blanco”). Paleta A usa fondo oscuro suave, CTA ámbar y acentos sky.

## Cambios

| Archivo | Qué |
|---------|-----|
| `landing-page.component.html` | Estructura nueva: product frame, bento, trust pills, pricing, accesos, flujo, módulos, CTA, footer |
| `landing-page.component.scss` | Tokens Paleta A; ~900 líneas (reemplazo del tema claro) |
| `landing-page.component.ts` | Ya tenía `bentoCells`, `heroPreviewRows`, `stackPills` (turno anterior) |
| `frontend/src/index.html` | Google Fonts: Inter + Outfit |

## Tokens Paleta A

- `bg` #0B1020
- `surface` #141B2D
- `primary` #38BDF8
- `cta` #F59E0B
- `text` #E8EDF5
- `muted` #94A3B8

## Pendiente

- Fases 4–5 del plan: screenshot real del panel en product frame; acordeón módulos.
- Build local sin `ng` en PATH; validar con Docker.

## Comando

```powershell
docker compose up -d --build frontend
```

Abrir `http://localhost/` con recarga forzada.
