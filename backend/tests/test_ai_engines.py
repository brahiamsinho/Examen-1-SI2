# Tests unitarios — motores de reglas IA (sin inferencia externa).
from decimal import Decimal

from app.modules.ai.schemas import (
    AssignmentRankIn,
    IncidentCategory,
    IncidentClassifyIn,
    IncidentPrioritizeIn,
    PriorityLevel,
    StructuredSummaryIn,
    UbicacionResumenIn,
)
from app.modules.ai.services.assignment_scorer import rank_talleres
from app.modules.ai.services.audio_extract import extract_from_transcription
from app.modules.ai.services.incident_classifier import classify_incident
from app.modules.ai.services.priority_engine import prioritize
from app.modules.ai.services.structured_summary import build_structured_summary


def test_audio_extract_battery():
    r = extract_from_transcription("mi auto no enciende y creo que es batería")
    assert "batería" in r.tipo_problema_mencionado or r.tipo_problema_mencionado == "batería"
    assert r.urgencia_percibida in ("media", "alta")


def test_classify_battery():
    out = classify_incident(
        IncidentClassifyIn(
            texto_cliente="no enciende, creo que es la batería",
            transcripcion_audio=None,
            hallazgos_vision=[],
        )
    )
    assert out.categoria == IncidentCategory.BATERIA
    assert "texto" in out.fuentes


def test_classify_vision_choque_boost():
    out = classify_incident(
        IncidentClassifyIn(
            texto_cliente="algo pasó con el auto",
            transcripcion_audio=None,
            hallazgos_vision=["posible choque lateral"],
        )
    )
    assert out.categoria == IncidentCategory.CHOQUE
    assert "imagen" in out.fuentes


def test_prioritize_road_and_crash():
    out = prioritize(
        IncidentPrioritizeIn(
            texto_cliente="choque en carretera",
            transcripcion_audio=None,
            hallazgos_vision=["daño visible lateral"],
            categoria=IncidentCategory.CHOQUE,
            direccion_referencia="km 12 carretera a Oruro",
        )
    )
    assert out.nivel_prioridad == PriorityLevel.ALTA


def test_structured_summary_ficha():
    out = build_structured_summary(
        StructuredSummaryIn(
            texto_cliente="no enciende",
            transcripcion_audio=None,
            hallazgos_vision=[],
            categoria=IncidentCategory.BATERIA,
            ubicacion=UbicacionResumenIn(
                latitud=Decimal("-16.5"),
                longitud=Decimal("-68.1"),
                direccion_referencia="Estacionamiento",
            ),
        )
    )
    assert "BATERIA" in out.resumen or "batería" in out.resumen.lower()
    assert out.ficha.ubicacion_valida is True
    assert out.ficha.tipo_problema == IncidentCategory.BATERIA


def test_assignment_rank_order():
    body = AssignmentRankIn(
        incident_lat=Decimal("-16.49"),
        incident_lng=Decimal("-68.12"),
        categoria=IncidentCategory.BATERIA,
        nivel_prioridad=PriorityLevel.MEDIA,
        ciudad_incidente="La Paz",
    )
    rows = [
        {
            "taller_id": 1,
            "nombre_comercial": "A",
            "ciudad": "La Paz",
            "latitud": -16.489,
            "longitud": -68.119,
            "pendientes_bandeja": 2,
            "especialidad_nombres": ["Electricidad"],
        },
        {
            "taller_id": 2,
            "nombre_comercial": "B",
            "ciudad": "La Paz",
            "latitud": -16.6,
            "longitud": -68.2,
            "pendientes_bandeja": 20,
            "especialidad_nombres": [],
        },
    ]
    out = rank_talleres(body, rows)
    assert out.mejor_taller_id == 1
    assert out.candidatos[0].score >= out.candidatos[1].score
