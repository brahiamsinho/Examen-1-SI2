"""Schemas portal técnico emergencias (sin BD)."""
from __future__ import annotations

import unittest

from pydantic import ValidationError

from app.modules.emergencias.models import EstadoSolicitudSeguimientoEnum
from app.modules.portal_tecnico_emergencias.schemas import ActualizarEstadoServicioIn


class TestPortalTecnicoEmergenciasSchemas(unittest.TestCase):
    def test_observacion_max_length(self) -> None:
        with self.assertRaises(ValidationError):
            ActualizarEstadoServicioIn(
                nuevo_estado=EstadoSolicitudSeguimientoEnum.EN_CAMINO,
                observacion="x" * 2001,
            )


if __name__ == "__main__":
    unittest.main()
