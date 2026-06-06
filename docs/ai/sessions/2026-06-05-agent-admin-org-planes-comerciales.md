# Sesión 2026-06-05 — Admin organizaciones: planes comerciales Free / Pro / Max

## Problema

El modal «Nueva organización» en `/admin/panel/organizaciones` mostraba enums internos de BD (`FREE`, `STARTER`, `PRO`, `ENTERPRISE`), distintos de los planes comerciales visibles en landing, **Planes y precios** y portal taller (**Free / Pro / Max**).

## Solución

### Frontend

- Nuevo `frontend/src/app/core/utils/saas-plan-tiers.ts`:
  - `CommercialPlanSlug`: `free` | `pro` | `max`
  - `planTenantToCommercialSlug` / `commercialSlugToPlanTenant`
  - `DEFAULT_COMMERCIAL_PLANS` como fallback
- `admin-organizaciones.component.ts`:
  - Formularios usan `commercialPlanSlug`
  - Catálogo desde `AdminApiService.listPricingPlans()`
  - Al crear/editar convierte a enum BD antes del API
- `admin-organizaciones.component.html`:
  - Select «Plan comercial» con nombre + precio
  - Tabla muestra nombre comercial; badge `legacy` si plan interno `STARTER`
- Estilos `.org__plan-name`, `.org__plan-legacy` en SCSS

### Backend

- Default al crear tenant: `PlanTenantEnum.FREE` (antes `STARTER`) en `schemas.py`, `service.py`, `plan_tiers.py`
- Seed `demo-sc` conserva `STARTER` para demostrar mapeo legacy → Free comercial

## Mapeo

| Enum BD     | Plan comercial |
|-------------|----------------|
| FREE        | Free           |
| STARTER     | Free (legacy)  |
| PRO         | Pro            |
| ENTERPRISE  | Max            |

## Verificación

```bash
cd frontend && npm run build
```

Manual: crear org con plan Pro → comprobar en taller suscripción que aparece Pro.
