# Contratos API — módulos IA 1–6
from __future__ import annotations

from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class IncidentCategory(str, Enum):
    BATERIA = "BATERIA"
    LLANTA = "LLANTA"
    CHOQUE = "CHOQUE"
    MOTOR = "MOTOR"
    OTROS = "OTROS"


class PriorityLevel(str, Enum):
    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAJA = "BAJA"
    REVISION_MANUAL = "REVISION_MANUAL"


class ImageClarity(str, Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"


class FuenteInferencia(str, Enum):
    TEXTO = "texto"
    AUDIO = "audio"
    IMAGEN = "imagen"


# --- IA1 audio ---
class AudioTranscribeResponse(BaseModel):
    transcripcion: str
    keywords: list[str] = Field(default_factory=list)
    confianza: float = Field(..., ge=0.0, le=1.0)
    tipo_problema_mencionado: str | None = None
    urgencia_percibida: str | None = None
    contexto_breve: str | None = None


# --- IA2 classify ---
class IncidentClassifyIn(BaseModel):
    texto_cliente: str | None = None
    transcripcion_audio: str | None = None
    hallazgos_vision: list[str] = Field(default_factory=list)


class IncidentClassifyOut(BaseModel):
    categoria: IncidentCategory
    confianza: float = Field(..., ge=0.0, le=1.0)
    fuentes: list[str] = Field(default_factory=list)


# --- IA3 image (API pública) ---
class DeteccionObjeto(BaseModel):
    """Salida de detector preentrenado (p. ej. YOLO/COCO) en el worker de inferencia."""

    etiqueta: str
    confianza: float = Field(..., ge=0.0, le=1.0)


class ImageAnalyzeResponse(BaseModel):
    hallazgos: list[str] = Field(default_factory=list)
    claridad_imagen: ImageClarity
    confianza: float = Field(..., ge=0.0, le=1.0)
    objetos_detectados: list[DeteccionObjeto] = Field(
        default_factory=list,
        description="Clases COCO (etiqueta en español) con confianza por caja.",
    )
    modelo_deteccion: str | None = Field(
        None, description="Identificador del modelo usado, p. ej. yolov8n."
    )


# --- IA4 structured summary ---
class UbicacionResumenIn(BaseModel):
    latitud: Decimal | None = None
    longitud: Decimal | None = None
    direccion_referencia: str | None = None


class StructuredSummaryIn(BaseModel):
    texto_cliente: str | None = None
    transcripcion_audio: str | None = None
    hallazgos_vision: list[str] = Field(default_factory=list)
    categoria: IncidentCategory | None = None
    ubicacion: UbicacionResumenIn | None = None


class FichaIncidente(BaseModel):
    tipo_problema: IncidentCategory
    ubicacion_valida: bool
    evidencia_audio: bool
    evidencia_imagen: bool
    incertidumbre: str = Field(..., description="BAJA | MEDIA | ALTA")


class StructuredSummaryOut(BaseModel):
    resumen: str
    ficha: FichaIncidente


# --- IA5 priority ---
class IncidentPrioritizeIn(BaseModel):
    texto_cliente: str | None = None
    transcripcion_audio: str | None = None
    hallazgos_vision: list[str] = Field(default_factory=list)
    categoria: IncidentCategory | None = None
    direccion_referencia: str | None = None


class IncidentPrioritizeOut(BaseModel):
    nivel_prioridad: PriorityLevel
    motivo: list[str] = Field(default_factory=list)


# --- IA6 assignment ---
class AssignmentRankIn(BaseModel):
    incident_lat: Decimal = Field(..., ge=Decimal("-90"), le=Decimal("90"))
    incident_lng: Decimal = Field(..., ge=Decimal("-180"), le=Decimal("180"))
    categoria: IncidentCategory
    nivel_prioridad: PriorityLevel
    ciudad_incidente: str | None = Field(
        None, description="Ciudad del incidente para matching con taller sin coords"
    )


class TallerCandidatoScore(BaseModel):
    taller_id: int
    nombre_comercial: str
    score: float
    detalle: dict = Field(default_factory=dict)


class AssignmentRankOut(BaseModel):
    candidatos: list[TallerCandidatoScore]
    mejor_taller_id: int | None = None
