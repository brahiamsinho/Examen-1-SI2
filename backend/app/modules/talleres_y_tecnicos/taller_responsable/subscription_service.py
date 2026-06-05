from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.acceso_y_administracion.billing import plan_tiers
from app.modules.acceso_y_administracion.billing import service as billing_service
from app.modules.acceso_y_administracion.billing.stripe_price_id import is_valid_stripe_price_id
from app.modules.acceso_y_administracion.billing.stripe_price_resolver import (
    resolve_effective_stripe_price_id,
)
from app.modules.acceso_y_administracion.bitacora.models import AccionBitacoraEnum
from app.modules.acceso_y_administracion.bitacora.service import registrar_accion
from app.modules.acceso_y_administracion.pricing_plans import service as pricing_service
from app.modules.acceso_y_administracion.tenants import service as tenants_service
from app.modules.acceso_y_administracion.usuarios.models import Usuario
from app.modules.talleres_y_tecnicos.taller_responsable.schemas import (
    TallerPlanOptionRead,
    TallerSuscripcionCheckoutOut,
    TallerSuscripcionRead,
)


async def get_suscripcion_portal(db: AsyncSession, user: Usuario) -> TallerSuscripcionRead:
    if user.tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta no está asociada a una organización SaaS.",
        )

    tenant = await tenants_service.get_tenant_by_id(db, user.tenant_id)
    catalog = await pricing_service.list_plans(db, active_only=True)
    current_slug = plan_tiers.resolve_current_plan_slug(tenant, catalog)
    current_order = plan_tiers.sort_order_for_slug(catalog, current_slug)
    current_name = next((p.name for p in catalog if p.slug == current_slug), current_slug)

    plan_options: list[TallerPlanOptionRead] = []
    for plan in catalog:
        price = float(plan.price_monthly_bob or 0)
        effective_price_id = resolve_effective_stripe_price_id(plan.stripe_price_id, plan.slug)
        stripe_ready = is_valid_stripe_price_id(effective_price_id) and price > 0
        is_current = plan.slug == current_slug
        can_upgrade = plan.sort_order > current_order and stripe_ready and settings.stripe_enabled
        plan_options.append(
            TallerPlanOptionRead(
                slug=plan.slug,
                name=plan.name,
                description=plan.description,
                price_monthly_bob=price,
                currency=plan.currency or "BOB",
                benefits=list(plan.benefits or []),
                featured=bool(plan.featured),
                badge=plan.badge,
                sort_order=plan.sort_order,
                is_current=is_current,
                can_upgrade=can_upgrade,
                stripe_checkout_available=stripe_ready and settings.stripe_enabled,
            )
        )

    return TallerSuscripcionRead(
        tenant_nombre=tenant.nombre,
        tenant_slug=tenant.slug,
        current_plan_slug=current_slug,
        current_plan_name=current_name,
        subscription_status=tenant.subscription_status.value,
        subscription_ends_at=tenant.subscription_ends_at,
        stripe_enabled=settings.stripe_enabled,
        plans=plan_options,
    )


async def crear_checkout_upgrade(
    db: AsyncSession,
    user: Usuario,
    *,
    plan_slug: str,
    success_url: str,
    cancel_url: str,
) -> TallerSuscripcionCheckoutOut:
    if user.tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta no está asociada a una organización SaaS.",
        )

    data = await billing_service.crear_checkout_upgrade(
        db,
        user.tenant_id,
        plan_slug,
        success_url=success_url,
        cancel_url=cancel_url,
    )
    await registrar_accion(
        db,
        modulo="taller_portal",
        entidad="suscripcion",
        accion=AccionBitacoraEnum.CONSULTAR,
        descripcion=f"Checkout upgrade plan={plan_slug}",
        usuario_id=user.id,
    )
    return TallerSuscripcionCheckoutOut(checkout_url=data["url"], session_id=data["id"])


async def confirmar_checkout_suscripcion(
    db: AsyncSession,
    user: Usuario,
    *,
    session_id: str,
) -> TallerSuscripcionRead:
    if user.tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta no está asociada a una organización SaaS.",
        )

    await billing_service.confirmar_checkout_session(db, user.tenant_id, session_id)
    await registrar_accion(
        db,
        modulo="taller_portal",
        entidad="suscripcion",
        accion=AccionBitacoraEnum.ACTUALIZAR,
        descripcion=f"Suscripción confirmada tras checkout session_id={session_id[:24]}",
        usuario_id=user.id,
    )
    return await get_suscripcion_portal(db, user)
