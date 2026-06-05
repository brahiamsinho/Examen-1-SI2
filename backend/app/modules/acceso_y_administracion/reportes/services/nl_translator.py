"""Traductor NL (español) → payload QBE estructurado (sin LLM)."""
from __future__ import annotations

import re
from datetime import datetime, timedelta

from app.modules.acceso_y_administracion.reportes.services.export_intent import (
    parse_export_formats_from_query,
)
from app.modules.acceso_y_administracion.reportes.services.qbe_engine import QBEScope

_MODEL_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r'\b(?:comisi[oó]n(?:es)?|comision(?:es)?)\b', re.I), 'ComisionTaller'),
    (re.compile(r'\b(?:t[eé]cnic[oa]s?|tecnicos?)\b', re.I), 'Tecnico'),
    (re.compile(r'\b(?:cliente?s?|cuentas?\s+cliente)\b', re.I), 'Cliente'),
    (
        re.compile(
            r'\b(?:solicitud(?:es)?|emergencia?s?|atenci[oó]n(?:es)?|historial)\b',
            re.I,
        ),
        'SolicitudEmergencia',
    ),
]

_ESTADO_SOLICITUD: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r'\b(?:finalizad[oa]s?|cerrad[oa]s?|completad[oa]s?)\b', re.I), 'FINALIZADA'),
    (re.compile(r'\b(?:cancelad[oa]s?|anulad[oa]s?)\b', re.I), 'CANCELADA'),
    (re.compile(r'\b(?:pendiente?s?|activ[oa]s?|en\s+curso|abiert[oa]s?)\b', re.I), 'REGISTRADA'),
    (re.compile(r'\ben\s+camino\b', re.I), 'EN_CAMINO'),
    (re.compile(r'\ben\s+atenci[oó]n\b', re.I), 'EN_ATENCION'),
]

_ESTADO_COMISION: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r'\b(?:pendiente?s?)\b', re.I), 'PENDIENTE'),
    (re.compile(r'\b(?:liquidad[oa]s?|pagad[oa]s?)\b', re.I), 'LIQUIDADA'),
    (re.compile(r'\b(?:calculad[oa]s?)\b', re.I), 'CALCULADA'),
]

_ESTADO_TECNICO: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r'\b(?:activ[oa]s?|disponible?s?)\b', re.I), 'ACTIVO'),
    (re.compile(r'\b(?:inactiv[oa]s?|desactivad[oa]s?)\b', re.I), 'INACTIVO'),
]


def _detect_model(query: str) -> str:
    for pattern, model in _MODEL_PATTERNS:
        if pattern.search(query):
            return model
    return 'SolicitudEmergencia'


def _date_filter(query: str) -> tuple[str, str] | None:
    now = datetime.utcnow()
    q = query.lower()
    if re.search(r'\bhoy\b', q):
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return 'created_at__gte', start.isoformat()
    if re.search(r'\b(?:esta\s+semana|última\s+semana|ultima\s+semana|semana\s+pasada)\b', q):
        start = now - timedelta(days=7)
        return 'created_at__gte', start.isoformat()
    if re.search(r'\b(?:este\s+mes|último\s+mes|ultimo\s+mes|mes\s+pasado)\b', q):
        start = now - timedelta(days=30)
        return 'created_at__gte', start.isoformat()
    if re.search(r'\b(?:30\s+d[ií]as|treinta\s+d[ií]as|últimos?\s+30)\b', q):
        start = now - timedelta(days=30)
        return 'created_at__gte', start.isoformat()
    return None


def _match_estado(query: str, model: str) -> str | None:
    patterns = _ESTADO_SOLICITUD
    if model == 'ComisionTaller':
        patterns = _ESTADO_COMISION
    elif model == 'Tecnico':
        patterns = _ESTADO_TECNICO
    elif model == 'Cliente':
        return None
    for pattern, estado in patterns:
        if pattern.search(query):
            return estado
    return None


def translate_nl_to_qbe(query: str, scope: QBEScope | None = None) -> dict:
    """Convierte texto (voz transcrita o escrito) a QBE + formatos de exportación."""
    text = (query or '').strip()
    if not text:
        raise ValueError('La consulta no puede estar vacía.')

    model = _detect_model(text)
    filters: dict = {}
    parts: list[str] = [f'Modelo detectado: {model}']

    estado = _match_estado(text, model)
    if estado:
        filters['estado'] = estado
        parts.append(f'filtro estado={estado}')

    date_key = 'calculado_at__gte' if model == 'ComisionTaller' else 'created_at__gte'
    date_filter = _date_filter(text)
    if date_filter:
        key, val = date_filter
        if model == 'ComisionTaller' and key.startswith('created_at'):
            key = date_key
        filters[key] = val
        parts.append('filtro por rango de fechas reciente')

    export_formats = parse_export_formats_from_query(text)
    if export_formats:
        parts.append(f'exportar en: {", ".join(export_formats)}')

    order_by = ['-created_at']
    if model == 'ComisionTaller':
        order_by = ['-calculado_at']

    qbe = {
        'model': model,
        'filters': filters,
        'order_by': order_by,
    }

    return {
        'qbe': qbe,
        'export_formats': export_formats,
        'interpretation': '; '.join(parts),
    }
