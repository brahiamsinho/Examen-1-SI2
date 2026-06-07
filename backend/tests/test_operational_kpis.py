"""Schemas y helpers del módulo analytics (KPIs operacionales §3)."""
from __future__ import annotations

import unittest

from app.modules.analytics.operational_kpis import _round_minutes
from app.modules.analytics.schemas import (
    IncidentePorTipoFila,
    OperationalKpisRead,
    SlaCumplimientoRead,
)


class TestOperationalKpisSchemas(unittest.TestCase):
    def test_operational_kpis_read_defaults(self) -> None:
        kpi = OperationalKpisRead(
            sla=SlaCumplimientoRead(
                umbral_minutos=60,
                servicios_evaluados=0,
                servicios_dentro_sla=0,
                porcentaje_cumplimiento=None,
            )
        )
        self.assertIsNone(kpi.tiempo_promedio_asignacion_min)
        self.assertEqual(kpi.casos_cancelados, 0)
        self.assertEqual(kpi.incidentes_por_tipo, [])

    def test_operational_kpis_read_full(self) -> None:
        kpi = OperationalKpisRead(
            tiempo_promedio_asignacion_min=12.5,
            tiempo_promedio_llegada_min=28.3,
            incidentes_por_tipo=[
                IncidentePorTipoFila(categoria="BATERIA", label="Batería", total=3),
            ],
            casos_cancelados=2,
            casos_no_atendidos=1,
            sla=SlaCumplimientoRead(
                umbral_minutos=60,
                servicios_evaluados=10,
                servicios_dentro_sla=8,
                porcentaje_cumplimiento=80.0,
            ),
        )
        self.assertEqual(kpi.incidentes_por_tipo[0].label, "Batería")
        self.assertEqual(kpi.sla.porcentaje_cumplimiento, 80.0)

    def test_round_minutes(self) -> None:
        self.assertIsNone(_round_minutes(None))
        self.assertEqual(_round_minutes(12.345), 12.3)
        self.assertIsNone(_round_minutes("invalid"))


if __name__ == "__main__":
    unittest.main()
