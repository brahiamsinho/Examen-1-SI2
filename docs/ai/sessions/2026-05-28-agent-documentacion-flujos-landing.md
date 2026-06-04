# Sesión 2026-05-28 — Documentación consolidada (landing + flujos taller)

## Qué se documentó

1. **Landing Paleta A (Dark Pro Soft)** — ya implementado en código; memoria y plan existentes.
2. **Flujo portal taller** — análisis conversacional formalizado en artefacto persistente.
3. **Diagrama UML** — secuencia PlantUML nuevo.
4. **Decisión arquitectónica** — registro vs login (DEC-029).

## Artefactos creados / actualizados

| Archivo | Tipo |
|---------|------|
| `docs/ai/FLOWS_PORTAL_TALLER.md` | **Nuevo** — fuente de verdad flujos `/taller` |
| `docs/diagrams/uml/sequence-taller-registro-login.puml` | **Nuevo** — UML 2.5 secuencia |
| `docs/ai/CURRENT_STATE.md` | Actualizado — enlaces a FLOWS |
| `docs/ai/HANDOFF_LATEST.md` | Actualizado — índice documentación sesión |
| `docs/ai/NEXT_STEPS.md` | Actualizado — PlantUML secuencia taller |
| `docs/ai/DECISIONS_LOG.md` | DEC-029 |
| `docs/ai/sessions/2026-05-28-agent-documentacion-flujos-landing.md` | Esta sesión |

## Contexto previo en la misma línea de trabajo

- `docs/ai/LANDING_REDESIGN_PLAN.md`
- `docs/ai/sessions/2026-05-28-agent-landing-paleta-a-dark.md`
- `docs/ai/sessions/2026-05-28-agent-saas-admin-usuarios-talleres.md`

## Mensaje clave para defensa / handoff

- **Crear taller** = `/taller/registro` + `POST /api/app/taller/registro`.
- **Login** = `/taller` + auth; no crea entidades de taller.
- **Admin** = otro flujo (`POST /api/talleres/`) con `tenant_id` y responsable preexistente.

## Próximo paso sugerido

- Abrir `sequence-taller-registro-login.puml` en PlantUML o EA y enlazar en matriz de trazabilidad cuando exista `TRACEABILITY_MATRIX.md`.
