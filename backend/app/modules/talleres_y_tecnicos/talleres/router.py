# app/modules/talleres/router.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import bind_auth_context, get_current_user
from app.core.tenant import AuthContext
from app.core.tenant_context import effective_list_tenant_id
from app.modules.talleres_y_tecnicos.talleres import service
from app.modules.talleres_y_tecnicos.talleres.schemas import (
    TallerCreate, TallerRead, TallerUpdate,
    TallerProvisionIn, TallerProvisionRead,
    TecnicoCreate, TecnicoRead, TecnicoUpdate,
    EspecialidadCreate, EspecialidadRead
)
from app.modules.acceso_y_administracion.usuarios.models import Usuario

router = APIRouter(prefix="/talleres", tags=["Talleres"])

@router.get("/", response_model=list[TallerRead])
async def listar_talleres(
    tenant_id: int | None = Query(default=None, description="Filtro tenant (solo superadmin)"),
    ctx: AuthContext = Depends(bind_auth_context),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    scope = effective_list_tenant_id(ctx, tenant_id)
    return await service.get_talleres(db, list_tenant_id=scope)

@router.post("/", response_model=TallerRead, status_code=201)
async def crear_taller(
    body: TallerCreate,
    ctx: AuthContext = Depends(bind_auth_context),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    data = body.model_dump()
    if ctx.is_platform_superadmin:
        if data.get("tenant_id") is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selecciona una organización (tenant_id) antes de crear el taller.",
            )
    else:
        data["tenant_id"] = ctx.tenant_id
    await service.validate_responsable_tenant(
        db, usuario_id=data["usuario_responsable_id"], tenant_id=data["tenant_id"]
    )
    return await service.create_taller(data, db, current_user.id)


@router.post("/provision", response_model=TallerProvisionRead, status_code=201)
async def provisionar_taller(
    body: TallerProvisionIn,
    ctx: AuthContext = Depends(bind_auth_context),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if ctx.is_platform_superadmin:
        if body.tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selecciona una organización (tenant_id) antes de crear el taller.",
            )
        tenant_id = body.tenant_id
    else:
        if ctx.tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tu cuenta no está asociada a una organización.",
            )
        tenant_id = ctx.tenant_id
    return await service.provision_taller_con_responsable(
        body, db, tenant_id=tenant_id, ejecutor_id=current_user.id
    )

@router.get("/{taller_id}", response_model=TallerRead)
async def obtener_taller(taller_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    return await service.get_taller_by_id(taller_id, db)

@router.put("/{taller_id}", response_model=TallerRead)
async def actualizar_taller(taller_id: int, body: TallerUpdate,
    db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return await service.update_taller(taller_id, body.model_dump(exclude_none=True), db, current_user.id)

# ── Especialidades ────────────────────────────────────────────
especialidades_router = APIRouter(prefix="/especialidades", tags=["Especialidades"])

@especialidades_router.get("/", response_model=list[EspecialidadRead])
async def listar_especialidades(db: AsyncSession = Depends(get_db)):
    return await service.get_especialidades(db)

@especialidades_router.post("/", response_model=EspecialidadRead, status_code=201)
async def crear_especialidad(body: EspecialidadCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    return await service.create_especialidad(body.nombre, body.descripcion, db)

# ── Técnicos ─────────────────────────────────────────────────
tecnicos_router = APIRouter(prefix="/tecnicos", tags=["Técnicos"])

@tecnicos_router.get("/", response_model=list[TecnicoRead])
async def listar_tecnicos(taller_id: Optional[int] = Query(None), db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    return await service.get_tecnicos(db, taller_id)

@tecnicos_router.post("/", response_model=TecnicoRead, status_code=201)
async def crear_tecnico(body: TecnicoCreate, db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)):
    return await service.create_tecnico(body.model_dump(), db, current_user.id)

@tecnicos_router.put("/{tecnico_id}", response_model=TecnicoRead)
async def actualizar_tecnico(tecnico_id: int, body: TecnicoUpdate,
    db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return await service.update_tecnico(tecnico_id, body.model_dump(exclude_none=True), db, current_user.id)
