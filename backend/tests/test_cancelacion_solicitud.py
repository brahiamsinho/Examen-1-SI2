"""Cancelación de solicitud por el cliente — reglas de negocio."""
from __future__ import annotations

import unittest

from app.modules.incidentes.emergencias.models import EstadoSolicitudSeguimientoEnum
from app.modules.incidentes.emergencias.schemas import CancelarSolicitudIn
from app.modules.incidentes.emergencias.service.helpers import (
    ESTADOS_LIBERAN_CUPO_TALLER,
    cliente_puede_cancelar,
)


class TestCancelacionHelpers(unittest.TestCase):
    def test_cliente_puede_cancelar_estados_abiertos(self) -> None:
        for est in (
            EstadoSolicitudSeguimientoEnum.REGISTRADA,
            EstadoSolicitudSeguimientoEnum.EN_REVISION,
            EstadoSolicitudSeguimientoEnum.TALLER_ASIGNADO,
            EstadoSolicitudSeguimientoEnum.TECNICO_ASIGNADO,
            EstadoSolicitudSeguimientoEnum.EN_CAMINO,
        ):
            self.assertTrue(cliente_puede_cancelar(est))

    def test_cliente_no_puede_cancelar_cerrados(self) -> None:
        for est in (
            EstadoSolicitudSeguimientoEnum.EN_ATENCION,
            EstadoSolicitudSeguimientoEnum.FINALIZADA,
            EstadoSolicitudSeguimientoEnum.CANCELADA,
        ):
            self.assertFalse(cliente_puede_cancelar(est))

    def test_liberan_cupo_taller(self) -> None:
        self.assertIn(EstadoSolicitudSeguimientoEnum.TALLER_ASIGNADO, ESTADOS_LIBERAN_CUPO_TALLER)
        self.assertNotIn(EstadoSolicitudSeguimientoEnum.REGISTRADA, ESTADOS_LIBERAN_CUPO_TALLER)


class TestCancelarSolicitudSchema(unittest.TestCase):
    def test_motivo_opcional(self) -> None:
        m = CancelarSolicitudIn()
        self.assertIsNone(m.motivo)

    def test_motivo_strip(self) -> None:
        m = CancelarSolicitudIn(motivo="  ya no necesito  ")
        self.assertEqual(m.motivo, "ya no necesito")


if __name__ == "__main__":
    unittest.main()
