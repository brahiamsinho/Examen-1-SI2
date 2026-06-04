from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import bind_auth_context, get_auth_context
from app.core.tenant import AuthContext
from app.modules.acceso_y_administracion.admin_finanzas import service
from app.modules.acceso_y_administracion.admin_finanzas.schemas import (
    AdminFinanzasReportes,
    AdminFinanzasResumen,
)

router = APIRouter(prefix="/admin/finanzas", tags=["Admin - Finanzas"])


def _resolve_tenant_scope(ctx: AuthContext, tenant_id: int | None) -> int | None:
    if ctx.is_platform_superadmin:
        return tenant_id
    if ctx.tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sin tenant asignado.",
        )
    if tenant_id is not None and tenant_id != ctx.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes consultar finanzas de otro tenant.",
        )
    return ctx.tenant_id


@router.get("/resumen", response_model=AdminFinanzasResumen)
async def obtener_finanzas_resumen(
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
    tenant_id: int | None = Query(default=None, description="Solo superadmin plataforma"),
    ctx: AuthContext = Depends(bind_auth_context),
    db: AsyncSession = Depends(get_db),
) -> AdminFinanzasResumen:
    scope = _resolve_tenant_scope(ctx, tenant_id)
    data = await service.get_finanzas_resumen(db, desde=desde, hasta=hasta, tenant_id=scope)
    return AdminFinanzasResumen.model_validate(data)


@router.get("/reportes", response_model=AdminFinanzasReportes)
async def obtener_finanzas_reportes(
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
    tenant_id: int | None = Query(default=None, description="Solo superadmin plataforma"),
    ctx: AuthContext = Depends(bind_auth_context),
    db: AsyncSession = Depends(get_db),
) -> AdminFinanzasReportes:
    scope = _resolve_tenant_scope(ctx, tenant_id)
    data = await service.get_finanzas_reportes(db, desde=desde, hasta=hasta, tenant_id=scope)
    return AdminFinanzasReportes.model_validate(data)
