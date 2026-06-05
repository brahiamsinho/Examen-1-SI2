"""Transcripción de audio para reportes vía Google Gemini (API key en `.env`)."""
from __future__ import annotations

import base64
import logging
from typing import Any

import httpx

from app.core.config import settings

_log = logging.getLogger(__name__)

_PROMPT = (
    "Transcribe el audio a texto en español. "
    "Devuelve únicamente la transcripción literal de lo hablado, "
    "sin comillas, sin markdown y sin explicaciones."
)

_SUPPORTED_MIME = {
    "audio/webm",
    "audio/wav",
    "audio/x-wav",
    "audio/mp3",
    "audio/mpeg",
    "audio/ogg",
    "audio/mp4",
    "audio/aac",
}


def _normalize_mime(content_type: str) -> str:
    ct = (content_type or "audio/webm").split(";")[0].strip().lower()
    return ct if ct in _SUPPORTED_MIME else "audio/webm"


def _extract_text(payload: dict[str, Any]) -> str:
    for cand in payload.get("candidates") or []:
        content = cand.get("content") or {}
        for part in content.get("parts") or []:
            text = part.get("text")
            if isinstance(text, str) and text.strip():
                return text.strip()
    feedback = payload.get("promptFeedback") or {}
    block = feedback.get("blockReason")
    if block:
        raise ValueError(f"Gemini bloqueó la transcripción: {block}")
    raise ValueError("Gemini no devolvió texto de transcripción.")


async def transcribe_audio_gemini(audio_bytes: bytes, content_type: str) -> dict[str, Any]:
    api_key = (settings.GEMINI_API_KEY or "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY no configurada.")
    model = (settings.GEMINI_MODEL or "gemini-2.5-flash").strip()
    mime = _normalize_mime(content_type)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": _PROMPT},
                    {
                        "inline_data": {
                            "mime_type": mime,
                            "data": base64.b64encode(audio_bytes).decode("ascii"),
                        }
                    },
                ],
            }
        ],
        "generationConfig": {"temperature": 0},
    }
    timeout = httpx.Timeout(settings.AI_INFERENCE_TIMEOUT_S)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, params={"key": api_key}, json=body)
        if resp.status_code >= 400:
            _log.warning("Gemini transcribe HTTP %s: %s", resp.status_code, resp.text[:400])
            resp.raise_for_status()
        data = resp.json()
    text = _extract_text(data)
    if not text:
        raise ValueError("Transcripción vacía.")
    return {"text": text, "confidence": 0.0, "provider": "gemini"}
