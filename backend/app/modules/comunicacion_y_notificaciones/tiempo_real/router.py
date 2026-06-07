# WebSocket — suscripción a eventos de una solicitud de emergencia.
from __future__ import annotations

import logging

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.database import AsyncSessionLocal

from .auth_ws import assert_ws_access_to_solicitud, authenticate_ws_token
from .bus import realtime_bus

_log = logging.getLogger(__name__)

router = APIRouter(tags=["Tiempo real (WebSocket)"])


@router.websocket("/ws/solicitudes/{solicitud_id}")
async def ws_solicitud_tiempo_real(
    websocket: WebSocket,
    solicitud_id: int,
    token: str | None = Query(default=None),
) -> None:
    async with AsyncSessionLocal() as db:
        user = await authenticate_ws_token(token, db)
        await assert_ws_access_to_solicitud(user, solicitud_id, db)

    await websocket.accept()
    await realtime_bus.subscribe(solicitud_id, websocket)

    try:
        await websocket.send_json(
            {
                "tipo": "conectado",
                "solicitud_id": solicitud_id,
                "payload": {"usuario_id": user.id},
            }
        )
        while True:
            raw = await websocket.receive_text()
            if raw.strip().lower() in ("ping", '{"tipo":"ping"}'):
                await websocket.send_json({"tipo": "pong", "solicitud_id": solicitud_id, "payload": {}})
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        _log.debug("WS solicitud=%s closed: %s", solicitud_id, exc)
    finally:
        await realtime_bus.unsubscribe(solicitud_id, websocket)
