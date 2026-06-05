"""CU43/CU45 — schema idempotencia client_request_id."""

from uuid import uuid4

from app.modules.incidentes.emergencias.schemas import SolicitudEmergenciaCreateIn


def test_create_in_acepta_client_request_id_opcional():
    body = SolicitudEmergenciaCreateIn(vehiculo_id=1)
    assert body.client_request_id is None


def test_create_in_con_client_request_id_uuid():
    cid = uuid4()
    body = SolicitudEmergenciaCreateIn(vehiculo_id=3, client_request_id=cid)
    assert body.client_request_id == cid
