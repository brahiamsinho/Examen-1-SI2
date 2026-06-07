"""Resuelve el Price ID efectivo de un plan: BD válida → variables .env por slug."""
from __future__ import annotations

from app.core.config import settings
from app.modules.acceso_y_administracion.billing.stripe_price_id import is_valid_stripe_price_id


def env_stripe_price_id_for_slug(slug: str) -> str | None:
    """Mapeo slug comercial → variable STRIPE_SAAS_PRICE_* del `.env`."""
    key = (slug or "").strip().lower()
    mapping = {
        "free": settings.STRIPE_SAAS_PRICE_STARTER,
        "starter": settings.STRIPE_SAAS_PRICE_STARTER,
        "pro": settings.STRIPE_SAAS_PRICE_PRO,
        "max": settings.STRIPE_SAAS_PRICE_MAX,
    }
    raw = mapping.get(key)
    pid = (raw or "").strip()
    return pid if is_valid_stripe_price_id(pid) else None


def resolve_effective_stripe_price_id(db_value: str | None, slug: str) -> str | None:
    """Price ID listo para checkout: prioriza BD si es válido; si no, cae al `.env`."""
    stored = (db_value or "").strip()
    if is_valid_stripe_price_id(stored):
        return stored
    return env_stripe_price_id_for_slug(slug)
