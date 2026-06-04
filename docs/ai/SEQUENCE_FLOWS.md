# SEQUENCE_FLOWS.md — Índice de flujos documentados

**Última actualización:** 2026-05-28

Índice de flujos end-to-end del sistema con narrativa en `docs/ai/` y diagramas en `docs/diagrams/uml/`.

---

## Portal web taller

| Flujo | Narrativa | Diagrama UML |
|-------|-----------|--------------|
| Registro taller + responsable → verificación → login → panel | **[FLOWS_PORTAL_TALLER.md](./FLOWS_PORTAL_TALLER.md)** | `docs/diagrams/uml/sequence-taller-registro-login.puml` |
| Login genérico (auth) | `FLOWS_PORTAL_TALLER.md` §4 | `docs/diagrams/uml/sequence-auth-login.puml` |

**Decisión:** DEC-029 — registro y login son operaciones distintas.

---

## Admin SaaS

| Flujo | Narrativa |
|-------|-----------|
| Usuarios/talleres con `tenant_id` y slug | `docs/ai/sessions/2026-05-28-agent-saas-admin-usuarios-talleres.md` |
| SaaS fases 1–3 | `docs/ai/SAAS_PHASE3_PLAN.md`, `CURRENT_STATE.md` |

---

## Cliente móvil / emergencias

| Flujo | Diagrama |
|-------|----------|
| Alta emergencia cliente | `docs/diagrams/uml/sequence-emergencia-alta-cliente.puml` |
| Selección taller (CU37) | `docs/puds/casos-uso/CICLO4_DETALLE_CASOS_USO.md` |

---

## Landing pública

| Flujo | Documento |
|-------|-----------|
| CTAs → `/taller/registro` y `/taller` | `LANDING_REDESIGN_PLAN.md`, sesión `sessions/2026-05-28-agent-landing-paleta-a-dark.md` |

---

## Pendiente

- `TRACEABILITY_MATRIX.md` — filas RF/CU → módulo → `.puml`
- Secuencia admin «crear taller + responsable»
- Secuencia CU37 seleccionar taller (PlantUML dedicado)
