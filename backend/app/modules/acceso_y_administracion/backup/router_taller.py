"""API portal taller — backups del taller (responsable)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_permission
from app.core.timeutil import utc_now_naive
from app.modules.acceso_y_administracion.backup import service
from app.modules.acceso_y_administracion.backup.models import EstadoBackupEnum, TipoBackupEnum
from app.modules.acceso_y_administracion.backup.schemas import (
    BackupRead,
    BackupRestoreIn,
    TallerBackupConfigRead,
    TallerBackupConfigUpdate,
)
from app.modules.acceso_y_administracion.usuarios.models import Usuario
from app.modules.talleres_y_tecnicos.talleres.models import Taller
from app.modules.talleres_y_tecnicos.taller_responsable.router import require_taller_responsable

router = APIRouter(prefix="/app/taller/backups", tags=["App taller - Backups"])


async def _to_read(db: AsyncSession, row) -> BackupRead:
    data = BackupRead.model_validate(row)
    return data


@router.get(
    "/",
    response_model=list[BackupRead],
    dependencies=[Depends(require_permission("backup_taller:gestionar"))],
)
async def listar_backups_taller(
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    _, taller = ctx
    rows = await service.list_backups(db, taller_id=taller.id, limit=limit, offset=offset)
    return [await _to_read(db, r) for r in rows]


@router.post(
    "/",
    response_model=BackupRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("backup_taller:gestionar"))],
)
async def crear_backup_taller(
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    user, taller = ctx
    reg = await service.create_backup(
        db,
        tipo=TipoBackupEnum.TALLER,
        taller_id=taller.id,
        usuario_id=user.id,
    )
    return await _to_read(db, reg)


@router.get(
    "/config",
    response_model=TallerBackupConfigRead,
    dependencies=[Depends(require_permission("backup_taller:gestionar"))],
)
async def obtener_config_taller(
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    _, taller = ctx
    cfg = await service.get_or_create_taller_config(db, taller.id)
    return TallerBackupConfigRead.model_validate(cfg)


@router.patch(
    "/config",
    response_model=TallerBackupConfigRead,
    dependencies=[Depends(require_permission("backup_taller:gestionar"))],
)
async def actualizar_config_taller(
    body: TallerBackupConfigUpdate,
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    _, taller = ctx
    cfg = await service.get_or_create_taller_config(db, taller.id)
    data = body.model_dump(exclude_none=True)
    if "frecuencia" in data and hasattr(data["frecuencia"], "value"):
        data["frecuencia"] = data["frecuencia"].value
    for k, v in data.items():
        setattr(cfg, k, v)
    cfg.actualizado_en = utc_now_naive()
    return TallerBackupConfigRead.model_validate(cfg)


@router.get(
    "/{backup_id}/download",
    dependencies=[Depends(require_permission("backup_taller:gestionar"))],
)
async def descargar_backup_taller(
    backup_id: int,
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    _, taller = ctx
    reg = await service.get_backup_for_taller(db, backup_id, taller.id)
    if reg.estado not in (EstadoBackupEnum.COMPLETADO, EstadoBackupEnum.RESTAURADO):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Backup no disponible para descarga.")
    content, filename, media = service.read_backup_bytes(reg.archivo)
    return Response(
        content=content,
        media_type=media,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post(
    "/{backup_id}/restore",
    response_model=BackupRead,
    dependencies=[Depends(require_permission("backup_taller:gestionar"))],
)
async def restaurar_backup_taller(
    backup_id: int,
    body: BackupRestoreIn,
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    if not body.confirmar:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Debe confirmar la restauración.")
    user, taller = ctx
    await service.get_backup_for_taller(db, backup_id, taller.id)
    reg = await service.restore_backup(
        db,
        backup_id,
        usuario_id=user.id,
        motivo=body.motivo.strip(),
        taller_id=taller.id,
        tenant_id=taller.tenant_id,
    )
    return await _to_read(db, reg)


@router.delete(
    "/{backup_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("backup_taller:gestionar"))],
)
async def eliminar_backup_taller(
    backup_id: int,
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    user, taller = ctx
    await service.get_backup_for_taller(db, backup_id, taller.id)
    await service.delete_backup(db, backup_id, usuario_id=user.id)
