# Reglas de acceso según estado de suscripción SaaS del tenant.
from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException, status

from app.core.timeutil import utc_now_naive
from app.modules.acceso_y_administracion.tenants.models import (
    EstadoSuscripcionTenantEnum,
    EstadoTenantEnum,
    Tenant,
)

_WRITE_ALLOWED = frozenset(
    {
        EstadoSuscripcionTenantEnum.TRIAL,
        EstadoSuscripcionTenantEnum.ACTIVA,
    }
)


def subscription_allows_read(tenant: Tenant) -> bool:
    if tenant.estado != EstadoTenantEnum.ACTIVO:
        return False
    if tenant.subscription_status in (
        EstadoSuscripcionTenantEnum.CANCELADA,
        EstadoSuscripcionTenantEnum.SUSPENDIDA,
    ):
        return False
    if tenant.subscription_status == EstadoSuscripcionTenantEnum.TRIAL:
        if tenant.subscription_ends_at and tenant.subscription_ends_at < utc_now_naive():
            return False
    return True


def subscription_allows_write(tenant: Tenant) -> bool:
    if not subscription_allows_read(tenant):
        return False
    return tenant.subscription_status in _WRITE_ALLOWED


def assert_tenant_subscription_write(tenant: Tenant) -> None:
    if subscription_allows_write(tenant):
        return
    detail = "La suscripción de tu organización no permite esta operación."
    if tenant.subscription_status == EstadoSuscripcionTenantEnum.PAST_DUE:
        detail = "Suscripción vencida. Regulariza el pago en el portal de facturación."
    raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=detail)
