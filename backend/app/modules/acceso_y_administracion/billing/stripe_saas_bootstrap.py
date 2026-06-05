"""Bootstrap de Price IDs SaaS: sincroniza `.env` → BD y crea precios en Stripe test si faltan."""
from __future__ import annotations

import logging
from decimal import Decimal

import anyio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.timeutil import utc_now_naive
from app.modules.acceso_y_administracion.billing.stripe_price_id import is_valid_stripe_price_id
from app.modules.acceso_y_administracion.billing.stripe_price_resolver import (
    env_stripe_price_id_for_slug,
    resolve_effective_stripe_price_id,
)
from app.modules.acceso_y_administracion.pricing_plans.models import PricingPlan
from app.modules.acceso_y_administracion.pricing_plans.service import invalidate_public_plans_cache

_log = logging.getLogger(__name__)

_BOOTSTRAP_METADATA_KEY = "emergenciasviales_plan_slug"


def _find_existing_price_id(slug: str) -> str | None:
    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY
    prices = stripe.Price.list(active=True, limit=100)
    for price in prices.auto_paging_iter():
        meta = price.metadata or {}
        if meta.get(_BOOTSTRAP_METADATA_KEY) == slug or meta.get("plan_slug") == slug:
            if is_valid_stripe_price_id(price.id):
                return price.id
    return None


def _create_recurring_price(
    *,
    slug: str,
    name: str,
    amount_bob: Decimal,
    currency: str,
) -> str:
    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY
    product = stripe.Product.create(
        name=f"EmergenciasViales — {name}",
        metadata={_BOOTSTRAP_METADATA_KEY: slug, "plan_slug": slug, "source": "saas_bootstrap"},
    )
    unit_amount = int(round(float(amount_bob) * 100))
    if unit_amount <= 0:
        raise ValueError(f"Plan {slug}: monto mensual inválido para Stripe ({amount_bob})")
    price = stripe.Price.create(
        product=product.id,
        unit_amount=unit_amount,
        currency=(currency or "BOB").strip().lower(),
        recurring={"interval": "month"},
        metadata={_BOOTSTRAP_METADATA_KEY: slug, "plan_slug": slug, "source": "saas_bootstrap"},
    )
    return price.id


def _provision_price_for_plan(slug: str, name: str, amount_bob: Decimal, currency: str) -> str:
    existing = _find_existing_price_id(slug)
    if existing:
        return existing
    return _create_recurring_price(slug=slug, name=name, amount_bob=amount_bob, currency=currency)


async def ensure_saas_stripe_prices(db: AsyncSession) -> None:
    """
    Al arrancar con STRIPE_SECRET_KEY:
    1) Sincroniza Price IDs válidos del `.env` a `pricing_plans` si la BD tiene vacío/inválido.
    2) Si STRIPE_SAAS_AUTO_BOOTSTRAP_PRICES=true y sigue faltando, crea Products/Prices en Stripe test.
    """
    if not settings.stripe_enabled:
        return

    rows = (await db.execute(select(PricingPlan).order_by(PricingPlan.sort_order))).scalars().all()
    changed = False

    for row in rows:
        stored = (row.stripe_price_id or "").strip()
        if float(row.price_monthly_bob or 0) <= 0:
            if stored and not is_valid_stripe_price_id(stored):
                row.stripe_price_id = None
                row.updated_at = utc_now_naive()
                changed = True
                _log.info("Plan %s: Price ID inválido eliminado (plan gratuito)", row.slug)
            continue

        stored = (row.stripe_price_id or "").strip()
        env_id = env_stripe_price_id_for_slug(row.slug)
        effective = resolve_effective_stripe_price_id(stored, row.slug)

        if effective and not is_valid_stripe_price_id(stored):
            row.stripe_price_id = effective
            row.updated_at = utc_now_naive()
            changed = True
            source = "env" if effective == env_id else "db"
            _log.info("Plan %s: Price ID sincronizado desde %s", row.slug, source)
            continue

        if effective:
            continue

        if not settings.STRIPE_SAAS_AUTO_BOOTSTRAP_PRICES:
            _log.warning(
                "Plan %s sin Price ID válido (BD/env). Activa STRIPE_SAAS_AUTO_BOOTSTRAP_PRICES "
                "o configura STRIPE_SAAS_PRICE_PRO/MAX en .env / Admin.",
                row.slug,
            )
            continue

        def _run() -> str:
            return _provision_price_for_plan(
                slug=row.slug,
                name=row.name,
                amount_bob=row.price_monthly_bob or Decimal("0"),
                currency=row.currency or "BOB",
            )

        try:
            new_price_id = await anyio.to_thread.run_sync(_run)
        except Exception as exc:
            _log.error("No se pudo crear Price ID en Stripe para plan %s: %s", row.slug, exc)
            continue

        if is_valid_stripe_price_id(new_price_id):
            row.stripe_price_id = new_price_id
            row.updated_at = utc_now_naive()
            changed = True
            _log.info("Plan %s: Price ID creado en Stripe (%s)", row.slug, new_price_id)

    if changed:
        await db.flush()
        invalidate_public_plans_cache()
        await db.commit()
