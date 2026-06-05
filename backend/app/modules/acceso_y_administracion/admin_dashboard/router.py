from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import bind_auth_context, get_current_user
from app.core.tenant import AuthContext
from app.core.tenant_context import effective_list_tenant_id
from app.modules.acceso_y_administracion.admin_dashboard import service
from app.modules.acceso_y_administracion.admin_dashboard.schemas import AdminPanelOverview

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
