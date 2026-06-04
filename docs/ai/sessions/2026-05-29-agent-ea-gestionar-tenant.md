# Sesión 2026-05-29 — Análisis: Gestionar tenant o red de talleres

## EA
- Paquete: `/Model/Clase` (27)
- Diagrama: **`class Gestionar tenant`** (ID **30**)

## Patrón BCE
| Artefacto | ID |
|-----------|-----|
| Actor Administrador | 165 |
| V.ListaOrganizaciones | 166 |
| V.FormularioTenant | 167 |
| TenantAdminController | 168 |
| StripeBillingService | 169 (opcional paso 5) |
| Tenant | 170 |
| Taller, Usuario | 171, 172 |

## API prevista (CU)
- `GET/POST /api/admin/tenants`
- `PATCH /api/admin/tenants/{id}`
- `billing/` Stripe SaaS

## ER
- Tenant `agrupa` Taller / Usuario (`1` .. `0..*`)

## Dependencias
- TenantAdminController → Tenant
- StripeBillingService → Tenant (suscripción)
- Sin punteada a Taller/Usuario (aislamiento vía `tenant_id` en ER)

## Estado código (2026-05-29)
- **No implementado aún** en repo: sin rutas `/api/admin/tenants`, sin `tenant_id` en modelos, sin `/admin/panel/organizaciones`.
- Diagrama = **diseño lógico / objetivo** alineado al ER conceptual y al CU.

## Excepciones (ficha CU)
- Slug duplicado, suscripción vencida, admin no superadmin
