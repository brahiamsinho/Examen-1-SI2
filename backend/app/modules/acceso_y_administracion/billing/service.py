from __future__ import annotations

from datetime import datetime, timezone

import anyio
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.timeutil import utc_now_naive
from app.modules.acceso_y_administracion.billing import stripe_saas_client
from app.modules.acceso_y_administracion.tenants.models import (
    EstadoSuscripcionTenantEnum,
    Tenant,
)
from app.modules.acceso_y_administracion.tenants import service as tenants_service


def _stripe_saas_ready() -> bool:
    return bool(settings.stripe_enabled and settings.stripe_saas_price_id)


async def ensure_stripe_customer(db: AsyncSession, tenant: Tenant) -> Tenant:
    if tenant.stripe_customer_id:
        return tenant
    if not settings.stripe_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe no configurado (STRIPE_SECRET_KEY).",
        )
    import stripe

    def _create() -> str:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        c = stripe.Customer.create(
            name=tenant.nombre,
            metadata={"tenant_id": str(tenant.id), "tenant_slug": tenant.slug},
        )
        return c.id

    cid = await anyio.to_thread.run_sync(_create)
    return await tenants_service.link_stripe_customer(db, tenant.id, cid)


async def crear_checkout_session(
    db: AsyncSession,
    tenant_id: int,
    *,
    success_url: str,
    cancel_url: str,
    price_id: str | None = None,
) -> dict:
    if not settings.stripe_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Billing SaaS no configurado (STRIPE_SECRET_KEY).",
        )
    tenant = await ensure_stripe_customer(db, await tenants_service.get_tenant_by_id(db, tenant_id))
    resolved_price = (price_id or settings.stripe_saas_price_id or "").strip()
    if not resolved_price:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No hay Price ID de Stripe (plan o STRIPE_SAAS_PRICE_STARTER).",
        )

    def _run() -> dict:
        return stripe_saas_client.crear_checkout_suscripcion(
            secret_key=settings.STRIPE_SECRET_KEY,
            customer_id=tenant.stripe_customer_id,
            price_id=resolved_price,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"tenant_id": str(tenant.id), "tenant_slug": tenant.slug},
        )

    out = await anyio.to_thread.run_sync(_run)
    if not out.get("url"):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Stripe no devolvió URL de checkout.",
        )
    return out


async def crear_billing_portal(
    db: AsyncSession, tenant_id: int, *, return_url: str
) -> dict:
    if not settings.stripe_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Stripe no configurado.")
    tenant = await tenants_service.get_tenant_by_id(db, tenant_id)
    if not tenant.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El tenant no tiene cliente Stripe. Inicia checkout primero.",
        )

    def _run() -> dict:
        return stripe_saas_client.crear_portal_facturacion(
            secret_key=settings.STRIPE_SECRET_KEY,
            customer_id=tenant.stripe_customer_id,
            return_url=return_url,
        )

    return await anyio.to_thread.run_sync(_run)


def _map_subscription_status(stripe_status: str) -> EstadoSuscripcionTenantEnum:
    m = {
        "trialing": EstadoSuscripcionTenantEnum.TRIAL,
        "active": EstadoSuscripcionTenantEnum.ACTIVA,
        "past_due": EstadoSuscripcionTenantEnum.PAST_DUE,
        "canceled": EstadoSuscripcionTenantEnum.CANCELADA,
        "unpaid": EstadoSuscripcionTenantEnum.PAST_DUE,
        "paused": EstadoSuscripcionTenantEnum.SUSPENDIDA,
    }
    return m.get(stripe_status, EstadoSuscripcionTenantEnum.ACTIVA)


async def aplicar_evento_stripe_saas(db: AsyncSession, event: object) -> None:
    etype = getattr(event, "type", None)
    data_obj = getattr(getattr(event, "data", None), "object", None)
    if data_obj is None:
        return

    tenant_id: int | None = None
    meta = getattr(data_obj, "metadata", None) or {}
    if isinstance(meta, dict) and meta.get("tenant_id"):
        tenant_id = int(meta["tenant_id"])
    elif getattr(data_obj, "customer", None):
        cid = str(data_obj.customer)
        from sqlalchemy import select

        r = await db.execute(
            select(Tenant).where(Tenant.stripe_customer_id == cid)
        )
        row = r.scalar_one_or_none()
        if row:
            tenant_id = row.id

    if tenant_id is None:
        return

    tenant = await tenants_service.get_tenant_by_id(db, tenant_id)
    now = utc_now_naive()

    if etype == "checkout.session.completed":
        sub_id = getattr(data_obj, "subscription", None)
        if sub_id:
            tenant.stripe_subscription_id = str(sub_id)
            tenant.subscription_status = EstadoSuscripcionTenantEnum.ACTIVA
            tenant.updated_at = now
        return

    if etype in (
        "customer.subscription.updated",
        "customer.subscription.deleted",
    ):
        sub_id = getattr(data_obj, "id", None)
        status_raw = getattr(data_obj, "status", "active")
        if sub_id:
            tenant.stripe_subscription_id = str(sub_id)
        tenant.subscription_status = _map_subscription_status(str(status_raw))
        period_end = getattr(data_obj, "current_period_end", None)
        if period_end:
            tenant.subscription_ends_at = datetime.fromtimestamp(
                int(period_end), tz=timezone.utc
            ).replace(tzinfo=None)
        if etype == "customer.subscription.deleted":
            tenant.subscription_status = EstadoSuscripcionTenantEnum.CANCELADA
        tenant.updated_at = now


async def procesar_webhook_stripe_saas(
    db: AsyncSession, payload: bytes, sig_header: str | None
) -> None:
    secret = settings.STRIPE_SAAS_WEBHOOK_SECRET
    if not secret or not settings.stripe_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Webhook SaaS no configurado.")
    if not sig_header:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Falta Stripe-Signature")

    def _parse():
        return stripe_saas_client.construir_evento_webhook(
            payload=payload,
            sig_header=sig_header,
            webhook_secret=secret,
        )

    try:
        event = await anyio.to_thread.run_sync(_parse)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Firma webhook inválida") from exc

    await aplicar_evento_stripe_saas(db, event)
