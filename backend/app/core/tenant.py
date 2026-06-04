# Multi-tenant SaaS — utilidades transversales (shared schema + tenant_id).
from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, status

from app.modules.acceso_y_administracion.usuarios.models import Usuario

PLATFORM_SUPERADMIN_ROLE = "ADMIN"


@dataclass(frozen=True)
class AuthContext:
    """Usuario autenticado + alcance de tenant para la petición."""

    user: Usuario
    roles: list[str]
    tenant_id: int | None
    is_platform_superadmin: bool

    @property
    def effective_tenant_id(self) -> int | None:
        """Tenant activo para filtrar datos (None = vista global plataforma)."""
        if self.is_platform_superadmin:
            return None
        return self.tenant_id


def is_platform_superadmin(user: Usuario, roles: list[str]) -> bool:
    return user.tenant_id is None and PLATFORM_SUPERADMIN_ROLE in roles


def assert_tenant_access(
    ctx: AuthContext,
    resource_tenant_id: int | None,
    *,
    detail: str = "Recurso fuera de tu organización (tenant).",
) -> None:
    if ctx.is_platform_superadmin:
        return
    if resource_tenant_id is None or ctx.tenant_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
    if resource_tenant_id != ctx.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def require_tenant_membership(ctx: AuthContext) -> int:
    if ctx.tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operación reservada a usuarios de un tenant. Use cuenta de plataforma solo para administración global.",
        )
    return ctx.tenant_id
