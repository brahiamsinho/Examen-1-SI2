"""Módulo tiempo real — cola de eventos tras commit."""
from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from app.modules.comunicacion_y_notificaciones.tiempo_real.publish import (
    _QUEUE_KEY,
    queue_solicitud_event,
)
from app.modules.comunicacion_y_notificaciones.tiempo_real.schemas import (
    RealtimeEventEnvelope,
    RealtimeEventType,
)


class TestTiempoRealPublish(unittest.TestCase):
    def test_queue_event_en_session_sync(self) -> None:
        sync = MagicMock()
        sync.info = {}
        session = MagicMock()
        session.sync_session = sync

        queue_solicitud_event(
            session,
            solicitud_id=99,
            tipo=RealtimeEventType.PAGO_CONFIRMADO,
            payload={"pago_id": 1},
        )
        queue_solicitud_event(
            session,
            solicitud_id=99,
            tipo=RealtimeEventType.TALLER_SELECCIONADO,
            payload={"taller_id": 3},
        )

        queued: list[RealtimeEventEnvelope] = sync.info[_QUEUE_KEY]
        self.assertEqual(len(queued), 2)
        self.assertEqual(queued[0].tipo, RealtimeEventType.PAGO_CONFIRMADO)
        self.assertEqual(queued[1].tipo, RealtimeEventType.TALLER_SELECCIONADO)
        self.assertEqual(queued[0].solicitud_id, 99)

    def test_envelope_to_ws_json(self) -> None:
        from app.core.timeutil import utc_now_naive

        ev = RealtimeEventEnvelope(
            tipo=RealtimeEventType.ESTADO_INCIDENTE,
            solicitud_id=7,
            payload={"estado_nuevo": "EN_CAMINO"},
            occurred_at=utc_now_naive(),
        )
        data = ev.to_ws_json()
        self.assertEqual(data["tipo"], "estado_incidente")
        self.assertEqual(data["solicitud_id"], 7)
        self.assertIn("occurred_at", data)


if __name__ == "__main__":
    unittest.main()
