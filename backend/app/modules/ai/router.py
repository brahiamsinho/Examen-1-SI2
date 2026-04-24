# Routers REST — prefijo /api/ai (registrado en main).
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import require_permission
from app.modules.ai import repository as ai_repository
from app.modules.ai.schemas import (
    AssignmentRankIn,
    AssignmentRankOut,
    AudioTranscribeResponse,
    DeteccionObjeto,
    ImageAnalyzeResponse,
    ImageClarity,
    IncidentClassifyIn,
    IncidentClassifyOut,
    IncidentPrioritizeIn,
    IncidentPrioritizeOut,
    StructuredSummaryIn,
    StructuredSummaryOut,
)
from app.modules.ai.services import inference_client
from app.modules.ai.services.assignment_scorer import rank_talleres
from app.modules.ai.services.audio_extract import extract_from_transcription
from app.modules.ai.services.incident_classifier import classify_incident
from app.modules.ai.services.priority_engine import prioritize
from app.modules.ai.services.structured_summary import build_structured_summary
_log = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["IA — inferencia y reglas"])


def _require_inference_available() -> None:
    if settings.AI_INFERENCE_STUB:
        return
    if not settings.AI_ENABLED or not inference_client.inference_base_url():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Inferencia IA deshabilitada. Configure AI_ENABLED=true y AI_INFERENCE_BASE_URL, "
            "o AI_INFERENCE_STUB=true para pruebas.",
        )


@router.post(
    "/audio/transcribe",
    response_model=AudioTranscribeResponse,
    dependencies=[Depends(require_permission("ai:inferir"))],
)
async def transcribe_audio(
    file: UploadFile = File(...),
):
    _require_inference_available()
    raw = await file.read()
    if len(raw) > settings.AI_MAX_AUDIO_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Audio demasiado grande.")
    try:
        data = await inference_client.call_transcribe_audio(
            raw,
            file.filename or "audio.bin",
            file.content_type or "application/octet-stream",
        )
    except Exception as e:
        _log.exception("transcribe_audio")
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail=f"Fallo inferencia audio: {e!s}") from e

    text = str(data.get("text") or "").strip()
    conf = float(data.get("confidence") or 0.0)
    conf = max(0.0, min(1.0, conf))
    ex = extract_from_transcription(text)
    return AudioTranscribeResponse(
        transcripcion=text,
        keywords=ex.keywords,
        confianza=conf,
        tipo_problema_mencionado=ex.tipo_problema_mencionado,
        urgencia_percibida=ex.urgencia_percibida,
        contexto_breve=ex.contexto_breve or None,
    )


@router.post(
    "/images/analyze",
    response_model=ImageAnalyzeResponse,
    dependencies=[Depends(require_permission("ai:inferir"))],
)
async def analyze_image(
    file: UploadFile = File(...),
):
    _require_inference_available()
    raw = await file.read()
    if len(raw) > settings.AI_MAX_IMAGE_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Imagen demasiado grande.")
    try:
        data = await inference_client.call_analyze_image(
            raw,
            file.filename or "image.bin",
            file.content_type or "application/octet-stream",
        )
    except Exception as e:
        _log.exception("analyze_image")
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail=f"Fallo inferencia imagen: {e!s}") from e

    clar = str(data.get("claridad_imagen") or data.get("claridad") or "MEDIA").upper()
    if clar not in ("BAJA", "MEDIA", "ALTA"):
        clar = "MEDIA"
    raw_objs = data.get("objetos_detectados") or []
    objetos: list[DeteccionObjeto] = []
    for o in raw_objs:
        if isinstance(o, dict) and o.get("etiqueta") is not None:
            objetos.append(
                DeteccionObjeto(
                    etiqueta=str(o["etiqueta"]),
                    confianza=max(0.0, min(1.0, float(o.get("confianza") or 0.0))),
                )
            )

    return ImageAnalyzeResponse(
        hallazgos=list(data.get("hallazgos") or []),
        claridad_imagen=ImageClarity(clar),
        confianza=max(0.0, min(1.0, float(data.get("confianza") or 0.0))),
        objetos_detectados=objetos,
        modelo_deteccion=data.get("modelo_deteccion"),
    )


@router.post(
    "/incidents/classify",
    response_model=IncidentClassifyOut,
    dependencies=[Depends(require_permission("ai:inferir"))],
)
async def incidents_classify(body: IncidentClassifyIn):
    return classify_incident(body)


@router.post(
    "/incidents/structured-summary",
    response_model=StructuredSummaryOut,
    dependencies=[Depends(require_permission("ai:inferir"))],
)
async def incidents_structured_summary(body: StructuredSummaryIn):
    return build_structured_summary(body)


@router.post(
    "/incidents/prioritize",
    response_model=IncidentPrioritizeOut,
    dependencies=[Depends(require_permission("ai:inferir"))],
)
async def incidents_prioritize(body: IncidentPrioritizeIn):
    return prioritize(body)


@router.post(
    "/assignment/rank",
    response_model=AssignmentRankOut,
    dependencies=[Depends(require_permission("ai:inferir"))],
)
async def assignment_rank(
    body: AssignmentRankIn,
    db: AsyncSession = Depends(get_db),
):
    rows = await ai_repository.list_talleres_for_assignment(db)
    if not rows:
        return AssignmentRankOut(candidatos=[], mejor_taller_id=None)
    return rank_talleres(body, rows)
