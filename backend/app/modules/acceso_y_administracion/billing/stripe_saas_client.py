"""Stripe Billing (suscripción SaaS del tenant). Ejecutar con anyio.to_thread.run_sync."""
from __future__ import annotations

from typing import Any

import stripe


def crear_checkout_suscripcion_publica(
    *,
    secret_key: str,
    price_id: str,
    customer_email: str,
    success_url: str,
    cancel_url: str,
    metadata: dict[str, str],
) -> dict[str, Any]:
    stripe.api_key = secret_key
    session = stripe.checkout.Session.create(
        mode="subscription",
        customer_email=customer_email,
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata=metadata,
    )
    return {"id": session.id, "url": session.url}


def crear_checkout_suscripcion(
    *,
    secret_key: str,
    customer_id: str,
    price_id: str,
    success_url: str,
    cancel_url: str,
    metadata: dict[str, str],
) -> dict[str, Any]:
    stripe.api_key = secret_key
    session = stripe.checkout.Session.create(
        mode="subscription",
        customer=customer_id,
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata=metadata,
    )
    return {"id": session.id, "url": session.url}


def crear_portal_facturacion(
    *, secret_key: str, customer_id: str, return_url: str
) -> dict[str, Any]:
    stripe.api_key = secret_key
    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return {"url": session.url}


def obtener_sesion_checkout(*, secret_key: str, session_id: str) -> Any:
    stripe.api_key = secret_key
    return stripe.checkout.Session.retrieve(session_id)


def construir_evento_webhook(
    *, payload: bytes, sig_header: str, webhook_secret: str
) -> Any:
    return stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
