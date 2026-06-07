"""API admin — backups de plataforma (superadmin)."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import bind_auth_context, require_platform_superadmin, require_permission
from app.core.tenant import AuthContext
from app.modules.acceso_y_administracion.backup import service
from app.modules.acceso_y_administracion.backup.models import BackupRegistro, EstadoBackupEnum
from app.modules.acceso_y_administracion.backup.schemas import (
    BackupConfigRead,
    BackupConfigUpdate,
    BackupCreateIn,
    BackupRead,
    BackupRestoreIn,
)
from app.modules.acceso_y_administracion.tenants.models import Tenant

router = APIRouter(prefix="/admin/backups", tags=["Admin - Backups"])


async def _to_read(db: AsyncSession, row: BackupRegistro) -> BackupRead:
    data = BackupRead.model_validate(row)
    if row.tenant_id:
        tr = await db.execute(select(Tenant).where(Tenant.id == row.tenant_id))
        t = tr.scalar_one_or_none()
        if t:
            data = data.model_copy(update={"tenant_slug": t.slug, "tenant_nombre": t.nombre})
    return data


@router.get("/", response_model=list[BackupRead], dependencies=[Depends(require_permission("backup:gestionar"))])
async def listar_backups(
    tenant_id: Optional[int] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    ctx: AuthContext = Depends(bind_auth_context),
    _admin: AuthContext = Depends(require_platform_superadmin),
    db: AsyncSession = Depends(get_db),
):
    rows = await service.list_backups(db, tenant_id=tenant_id, limit=limit, offset=offset)
    return [await _to_read(db, r) for r in rows]


@router.post(
    "/",
    response_model=BackupRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("backup:gestionar"))],
)
async def crear_backup(
    body: BackupCreateIn,
    ctx: AuthContext = Depends(bind_auth_context),
    _admin: AuthContext = Depends(require_platform_superadmin),
    db: AsyncSession = Depends(get_db),
):
    reg = await service.create_backup(
        db,
        tipo=body.tipo,
        tenant_id=body.tenant_id,
        incluir_evidencias=body.incluir_evidencias,
        usuario_id=ctx.user.id,
    )
    return await _to_read(db, reg)


@router.get("/config", response_model=BackupConfigRead, dependencies=[Depends(require_permission("backup:gestionar"))])
async def obtener_config(
    _admin: AuthContext = Depends(require_platform_superadmin),
    db: AsyncSession = Depends(get_db),
):
    cfg = await service.get_or_create_config(db)
    return BackupConfigRead.model_validate(cfg)


@router.patch("/config", response_model=BackupConfigRead, dependencies=[Depends(require_permission("backup:gestionar"))])
async def actualizar_config(
    body: BackupConfigUpdate,
    ctx: AuthContext = Depends(bind_auth_context),
    _admin: AuthContext = Depends(require_platform_superadmin),
    db: AsyncSession = Depends(get_db),
):
    cfg = await service.get_or_create_config(db)
    data = body.model_dump(exclude_none=True)
    if "frecuencia" in data and hasattr(data["frecuencia"], "value"):
        data["frecuencia"] = data["frecuencia"].value
    for k, v in data.items():
        setattr(cfg, k, v)
    from app.core.timeutil import utc_now_naive

    cfg.actualizado_en = utc_now_naive()
    return BackupConfigRead.model_validate(cfg)


@router.get("/{backup_id}", response_model=BackupRead, dependencies=[Depends(require_permission("backup:gestionar"))])
async def detalle_backup(
    backup_id: int,
    _admin: AuthContext = Depends(require_platform_superadmin),
    db: AsyncSession = Depends(get_db),
):
    reg = await service.get_backup(db, backup_id)
    return await _to_read(db, reg)


@router.get("/{backup_id}/download", dependencies=[Depends(require_permission("backup:gestionar"))])
async def descargar_backup(
    backup_id: int,
    _admin: AuthContext = Depends(require_platform_superadmin),
    db: AsyncSession = Depends(get_db),
):
    reg = await service.get_backup(db, backup_id)
    if reg.estado not in (EstadoBackupEnum.COMPLETADO, EstadoBackupEnum.RESTAURADO):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Backup no disponible para descarga.")
    content, filename, media = service.read_backup_bytes(reg.archivo)
    return Response(
        content=content,
        media_type=media,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/{backup_id}/restore", response_model=BackupRead, dependencies=[Depends(require_permission("backup:gestionar"))])
async def restaurar_backup(
    backup_id: int,
    body: BackupRestoreIn,
    ctx: AuthContext = Depends(bind_auth_context),
    _admin: AuthContext = Depends(require_platform_superadmin),
    db: AsyncSession = Depends(get_db),
):
    if not body.confirmar:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Debe confirmar la restauración.")
    reg = await service.restore_backup(
        db,
        backup_id,
        usuario_id=ctx.user.id,
        motivo=body.motivo.strip(),
    )
    return await _to_read(db, reg)


@router.delete("/{backup_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("backup:gestionar"))])
async def eliminar_backup(
    backup_id: int,
    ctx: AuthContext = Depends(bind_auth_context),
    _admin: AuthContext = Depends(require_platform_superadmin),
    db: AsyncSession = Depends(get_db),
):
    await service.delete_backup(db, backup_id, usuario_id=ctx.user.id)
