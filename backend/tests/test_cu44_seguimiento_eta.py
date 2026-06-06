"""CU44 — lógica de ETA y schema."""

from datetime import datetime, timezone

from app.modules.incidentes.emergencias.models import EstadoSolicitudSeguimientoEnum
from app.modules.incidentes.emergencias.schemas import EtaDisponibilidadEnum, SolicitudEtaRead
from app.modules.incidentes.emergencias.service.seguimiento_eta import _build_eta_read


def test_build_eta_pendiente_sin_taller():
    class S:
        id = 1
        estado = EstadoSolicitudSeguimientoEnum.REGISTRADA
        tiempo_estimado_min = None
        updated_at = datetime(2026, 6, 5, 12, 0, tzinfo=timezone.utc)
        taller_id = None
        tecnico_id = None

    out = _build_eta_read(S())
    assert out.disponibilidad == EtaDisponibilidadEnum.NO_APLICABLE
    assert out.tiempo_estimado_min is None
    assert out.eta_aplicable is False


def test_build_eta_disponible_en_camino():
    class S:
        id = 2
        estado = EstadoSolicitudSeguimientoEnum.EN_CAMINO
        tiempo_estimado_min = 25
        updated_at = datetime(2026, 6, 5, 12, 0, tzinfo=timezone.utc)
        taller_id = 3
        tecnico_id = 7

    out = _build_eta_read(S())
    assert out.disponibilidad == EtaDisponibilidadEnum.DISPONIBLE
    assert out.tiempo_estimado_min == 25
    assert "25 min" in out.mensaje


def test_build_eta_historico_finalizada():
    class S:
        id = 3
        estado = EstadoSolicitudSeguimientoEnum.FINALIZADA
        tiempo_estimado_min = 40
        updated_at = datetime(2026, 6, 5, 12, 0, tzinfo=timezone.utc)
        taller_id = 1
        tecnico_id = 2

    out = _build_eta_read(S())
    assert out.disponibilidad == EtaDisponibilidadEnum.HISTORICO
    assert out.eta_aplicable is False
