from __future__ import annotations

import anyio
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import require_platform_superadmin
from app.core.tenant import AuthContext
from app.modules.acceso_y_administracion.billing import stripe_saas_client
from app.modules.acceso_y_administracion.pricing_plans import service
from app.modules.acceso_y_administracion.pricing_plans.schemas import (
    CheckoutOut,
    PricingPlanRead,
    PricingPlanUpdate,
    PublicCheckoutIn,
    PublicPricingBootstrapRead,
    StripeConfigPublicRead,
)

_PUBLIC_CACHE_CONTROL = "public, max-age=300"

admin_router = APIRouter(prefix="/admin/pricing-plans", tags=["Admin - Planes y precios"])
public_router = APIRouter(prefix="/public/pricing", tags=["Public - Planes y precios"])


@admin_router.get("", response_model=list[PricingPlanRead])
async def listar_planes_admin(
    _ctx: AuthContext = Depends(require_platform_superadmin),
    db: AsyncSession = Depends(get_db),
) -> list[PricingPlanRead]:
    return await service.list_plans(db, active_only=False)


@admin_router.patch("/{slug}", response_model=PricingPlanRead)
async def actualizar_plan(
    slug: str,
    body: PricingPlanUpdate,
    _ctx: AuthContext = Depends(require_platform_superadmin),
    db: AsyncSession = Depends(get_db),
) -> PricingPlanRead:
    return await service.update_plan(db, slug, body.model_dump(exclude_unset=True))


@public_router.get("/bootstrap", response_model=PublicPricingBootstrapRead)
async def bootstrap_pricing_publico(
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> PublicPricingBootstrapRead:
    plans = await service.list_public_plans_cached(db)
    stripe = StripeConfigPublicRead(**service.stripe_public_config())
    response.headers["Cache-Control"] = _PUBLIC_CACHE_CONTROL
    return PublicPricingBootstrapRead(plans=plans, stripe=stripe)


@public_router.get("/plans", response_model=list[PricingPlanRead])
async def listar_planes_publicos(
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> list[PricingPlanRead]:
    plans = await service.list_public_plans_cached(db)
    response.headers["Cache-Control"] = _PUBLIC_CACHE_CONTROL
    return plans


@public_router.get("/stripe-config", response_model=StripeConfigPublicRead)
async def config_stripe_publico() -> StripeConfigPublicRead:
    cfg = service.stripe_public_config()
    return StripeConfigPublicRead(**cfg)


@public_router.post("/checkout", response_model=CheckoutOut, status_code=status.HTTP_201_CREATED)
async def checkout_plan_publico(
    body: PublicCheckoutIn,
    db: AsyncSession = Depends(get_db),
) -> CheckoutOut:
    if not settings.stripe_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe no configurado (STRIPE_SECRET_KEY).",
        )
    plan = await service.get_plan_by_slug(db, body.plan_slug)
    if not plan.active:
        raise HTTPException(status_code=400, detail="Plan no disponible.")
    from app.modules.acceso_y_administracion.billing.stripe_price_id import assert_valid_stripe_price_id
    from app.modules.acceso_y_administracion.billing.stripe_price_resolver import (
        resolve_effective_stripe_price_id,
    )

    price_id = resolve_effective_stripe_price_id(plan.stripe_price_id, plan.slug)
    if not price_id:
        if plan.price_monthly_bob and float(plan.price_monthly_bob) > 0:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Este plan no tiene Price ID de Stripe. Configurá .env (STRIPE_SAAS_PRICE_*) "
                    "o Admin → Planes y precios."
                ),
            )
        raise HTTPException(status_code=400, detail="El plan gratuito no usa checkout Stripe.")

    price_id = assert_valid_stripe_price_id(price_id)

    def _run() -> dict:
        import stripe

        try:
            return stripe_saas_client.crear_checkout_suscripcion_publica(
                secret_key=settings.STRIPE_SECRET_KEY,
                price_id=price_id,
                customer_email=str(body.email),
                success_url=body.success_url,
                cancel_url=body.cancel_url,
                metadata={"plan_slug": plan.slug, "source": "landing"},
            )
        except stripe.InvalidRequestError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Stripe rechazó el checkout: {exc.user_message or str(exc)}",
            ) from exc

    out = await anyio.to_thread.run_sync(_run)
    if not out.get("url"):
        raise HTTPException(status_code=502, detail="Stripe no devolvió URL de checkout.")
    return CheckoutOut(checkout_url=out["url"], session_id=out["id"])
