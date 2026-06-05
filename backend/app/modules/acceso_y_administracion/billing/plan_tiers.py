"""Resolución de plan comercial (pricing_plans) vs plan del tenant."""
from __future__ import annotations

from app.modules.acceso_y_administracion.billing.stripe_price_resolver import (
    resolve_effective_stripe_price_id,
)
from app.modules.acceso_y_administracion.pricing_plans.schemas import PricingPlanRead
from app.modules.acceso_y_administracion.tenants.models import PlanTenantEnum, Tenant

PLAN_ENUM_TO_DEFAULT_SLUG: dict[PlanTenantEnum, str] = {
    PlanTenantEnum.FREE: "free",
    PlanTenantEnum.STARTER: "free",
    PlanTenantEnum.PRO: "pro",
    PlanTenantEnum.ENTERPRISE: "max",
}

SLUG_TO_PLAN_ENUM: dict[str, PlanTenantEnum] = {
    "free": PlanTenantEnum.FREE,
    "pro": PlanTenantEnum.PRO,
    "max": PlanTenantEnum.ENTERPRISE,
}


def resolve_current_plan_slug(tenant: Tenant, plans: list[PricingPlanRead]) -> str:
    price_id = (tenant.stripe_price_id or "").strip()
    if price_id:
        for plan in plans:
            pid = resolve_effective_stripe_price_id(plan.stripe_price_id, plan.slug)
            if pid and pid == price_id:
                return plan.slug
    return PLAN_ENUM_TO_DEFAULT_SLUG.get(tenant.plan, "free")


def sort_order_for_slug(plans: list[PricingPlanRead], slug: str) -> int:
    for plan in plans:
        if plan.slug == slug:
            return plan.sort_order
    return 0


def plan_enum_for_slug(slug: str) -> PlanTenantEnum:
    return SLUG_TO_PLAN_ENUM.get(slug.strip().lower(), PlanTenantEnum.STARTER)
