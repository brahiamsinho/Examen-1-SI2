"""Validación de Stripe Price ID (formato price_...)."""
from __future__ import annotations

from fastapi import HTTPException, status


def is_valid_stripe_price_id(value: str | None) -> bool:
    pid = (value or "").strip()
    return pid.startswith("price_") and len(pid) > len("price_")


def assert_valid_stripe_price_id(value: str, *, context: str = "Price ID de Stripe") -> str:
    pid = value.strip()
    if not is_valid_stripe_price_id(pid):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"{context} inválido: debe ser el ID del objeto Price en Stripe "
                f"(ej. price_1ABC...), no el monto en BOB ni un número suelto. "
                f"Configuralo en Admin → Planes y precios o en Stripe Dashboard → Products."
            ),
        )
    return pid
