# Servicio cliente emergencias: solicitudes, ubicaciones, evidencias (mismo contrato público).
from .evidencias import agregar_evidencia, agregar_evidencia_archivo
from .seleccion_taller import listar_talleres_candidatos, seleccionar_taller
from .seguimiento_eta import obtener_eta_cliente
from .solicitudes import (
    actualizar_texto,
    crear_solicitud,
    listar_solicitudes,
    obtener_detalle,
    obtener_seguimiento,
    obtener_ubicacion_tecnico_compartida_cliente,
)
from .ubicaciones import agregar_ubicacion

__all__ = [
    "actualizar_texto",
    "agregar_evidencia",
    "agregar_evidencia_archivo",
    "agregar_ubicacion",
    "crear_solicitud",
    "listar_solicitudes",
    "listar_talleres_candidatos",
    "obtener_detalle",
    "obtener_eta_cliente",
    "obtener_seguimiento",
    "obtener_ubicacion_tecnico_compartida_cliente",
    "seleccionar_taller",
]
