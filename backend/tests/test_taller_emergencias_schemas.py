"""Validaciones Pydantic del módulo taller_emergencias (sin BD)."""
from __future__ import annotations

import unittest

from pydantic import ValidationError

from app.modules.atencion.taller_emergencias.schemas import (
    AsignarTecnicoIn,
    RegistrarPresupuestoIn,
    RechazarBandejaIn,
    TallerDisponibilidadUpdateIn,
)


class TestTallerEmergenciasSchemas(unittest.TestCase):
    def test_rechazar_motivo_min_length(self) -> None:
        with self.assertRaises(ValidationError):
            RechazarBandejaIn(motivo_rechazo="ab")

    def test_rechazar_motivo_ok(self) -> None:
        m = RechazarBandejaIn(motivo_rechazo="No disponemos de grúa")
        self.assertEqual(m.motivo_rechazo, "No disponemos de grúa")

    def test_disponibilidad_capacidad_rango(self) -> None:
        with self.assertRaises(ValidationError):
            TallerDisponibilidadUpdateIn(capacidad_maxima_diaria=0)

    def test_asignar_tecnico_id_positivo(self) -> None:
        with self.assertRaises(ValidationError):
            AsignarTecnicoIn(tecnico_id=0)

    def test_registrar_presupuesto_ok(self) -> None:
        from decimal import Decimal

        p = RegistrarPresupuestoIn(
            presupuesto_bob=Decimal("450.50"),
            detalle="Cambio de batería y revisión eléctrica",
            observaciones="Incluye mano de obra",
        )
        self.assertEqual(p.presupuesto_bob, Decimal("450.50"))

    def test_registrar_presupuesto_detalle_corto(self) -> None:
        from decimal import Decimal

        with self.assertRaises(ValidationError):
            RegistrarPresupuestoIn(presupuesto_bob=Decimal("10"), detalle="ab")


if __name__ == "__main__":
    unittest.main()
