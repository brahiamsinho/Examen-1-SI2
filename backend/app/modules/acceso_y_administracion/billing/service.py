from __future__ import annotations

from datetime import datetime, timezone

import anyio
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.timeutil import utc_now_naive
from app.modules.acceso_y_administracion.billing import stripe_saas_client
from app.modules.acceso_y_administracion.billing.stripe_price_id import (
    assert_valid_stripe_price_id,
    is_valid_stripe_price_id,
)
from app.modules.acceso_y_administracion.billing.stripe_price_resolver import (
    resolve_effective_stripe_price_id,
)
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
    metadata: dict[str, str] | None = None,
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
    resolved_price = assert_valid_stripe_price_id(resolved_price)

    def _run() -> dict:
        import stripe

        try:
            return stripe_saas_client.crear_checkout_suscripcion(
                secret_key=settings.STRIPE_SECRET_KEY,
                customer_id=tenant.stripe_customer_id,
                price_id=resolved_price,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "tenant_id": str(tenant.id),
                    "tenant_slug": tenant.slug,
                    **({k: v for k, v in (metadata or {}).items() if v}),
                },
            )
        except stripe.InvalidRequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Stripe rechazó el checkout: {exc.user_message or str(exc)}",
            ) from exc

    out = await anyio.to_thread.run_sync(_run)
    if not out.get("url"):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Stripe no devolvió URL de checkout.",
        )
    return out


async def crear_checkout_upgrade(
    db: AsyncSession,
    tenant_id: int,
    plan_slug: str,
    *,
    success_url: str,
    cancel_url: str,
) -> dict:
    """Checkout Stripe solo hacia un plan superior al actual del tenant."""
    from app.modules.acceso_y_administracion.billing import plan_tiers
    from app.modules.acceso_y_administracion.pricing_plans import service as pricing_service

    tenant = await tenants_service.get_tenant_by_id(db, tenant_id)
    catalog = await pricing_service.list_plans(db, active_only=True)
    current_slug = plan_tiers.resolve_current_plan_slug(tenant, catalog)
    current_order = plan_tiers.sort_order_for_slug(catalog, current_slug)

    target = await pricing_service.get_plan_by_slug(db, plan_slug)
    if not target.active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Plan no disponible.")
    if target.sort_order <= current_order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo podés ascender a un plan superior. No se permite degradar.",
        )

    price_id = resolve_effective_stripe_price_id(target.stripe_price_id, target.slug)
    if not price_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"El plan «{target.name}» no tiene Price ID de Stripe. "
                "Configurá STRIPE_SAAS_PRICE_PRO/MAX en .env, activá bootstrap automático "
                "o pegá price_... en Admin → Planes y precios."
            ),
        )
    price_id = assert_valid_stripe_price_id(price_id)
    if float(target.price_monthly_bob or 0) <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El plan gratuito no requiere checkout.",
        )

    return await crear_checkout_session(
        db,
        tenant_id,
        success_url=success_url,
        cancel_url=cancel_url,
        price_id=price_id,
        metadata={"plan_slug": target.slug, "source": "taller_panel"},
    )


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


async def aplicar_checkout_session_completada(
    db: AsyncSession, tenant: Tenant, session: object
) -> None:
    """Actualiza tenant tras checkout exitoso (webhook o confirmación manual)."""
    now = utc_now_naive()
    meta = getattr(session, "metadata", None) or {}
    if not isinstance(meta, dict):
        meta = {}

    customer_id = getattr(session, "customer", None)
    if customer_id and not tenant.stripe_customer_id:
        tenant.stripe_customer_id = str(customer_id)

    sub_id = getattr(session, "subscription", None)
    if sub_id:
        tenant.stripe_subscription_id = str(sub_id)
        tenant.subscription_status = EstadoSuscripcionTenantEnum.ACTIVA
        tenant.updated_at = now

    plan_slug = meta.get("plan_slug")
    if plan_slug:
        from app.modules.acceso_y_administracion.billing import plan_tiers
        from app.modules.acceso_y_administracion.pricing_plans import service as pricing_service

        slug = str(plan_slug).strip().lower()
        try:
            plan_row = await pricing_service.get_plan_by_slug(db, slug)
            tenant.plan = plan_tiers.plan_enum_for_slug(slug)
            effective = resolve_effective_stripe_price_id(plan_row.stripe_price_id, slug)
            if effective:
                tenant.stripe_price_id = effective
        except HTTPException:
            tenant.plan = plan_tiers.plan_enum_for_slug(slug)
        tenant.updated_at = now


async def confirmar_checkout_session(
    db: AsyncSession, tenant_id: int, session_id: str
) -> Tenant:
    """Confirma pago consultando la sesión en Stripe (útil en local sin webhook)."""
    if not settings.stripe_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe no configurado (STRIPE_SECRET_KEY).",
        )

    sid = (session_id or "").strip()
    if not sid.startswith("cs_"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="session_id de Stripe inválido.",
        )

    def _retrieve() -> object:
        import stripe

        try:
            return stripe_saas_client.obtener_sesion_checkout(
                secret_key=settings.STRIPE_SECRET_KEY,
                session_id=sid,
            )
        except stripe.InvalidRequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Sesión de checkout no encontrada: {exc.user_message or str(exc)}",
            ) from exc

    session = await anyio.to_thread.run_sync(_retrieve)
    meta = getattr(session, "metadata", None) or {}
    if not isinstance(meta, dict):
        meta = {}
    meta_tenant = meta.get("tenant_id")
    if meta_tenant is not None and str(meta_tenant) != str(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La sesión de pago no pertenece a tu organización.",
        )

    session_status = getattr(session, "status", None)
    payment_status = getattr(session, "payment_status", None)
    if session_status != "complete" or payment_status not in ("paid", "no_payment_required"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El pago aún no está confirmado. Esperá unos segundos y recargá la página.",
        )

    tenant = await tenants_service.get_tenant_by_id(db, tenant_id)
    await aplicar_checkout_session_completada(db, tenant, session)
    return tenant


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
        await aplicar_checkout_session_completada(db, tenant, data_obj)
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
