# Lógica — notificaciones in-app + FCM + mensajes por solicitud (CU19, CU21).
from __future__ import annotations

import asyncio
import logging
from typing import Literal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.timeutil import utc_now_naive
from app.modules.comunicaciones import fcm_client, repository
from app.modules.comunicaciones.models import TipoNotificacionEnum
from app.modules.comunicaciones.schemas import (
    FcmTokenRegisterIn,
    MensajeSolicitudCreateIn,
    MensajeSolicitudRead,
    NotificacionRead,
)
from app.modules.emergencias.models import SolicitudEmergencia
from app.modules.portal_cliente.service import get_cliente_row_for_usuario, require_cliente_rol
from app.modules.portal_tecnico.service import get_tecnico_row_for_usuario, require_tecnico_rol
from app.modules.usuarios.models import Usuario

_log = logging.getLogger(__name__)


async def _notificar_push(
    db: AsyncSession,
    *,
    usuario_destino_id: int,
    titulo: str,
    cuerpo: str,
    data: dict[str, str],
) -> None:
    if not settings.FCM_ENABLED:
        return
    tokens = await repository.list_fcm_tokens_usuario(db, usuario_id=usuario_destino_id)
    if not tokens:
        return
    try:
        await asyncio.to_thread(
            fcm_client.send_push_multicast_sync,
            tokens,
            title=titulo,
            body=cuerpo,
            data=data,
        )
    except Exception:
        _log.exception("Error en hilo FCM")


async def crear_notificacion_y_push(
    db: AsyncSession,
    *,
    usuario_destino_id: int,
    solicitud_id: int | None,
    tipo: TipoNotificacionEnum,
    titulo: str,
    mensaje: str,
) -> NotificacionRead:
    now = utc_now_naive()
    row = await repository.insert_notificacion(
        db,
        usuario_id=usuario_destino_id,
        solicitud_id=solicitud_id,
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
        created_at=now,
    )
    data = {
        "tipo": tipo.value,
        "notificacion_id": str(row.id),
        **({"solicitud_id": str(solicitud_id)} if solicitud_id is not None else {}),
    }
    await _notificar_push(db, usuario_destino_id=usuario_destino_id, titulo=titulo, cuerpo=mensaje, data=data)
    return NotificacionRead.model_validate(row)


async def registrar_fcm_token(user: Usuario, body: FcmTokenRegisterIn, db: AsyncSession) -> dict[str, str]:
    now = utc_now_naive()
    await repository.upsert_fcm_token(
        db,
        usuario_id=user.id,
        token=body.token.strip(),
        platform=body.platform.strip() if body.platform else None,
        now=now,
    )
    await db.commit()
    return {"status": "ok"}


async def eliminar_fcm_token(user: Usuario, body: FcmTokenRegisterIn, db: AsyncSession) -> dict[str, str]:
    n = await repository.delete_fcm_token(db, usuario_id=user.id, token=body.token.strip())
    await db.commit()
    return {"status": "ok", "eliminados": str(n)}


async def listar_notificaciones(
    user: Usuario, db: AsyncSession, *, solo_no_leidas: bool, limit: int
) -> list[NotificacionRead]:
    rows = await repository.list_notificaciones_usuario(
        db, usuario_id=user.id, solo_no_leidas=solo_no_leidas, limit=limit
    )
    return [NotificacionRead.model_validate(x) for x in rows]


async def marcar_notificacion_leida(user: Usuario, notif_id: int, db: AsyncSession) -> NotificacionRead:
    n = await repository.get_notificacion_propia(db, notif_id=notif_id, usuario_id=user.id)
    if n is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notificación no encontrada")
    await repository.marcar_notificacion_leida(db, n=n, leida_at=utc_now_naive())
    await db.commit()
    await db.refresh(n)
    return NotificacionRead.model_validate(n)


async def _get_solicitud_or_404(db: AsyncSession, solicitud_id: int) -> SolicitudEmergencia:
    sol = await repository.get_solicitud_by_id(db, solicitud_id)
    if sol is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")
    return sol


async def _assert_cliente_solicitud_propia(db: AsyncSession, user: Usuario, sol: SolicitudEmergencia) -> None:
    await require_cliente_rol(user.id, db)
    c = await get_cliente_row_for_usuario(user.id, db)
    if sol.cliente_id != c.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")


async def _assert_tecnico_asignado(db: AsyncSession, user: Usuario, sol: SolicitudEmergencia) -> None:
    await require_tecnico_rol(user.id, db)
    t = await get_tecnico_row_for_usuario(user.id, db)
    if sol.tecnico_id is None or sol.tecnico_id != t.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No estás asignado a esta solicitud.",
        )


async def listar_mensajes(
    user: Usuario,
    solicitud_id: int,
    db: AsyncSession,
    actor: Literal["cliente", "tecnico"],
) -> list[MensajeSolicitudRead]:
    sol = await _get_solicitud_or_404(db, solicitud_id)
    if actor == "cliente":
        await _assert_cliente_solicitud_propia(db, user, sol)
    else:
        await _assert_tecnico_asignado(db, user, sol)
    rows = await repository.list_mensajes_solicitud(db, solicitud_id=solicitud_id)
    return [MensajeSolicitudRead.model_validate(x) for x in rows]


async def enviar_mensaje(
    user: Usuario,
    solicitud_id: int,
    body: MensajeSolicitudCreateIn,
    db: AsyncSession,
    actor: Literal["cliente", "tecnico"],
) -> MensajeSolicitudRead:
    sol = await _get_solicitud_or_404(db, solicitud_id)
    texto = body.mensaje.strip()
    now = utc_now_naive()

    if actor == "cliente":
        await _assert_cliente_solicitud_propia(db, user, sol)
        if sol.tecnico_id is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Aún no hay técnico asignado; no se puede enviar mensaje.",
            )
        tu = await repository.get_tecnico_usuario_id_for_solicitud(db, tecnico_row_id=sol.tecnico_id)
        if tu is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Técnico inválido.")
        cu = await repository.get_cliente_usuario_id(db, cliente_id=sol.cliente_id)
        if cu is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Cliente inválido.")
        if user.id != cu:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el cliente titular puede escribir.")
        emisor, receptor = user.id, tu
    else:
        await _assert_tecnico_asignado(db, user, sol)
        cu = await repository.get_cliente_usuario_id(db, cliente_id=sol.cliente_id)
        if cu is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Cliente inválido.")
        emisor, receptor = user.id, cu

    msg = await repository.insert_mensaje(
        db,
        solicitud_id=solicitud_id,
        emisor_usuario_id=emisor,
        receptor_usuario_id=receptor,
        texto=texto,
        created_at=now,
    )
    await db.flush()

    await crear_notificacion_y_push(
        db,
        usuario_destino_id=receptor,
        solicitud_id=solicitud_id,
        tipo=TipoNotificacionEnum.MENSAJE_NUEVO,
        titulo="Nuevo mensaje",
        mensaje=texto[:120] + ("…" if len(texto) > 120 else ""),
    )
    await db.commit()
    await db.refresh(msg)
    return MensajeSolicitudRead.model_validate(msg)
