# Sesión 2026-05-29 — Componentes por paquete funcional (FastAPI)

## Contexto

Réplica del diagrama de capas (Web → API → Service → Repository → PostgreSQL) para los **5 paquetes** del diagrama `pkg IDENTIFICAR PAQUETES - Casos de Uso`.

## Diagramas creados (`Model/Arquitectura`)

| ID | Nombre |
|----|--------|
| 33 | component PKG Seguimiento tiempo real |
| 36 | component PKG Seleccion taller y pagos |
| 37 | component PKG Offline sincronizacion |
| 35 | component PKG Analitica KPIs |
| 34 | component PKG Multi-tenant SaaS |

Elementos **215–267**, conectores **406–453**.

**2026-05-29:** Renombrados componentes — sin prefijos `CU##` en el diagrama (solo `mobile/`, `api/`, `service/`, `repository/`).

## Notas de implementación

- **Repository:** capa de diseño; solo `pagos/repository.py` tiene archivo explícito.
- **Offline (37):** CU de continuidad documentados como diseño; no hay outbox SQLite completo en mobile aún.
- **Tenant (34):** alineado a análisis de clases ID 30; backend sin `/api/admin/tenants`.
- **Presupuesto:** misma API que actualizar estado técnico (`PATCH` con `presupuesto_bob`).

## Guía

`docs/ai/EA_ARCHITECTURE_SYSTEM_GUIDE.md` — sección «Diagramas por paquete funcional».
