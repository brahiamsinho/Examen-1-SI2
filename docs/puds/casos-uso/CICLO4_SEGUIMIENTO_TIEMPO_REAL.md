# Ciclo 4 — Casos de uso (matriz oficial CU36–CU40)

**Actualizado:** 2026-05-28  
**Detalle académico:** `CICLO4_DETALLE_CASOS_USO.md`  
**Diagramas:** `docs/diagrams/uml/usecases/ciclo4/` · EA paquete **7**  
**Memoria agente:** `docs/ai/CURRENT_STATE.md` · sesión `docs/ai/sessions/2026-06-02-agent-cu37-cu36-mobile.md`

## Matriz oficial

| ID | Caso de uso | Actor | Prioridad | Riesgo | Estado código |
|----|-------------|-------|-----------|--------|---------------|
| CU36 | Consultar ubicación del técnico en tiempo real | Cliente | Alta | Alto | **Implementado** (REST + mapa; polling 12 s en mobile; sin WebSocket) |
| CU37 | Seleccionar taller para realizar el servicio | Cliente | Alta | Alta | **Implementado** (candidatos + confirmación cliente; bandeja solo taller elegido) |
| CU38 | Procesar pago mediante pasarela | Cliente | Alta | Alta | **Implementado** (Stripe TARJETA si `STRIPE_*` en backend; resto simulado) |
| CU39 | Actualizar estado de atención del servicio | Técnico | Alta | Medio | **Implementado** |
| CU40 | Gestionar tenant o red de talleres | Administrador | Alta | Alta | **Implementado** (SaaS fases 1–3) |

## Paquetes código

| CU | Módulos principales |
|----|---------------------|
| CU36 | `incidentes/emergencias`, `mobile/cliente/emergencias` |
| CU37 | `modules/ai/` (`assignment/rank`), bandeja taller |
| CU38 | `pagos_y_comisiones/pagos`, `mobile/cliente/pagos`, Stripe |
| CU39 | `tecnico/emergencias`, PATCH estado + presupuesto |
| CU40 | `tenants/`, `admin-organizaciones`, `billing/`, RLS |

## Nota histórica

Versiones anteriores del Ciclo 4 incluían CU41–CU44 y otros nombres para CU37–CU40; quedaron **obsoletas** al adoptar esta matriz.
