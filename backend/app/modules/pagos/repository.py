from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.emergencias.models import SolicitudEmergencia
from app.modules.pagos.models import EstadoPagoEnum, Pago


async def get_solicitud_cliente(
    db: AsyncSession, *, solicitud_id: int, cliente_id: int
) -> SolicitudEmergencia | None:
    r = await db.execute(
        select(SolicitudEmergencia).where(
            SolicitudEmergencia.id == solicitud_id,
            SolicitudEmergencia.cliente_id == cliente_id,
        )
    )
    return r.scalar_one_or_none()


async def count_pagos_pagados_solicitud(db: AsyncSession, *, solicitud_id: int) -> int:
    r = await db.execute(
        select(func.count())
        .select_from(Pago)
        .where(Pago.solicitud_id == solicitud_id, Pago.estado == EstadoPagoEnum.PAGADO)
    )
    return int(r.scalar_one())


async def list_pagos_solicitud(db: AsyncSession, *, solicitud_id: int, cliente_id: int) -> list[Pago]:
    r = await db.execute(
        select(Pago)
        .where(Pago.solicitud_id == solicitud_id, Pago.cliente_id == cliente_id)
        .order_by(Pago.created_at.desc())
    )
    return list(r.scalars().all())


async def get_pago_solicitud_cliente(
    db: AsyncSession, *, pago_id: int, solicitud_id: int, cliente_id: int
) -> Pago | None:
    r = await db.execute(
        select(Pago).where(
            Pago.id == pago_id,
            Pago.solicitud_id == solicitud_id,
            Pago.cliente_id == cliente_id,
        )
    )
    return r.scalar_one_or_none()


async def insert_pago(
    db: AsyncSession,
    *,
    solicitud_id: int,
    cliente_id: int,
    monto,
    moneda: str,
    metodo,
    estado,
    proveedor: str,
    created_at,
) -> Pago:
    row = Pago(
        solicitud_id=solicitud_id,
        cliente_id=cliente_id,
        monto=monto,
        moneda=moneda,
        metodo=metodo,
        estado=estado,
        proveedor=proveedor,
        created_at=created_at,
    )
    db.add(row)
    await db.flush()
    return row


async def refresh_pago(db: AsyncSession, pago: Pago) -> None:
    await db.refresh(pago)
