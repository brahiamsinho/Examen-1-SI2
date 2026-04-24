# Ficha y resumen determinísticos sin LLM (IA4).
from __future__ import annotations

from app.modules.ai.schemas import (
    FichaIncidente,
    IncidentCategory,
    StructuredSummaryIn,
    StructuredSummaryOut,
)


def build_structured_summary(body: StructuredSummaryIn) -> StructuredSummaryOut:
    cat = body.categoria or IncidentCategory.OTROS
    textos = " ".join(
        x
        for x in (body.texto_cliente or "", body.transcripcion_audio or "")
        if x
    ).strip()

    ubi = body.ubicacion
    ubicacion_valida = bool(
        ubi and ubi.latitud is not None and ubi.longitud is not None
    )
    evid_audio = bool(body.transcripcion_audio and body.transcripcion_audio.strip())
    evid_img = bool(body.hallazgos_vision)

    incert = "BAJA"
    if cat == IncidentCategory.OTROS:
        incert = "ALTA"
    elif not textos and not evid_audio:
        incert = "MEDIA"
    elif not ubicacion_valida:
        incert = "MEDIA"

    ficha = FichaIncidente(
        tipo_problema=cat,
        ubicacion_valida=ubicacion_valida,
        evidencia_audio=evid_audio,
        evidencia_imagen=evid_img,
        incertidumbre=incert,
    )

    partes: list[str] = []
    if textos:
        partes.append(f"Cliente indica: {textos[:280]}{'…' if len(textos) > 280 else ''}")
    elif evid_audio:
        partes.append("Hay relato en audio transcrito disponible para el taller.")
    else:
        partes.append("Descripción textual limitada.")

    partes.append(f"Clasificación automática del problema: {cat.value}.")

    if body.hallazgos_vision:
        partes.append("Evidencia fotográfica: " + "; ".join(body.hallazgos_vision[:5]) + ".")

    if ubi and ubi.direccion_referencia:
        partes.append(f"Referencia de ubicación: {ubi.direccion_referencia[:200]}.")
    elif ubicacion_valida:
        partes.append("Ubicación GPS registrada.")
    else:
        partes.append("Ubicación GPS no confirmada en los datos recibidos.")

    if incert == "ALTA":
        partes.append("Prioridad sugerida: revisión humana por alta incertidumbre.")
    elif incert == "MEDIA":
        partes.append("Prioridad sugerida: validar detalles con el cliente si es posible.")

    resumen = " ".join(partes)
    return StructuredSummaryOut(resumen=resumen, ficha=ficha)
