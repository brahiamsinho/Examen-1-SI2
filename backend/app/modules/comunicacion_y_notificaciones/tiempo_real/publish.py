# Encola eventos en la sesión SQLAlchemy y los publica tras commit exitoso.
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.timeutil import utc_now_naive

from .bus import realtime_bus
from .schemas import RealtimeEventEnvelope, RealtimeEventType

_log = logging.getLogger(__name__)

_QUEUE_KEY = "_realtime_ws_events"


def queue_solicitud_event(
    session: AsyncSession,
    *,
    solicitud_id: int,
    tipo: RealtimeEventType,
    payload: dict[str, Any] | None = None,
    occurred_at: datetime | None = None,
) -> None:
    sync = session.sync_session
    q: list[RealtimeEventEnvelope] = sync.info.setdefault(_QUEUE_KEY, [])
    q.append(
        RealtimeEventEnvelope(
            tipo=tipo,
            solicitud_id=solicitud_id,
            payload=payload or {},
            occurred_at=occurred_at or utc_now_naive(),
        )
    )


def _dispatch_events(session: Session) -> None:
    events: list[RealtimeEventEnvelope] = session.info.pop(_QUEUE_KEY, [])
    if not events:
        return
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        _log.warning("No event loop for realtime publish; dropping %d events", len(events))
        return
    for ev in events:
        loop.create_task(realtime_bus.publish(ev))


@event.listens_for(Session, "after_commit")
def _realtime_after_commit(session: Session) -> None:
    _dispatch_events(session)


@event.listens_for(Session, "after_rollback")
def _realtime_after_rollback(session: Session) -> None:
    session.info.pop(_QUEUE_KEY, None)
