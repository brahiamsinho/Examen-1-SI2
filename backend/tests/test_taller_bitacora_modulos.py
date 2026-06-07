"""Whitelist de módulos visibles en bitácora del portal taller."""

from app.modules.talleres_y_tecnicos.taller_responsable.bitacora_service import TALLER_BITACORA_MODULOS


def test_taller_bitacora_incluye_modulos_operativos():
    assert "taller_emergencias" in TALLER_BITACORA_MODULOS
    assert "taller_responsable" in TALLER_BITACORA_MODULOS
    assert "taller_portal" in TALLER_BITACORA_MODULOS


def test_taller_bitacora_excluye_modulos_cliente_y_global():
    assert "emergencias" not in TALLER_BITACORA_MODULOS
    assert "clientes" not in TALLER_BITACORA_MODULOS
    assert "vehiculos" not in TALLER_BITACORA_MODULOS
    assert "pagos" not in TALLER_BITACORA_MODULOS
