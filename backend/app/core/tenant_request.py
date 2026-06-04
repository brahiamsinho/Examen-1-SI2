# Resolver tenant_id desde slug de la petición (header / subdominio).
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.tenant_context import get_request_tenant_slug
from app.modules.acceso_y_administracion.tenants import service as tenants_service
from app.modules.acceso_y_administracion.tenants.models import Tenant


async def resolve_tenant_id_for_request(
    db: AsyncSession, *, default_slug: str | None = None
) -> int:
    """
    Usa X-Tenant-Slug / subdominio (contextvar) o tenant por defecto (demo-sc).
    """
    slug = get_request_tenant_slug() or default_slug
    if slug:
        t = await tenants_service.get_tenant_by_slug(db, slug.strip().lower())
        if t is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organización no encontrada",
            )
        return t.id
    t = await tenants_service.ensure_default_tenant(db)
    return t.id
