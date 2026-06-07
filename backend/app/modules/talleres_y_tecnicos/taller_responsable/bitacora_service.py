"""Consulta de bitácora acotada al taller: mismo tenant, solo equipo del taller y módulos operativos."""
from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.acceso_y_administracion.bitacora.models import AccionBitacoraEnum, Bitacora
from app.modules.acceso_y_administracion.usuarios.models import Usuario
from app.modules.talleres_y_tecnicos.taller_responsable.schemas import TallerBitacoraRead
from app.modules.talleres_y_tecnicos.talleres.models import Taller, Tecnico

# Módulos visibles en el portal taller (excluye emergencias de clientes, pagos, vehículos, etc.).
TALLER_BITACORA_MODULOS: frozenset[str] = frozenset(
    {
        "auth",
        "talleres",
        "taller_responsable",
        "taller_emergencias",
        "tecnico",
        "taller_portal",
        "usuarios",
    }
)


def _usuario_display(nombres: str | None, apellidos: str | None, email: str | None) -> str:
    parts = [p.strip() for p in (nombres, apellidos) if p and p.strip()]
    if parts:
        return " ".join(parts)
    if email:
        return email.split("@", 1)[0]
    return "Usuario"


async def _actor_usuario_ids(db: AsyncSession, taller: Taller) -> set[int]:
    ids = {taller.usuario_responsable_id}
    r = await db.execute(select(Tecnico.usuario_id).where(Tecnico.taller_id == taller.id))
    ids.update(row[0] for row in r.fetchall())
    return ids


async def listar_bitacora_taller(
    db: AsyncSession,
    user: Usuario,
    taller: Taller,
    *,
    usuario_id: int | None = None,
    modulo: str | None = None,
    accion: AccionBitacoraEnum | None = None,
    desde: datetime | None = None,
    hasta: datetime | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[TallerBitacoraRead]:
    if user.tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta no está asociada a una organización.",
        )

    actor_ids = await _actor_usuario_ids(db, taller)
    if usuario_id is not None:
        if usuario_id not in actor_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puedes filtrar por miembros de tu equipo de taller.",
            )

    modulos = TALLER_BITACORA_MODULOS
    if modulo:
        mod = modulo.strip()
        if mod not in modulos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Módulo no disponible en la bitácora del taller: {mod}",
            )
        modulos = frozenset({mod})

    tecnico_subq = select(Tecnico.usuario_id).where(Tecnico.taller_id == taller.id)

    stmt = (
        select(Bitacora, Usuario.nombres, Usuario.apellidos, Usuario.email)
        .join(Usuario, Bitacora.usuario_id == Usuario.id)
        .where(
            Usuario.tenant_id == user.tenant_id,
            Bitacora.modulo.in_(modulos),
            or_(
                Bitacora.usuario_id == taller.usuario_responsable_id,
                Bitacora.usuario_id.in_(tecnico_subq),
            ),
        )
        .order_by(Bitacora.created_at.desc())
        .limit(min(limit, 200))
        .offset(offset)
    )

    if usuario_id is not None:
        stmt = stmt.where(Bitacora.usuario_id == usuario_id)
    if accion is not None:
        stmt = stmt.where(Bitacora.accion == accion)
    if desde is not None:
        stmt = stmt.where(Bitacora.created_at >= desde)
    if hasta is not None:
        stmt = stmt.where(Bitacora.created_at <= hasta)

    rows = (await db.execute(stmt)).all()
    out: list[TallerBitacoraRead] = []
    for bit, nombres, apellidos, email in rows:
        out.append(
            TallerBitacoraRead(
                id=bit.id,
                usuario_id=bit.usuario_id,
                usuario_nombre=_usuario_display(nombres, apellidos, email),
                modulo=bit.modulo,
                entidad=bit.entidad,
                entidad_id=bit.entidad_id,
                accion=bit.accion,
                descripcion=bit.descripcion,
                created_at=bit.created_at,
            )
        )
    return out
