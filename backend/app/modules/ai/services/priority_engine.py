# Priorización por reglas (IA5).
from __future__ import annotations

from app.modules.ai.schemas import (
    IncidentCategory,
    IncidentPrioritizeIn,
    IncidentPrioritizeOut,
    PriorityLevel,
)
from app.modules.ai.text_normalize import normalize_for_match


def _norm(s: str | None) -> str:
    return normalize_for_match(s)


def prioritize(body: IncidentPrioritizeIn) -> IncidentPrioritizeOut:
    motivos: list[str] = []
    text = _norm(body.texto_cliente) + " " + _norm(body.transcripcion_audio)
    ref = _norm(body.direccion_referencia)

    vision_joined = normalize_for_match(" ".join(body.hallazgos_vision))

    if any(
        normalize_for_match(x) in vision_joined
        for x in ("choque", "impacto", "abollad", "colision", "yolo", "daño", "dano")
    ):
        motivos.append("hallazgo visual de posible choque o daño estructural")

    if body.categoria == IncidentCategory.CHOQUE:
        motivos.append("categoría incidente: choque")

    if "persona" in vision_joined and ("vehiculo" in vision_joined or "coche" in vision_joined):
        motivos.append("visión: personas y vehículo detectados (modelo YOLO); valorar interacción / accidente")

    if any(normalize_for_match(x) in text for x in ("accidente", "choque", "volcad", "herid", "atrapad")):
        motivos.append("texto o audio menciona accidente o riesgo")

    if any(normalize_for_match(x) in text + ref for x in ("carretera", "autopista", "ruta", "peaje", "km ")):
        motivos.append("ubicación o relato sugiere vía rápida / carretera")

    if any(normalize_for_match(x) in text for x in ("urgente", "grave", "incendio", "explosion")):
        motivos.append("lenguaje de alto riesgo")

    if len(motivos) >= 2:
        return IncidentPrioritizeOut(nivel_prioridad=PriorityLevel.ALTA, motivo=motivos)

    if motivos:
        return IncidentPrioritizeOut(nivel_prioridad=PriorityLevel.ALTA, motivo=motivos)

    # Ambigüedad: categoría OTROS y poco texto
    if body.categoria == IncidentCategory.OTROS and len(text.strip()) < 12:
        return IncidentPrioritizeOut(
            nivel_prioridad=PriorityLevel.REVISION_MANUAL,
            motivo=["descripción muy breve y categoría indeterminada"],
        )

    if body.categoria in (IncidentCategory.BATERIA, IncidentCategory.LLANTA):
        return IncidentPrioritizeOut(
            nivel_prioridad=PriorityLevel.MEDIA,
            motivo=["tipo de fallo habitualmente no inmediato"],
        )

    if body.categoria == IncidentCategory.MOTOR:
        return IncidentPrioritizeOut(
            nivel_prioridad=PriorityLevel.MEDIA,
            motivo=["posible fallo mecánico; validar síntomas"],
        )

    return IncidentPrioritizeOut(nivel_prioridad=PriorityLevel.BAJA, motivo=["sin señales de urgencia extrema"])
