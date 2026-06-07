from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import bind_auth_context, get_current_user, require_permission
from app.core.tenant import AuthContext
from app.core.tenant_context import effective_list_tenant_id
from app.modules.acceso_y_administracion.admin_dashboard import service
from app.modules.acceso_y_administracion.admin_dashboard.kpis import get_panel_kpis
from app.modules.acceso_y_administracion.admin_dashboard.schemas import AdminKpisRead, AdminPanelOverview
from app.modules.acceso_y_administracion.admin_finanzas.router import _resolve_tenant_scope

router = APIRouter(prefix="/admin/panel", tags=["Admin - Panel"])


@router.get("/overview", response_model=AdminPanelOverview)
async def panel_overview(
    tenant_id: int | None = Query(default=None, description="Filtro tenant (solo superadmin)"),
    ctx: AuthContext = Depends(bind_auth_context),
    _=Depends(get_current_user),
) -> AdminPanelOverview:
    scope = effective_list_tenant_id(ctx, tenant_id)
    data = await service.get_panel_overview(tenant_id=scope)
    return AdminPanelOverview.model_validate(data)


@router.get(
    "/kpis",
    response_model=AdminKpisRead,
    dependencies=[Depends(require_permission("reportes:leer"))],
)
async def panel_kpis(
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
    tenant_id: int | None = Query(default=None, description="Solo superadmin plataforma"),
    ctx: AuthContext = Depends(bind_auth_context),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
) -> AdminKpisRead:
    """CU46 — KPIs operativos y financieros del administrador."""
    scope = _resolve_tenant_scope(ctx, tenant_id)
    data = await get_panel_kpis(db, desde=desde, hasta=hasta, tenant_id=scope)
    return AdminKpisRead.model_validate(data)
