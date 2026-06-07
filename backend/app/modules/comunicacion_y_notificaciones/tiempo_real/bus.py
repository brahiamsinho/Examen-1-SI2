# Bus en memoria: suscriptores WebSocket por solicitud_id.
from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import Any

from fastapi import WebSocket

from .schemas import RealtimeEventEnvelope

_log = logging.getLogger(__name__)


class RealtimeBus:
    def __init__(self) -> None:
        self._rooms: dict[int, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def subscribe(self, solicitud_id: int, ws: WebSocket) -> None:
        async with self._lock:
            self._rooms[solicitud_id].add(ws)

    async def unsubscribe(self, solicitud_id: int, ws: WebSocket) -> None:
        async with self._lock:
            room = self._rooms.get(solicitud_id)
            if not room:
                return
            room.discard(ws)
            if not room:
                self._rooms.pop(solicitud_id, None)

    async def publish(self, event: RealtimeEventEnvelope) -> None:
        async with self._lock:
            subscribers = list(self._rooms.get(event.solicitud_id, ()))

        if not subscribers:
            return

        payload = event.to_ws_json()
        dead: list[tuple[int, WebSocket]] = []

        for ws in subscribers:
            try:
                await ws.send_json(payload)
            except Exception as exc:
                _log.debug("WS send failed solicitud=%s: %s", event.solicitud_id, exc)
                dead.append((event.solicitud_id, ws))

        for solicitud_id, ws in dead:
            await self.unsubscribe(solicitud_id, ws)

    def stats(self) -> dict[str, Any]:
        return {
            "rooms": len(self._rooms),
            "connections": sum(len(v) for v in self._rooms.values()),
        }


realtime_bus = RealtimeBus()
