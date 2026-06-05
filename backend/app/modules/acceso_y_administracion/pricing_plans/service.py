from __future__ import annotations

import time
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.timeutil import utc_now_naive
from app.modules.acceso_y_administracion.pricing_plans.models import PricingPlan
from app.modules.acceso_y_administracion.pricing_plans.schemas import PricingPlanRead

_PUBLIC_PLANS_CACHE_TTL_S = 300
_public_plans_cache: tuple[float, list[PricingPlanRead]] | None = None


def _to_read(row: PricingPlan) -> PricingPlanRead:
    benefits = row.benefits if isinstance(row.benefits, list) else []
    return PricingPlanRead(
        id=row.id,
        slug=row.slug,
        name=row.name,
        description=row.description,
        price_monthly_bob=row.price_monthly_bob or Decimal("0"),
        currency=row.currency or "BOB",
        benefits=[str(b) for b in benefits],
        featured=bool(row.featured),
        badge=row.badge,
        cta_label=row.cta_label,
        cta_router_link=row.cta_router_link,
        cta_href=row.cta_href,
        stripe_price_id=row.stripe_price_id,
        sort_order=row.sort_order,
        active=bool(row.active),
    )


def invalidate_public_plans_cache() -> None:
    global _public_plans_cache
    _public_plans_cache = None


async def list_plans(db: AsyncSession, *, active_only: bool = False) -> list[PricingPlanRead]:
    stmt = select(PricingPlan).order_by(PricingPlan.sort_order, PricingPlan.id)
    if active_only:
        stmt = stmt.where(PricingPlan.active.is_(True))
    rows = (await db.execute(stmt)).scalars().all()
    return [_to_read(r) for r in rows]


async def list_public_plans_cached(db: AsyncSession) -> list[PricingPlanRead]:
    """Planes activos para landing con cache en memoria (TTL 5 min)."""
    global _public_plans_cache
    now = time.monotonic()
    if _public_plans_cache is not None:
        cached_at, cached_plans = _public_plans_cache
        if now - cached_at < _PUBLIC_PLANS_CACHE_TTL_S:
            return cached_plans

    plans = await list_plans(db, active_only=True)
    _public_plans_cache = (now, plans)
    return plans


async def get_plan_by_slug(db: AsyncSession, slug: str) -> PricingPlan:
    r = await db.execute(select(PricingPlan).where(PricingPlan.slug == slug.strip().lower()))
    row = r.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Plan no encontrado.")
    return row


async def update_plan(db: AsyncSession, slug: str, data: dict) -> PricingPlanRead:
    row = await get_plan_by_slug(db, slug)
    for key, val in data.items():
        if val is None:
            continue
        setattr(row, key, val)
    row.updated_at = utc_now_naive()
    await db.flush()
    invalidate_public_plans_cache()
    return _to_read(row)


def stripe_public_config() -> dict:
    return {
        "enabled": settings.stripe_enabled,
        "publishable_key": (settings.STRIPE_PUBLISHABLE_KEY or "").strip() or None,
    }
