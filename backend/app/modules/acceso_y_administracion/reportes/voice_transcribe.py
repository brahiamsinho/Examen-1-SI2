"""Transcripción de voz para reportes: Gemini real o Whisper (nunca stub)."""
from __future__ import annotations

from app.core.config import settings
from app.modules.acceso_y_administracion.reportes.gemini_transcribe import transcribe_audio_gemini
from app.modules.ai.services import inference_client


async def transcribe_reporte_voice(
    raw: bytes,
    filename: str,
    content_type: str,
) -> dict:
    if (settings.GEMINI_API_KEY or "").strip():
        return await transcribe_audio_gemini(raw, content_type)

    if settings.AI_INFERENCE_STUB:
        raise RuntimeError(
            "Los reportes por voz no usan modo simulado (AI_INFERENCE_STUB). "
            "Configura GEMINI_API_KEY en .env o usa Whisper real "
            "(AI_INFERENCE_STUB=false y contenedor ai-inference)."
        )

    if not settings.AI_ENABLED:
        raise RuntimeError(
            "Configura GEMINI_API_KEY en .env o habilita Whisper "
            "(AI_ENABLED=true y ai-inference)."
        )

    return await inference_client.call_transcribe_audio(
        raw,
        filename or "audio.bin",
        content_type or "application/octet-stream",
    )
