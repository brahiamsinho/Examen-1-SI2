# Horarios de atención por taller (zona America/La_Paz).
from __future__ import annotations

from datetime import datetime, time
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.timeutil import utc_now_naive
from app.modules.talleres_y_tecnicos.talleres.horarios_schemas import (
    NOMBRES_DIA,
    TallerHorarioDiaRead,
    TallerHorariosRead,
    TallerHorariosUpdateIn,
)
from app.modules.talleres_y_tecnicos.talleres.models import TallerHorario

TZ_BOLIVIA = ZoneInfo("America/La_Paz")

DEFAULT_APERTURA = time(8, 0)
DEFAULT_CIERRE = time(18, 0)
DOMINGO_CERRADO = time(0, 0)


async def _list_horarios_rows(db: AsyncSession, taller_id: int) -> list[TallerHorario]:
    r = await db.execute(
        select(TallerHorario)
        .where(TallerHorario.taller_id == taller_id)
        .order_by(TallerHorario.dia_semana)
    )
    return list(r.scalars().all())


async def ensure_default_horarios(db: AsyncSession, taller_id: int) -> list[TallerHorario]:
    """Crea Lun–Sáb 08:00–18:00 y Dom cerrado si aún no hay filas."""
    existing = await _list_horarios_rows(db, taller_id)
    if existing:
        return existing

    now = utc_now_naive()
    rows: list[TallerHorario] = []
    for dia in range(7):
        activo = dia < 6
        rows.append(
            TallerHorario(
                taller_id=taller_id,
                dia_semana=dia,
                hora_apertura=DEFAULT_APERTURA if activo else DOMINGO_CERRADO,
                hora_cierre=DEFAULT_CIERRE if activo else time(1, 0),
                activo=activo,
                created_at=now,
                updated_at=now,
            )
        )
    db.add_all(rows)
    await db.flush()
    return rows


def _now_bolivia(now: datetime | None = None) -> datetime:
    if now is None:
        return datetime.now(TZ_BOLIVIA)
    if now.tzinfo is None:
        return now.replace(tzinfo=ZoneInfo("UTC")).astimezone(TZ_BOLIVIA)
    return now.astimezone(TZ_BOLIVIA)


def _is_row_abierto(row: TallerHorario, momento: datetime) -> bool:
    if not row.activo:
        return False
    if momento.weekday() != row.dia_semana:
        return False
    hora = momento.time().replace(tzinfo=None)
    return row.hora_apertura <= hora < row.hora_cierre


async def is_taller_abierto_ahora(
    db: AsyncSession,
    taller_id: int,
    *,
    now: datetime | None = None,
) -> bool:
    rows = await ensure_default_horarios(db, taller_id)
    momento = _now_bolivia(now)
    for row in rows:
        if row.dia_semana == momento.weekday():
            return _is_row_abierto(row, momento)
    return False


async def abierto_map_for_talleres(
    db: AsyncSession,
    taller_ids: list[int],
) -> dict[int, bool]:
    if not taller_ids:
        return {}
    momento = _now_bolivia()
    dia = momento.weekday()
    r = await db.execute(
        select(TallerHorario).where(
            TallerHorario.taller_id.in_(taller_ids),
            TallerHorario.dia_semana == dia,
        )
    )
    rows = {row.taller_id: row for row in r.scalars().all()}
    out: dict[int, bool] = {}
    for tid in taller_ids:
        row = rows.get(tid)
        if row is None:
            await ensure_default_horarios(db, tid)
            out[tid] = await is_taller_abierto_ahora(db, tid, now=momento)
        else:
            out[tid] = _is_row_abierto(row, momento)
    return out


def _to_read(rows: list[TallerHorario], abierto: bool) -> TallerHorariosRead:
    by_day = {row.dia_semana: row for row in rows}
    horarios: list[TallerHorarioDiaRead] = []
    for dia in range(7):
        row = by_day.get(dia)
        if row is None:
            horarios.append(
                TallerHorarioDiaRead(
                    dia_semana=dia,
                    nombre_dia=NOMBRES_DIA[dia],
                    hora_apertura=None,
                    hora_cierre=None,
                    activo=False,
                )
            )
            continue
        horarios.append(
            TallerHorarioDiaRead(
                dia_semana=dia,
                nombre_dia=NOMBRES_DIA[dia],
                hora_apertura=row.hora_apertura if row.activo else None,
                hora_cierre=row.hora_cierre if row.activo else None,
                activo=row.activo,
            )
        )
    return TallerHorariosRead(horarios=horarios, abierto_ahora=abierto)


async def obtener_horarios(db: AsyncSession, taller_id: int) -> TallerHorariosRead:
    rows = await ensure_default_horarios(db, taller_id)
    abierto = await is_taller_abierto_ahora(db, taller_id)
    return _to_read(rows, abierto)


async def actualizar_horarios(
    db: AsyncSession,
    taller_id: int,
    body: TallerHorariosUpdateIn,
) -> TallerHorariosRead:
    rows = await ensure_default_horarios(db, taller_id)
    by_day = {row.dia_semana: row for row in rows}
    now = utc_now_naive()

    for item in body.horarios:
        row = by_day.get(item.dia_semana)
        if row is None:
            row = TallerHorario(
                taller_id=taller_id,
                dia_semana=item.dia_semana,
                created_at=now,
            )
            db.add(row)
            by_day[item.dia_semana] = row

        row.activo = item.activo
        if item.activo:
            assert item.hora_apertura is not None and item.hora_cierre is not None
            row.hora_apertura = item.hora_apertura
            row.hora_cierre = item.hora_cierre
        else:
            row.hora_apertura = DOMINGO_CERRADO
            row.hora_cierre = time(1, 0)
        row.updated_at = now

    await db.flush()
    abierto = await is_taller_abierto_ahora(db, taller_id)
    return _to_read(list(by_day.values()), abierto)


async def assert_taller_abierto(
    db: AsyncSession,
    taller_id: int,
    *,
    accion: str = "operar",
) -> None:
    if await is_taller_abierto_ahora(db, taller_id):
        return
    horarios = await obtener_horarios(db, taller_id)
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"El taller está fuera de horario de atención y no puede {accion} en este momento.",
    )
