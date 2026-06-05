"""
Motor QBE seguro para SQLAlchemy async — solo modelos en whitelist y filtros validados.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from sqlalchemy import Select, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from app.modules.atencion.taller_emergencias.models import ComisionTaller
from app.modules.clientes_y_vehiculos.clientes.models import Cliente
from app.modules.incidentes.emergencias.models import SolicitudEmergencia
from app.modules.talleres_y_tecnicos.talleres.models import Tecnico

ALLOWED_MODELS: dict[str, type] = {
    'SolicitudEmergencia': SolicitudEmergencia,
    'ComisionTaller': ComisionTaller,
    'Cliente': Cliente,
    'Tecnico': Tecnico,
}

DEFAULT_FIELDS: dict[str, list[str]] = {
    'SolicitudEmergencia': [
        'id', 'estado', 'cliente_id', 'vehiculo_id', 'taller_id', 'tecnico_id',
        'created_at', 'finalizada_at', 'presupuesto_bob',
    ],
    'ComisionTaller': [
        'id', 'solicitud_id', 'taller_id', 'monto_servicio', 'monto_comision',
        'monto_taller_neto', 'estado', 'calculado_at', 'liquidado_at',
    ],
    'Cliente': ['id', 'usuario_id', 'ciudad', 'direccion', 'created_at'],
    'Tecnico': ['id', 'usuario_id', 'documento_identidad', 'estado', 'disponibilidad', 'created_at'],
}

SCOPE_COLUMNS: dict[str, tuple[str, ...]] = {
    'SolicitudEmergencia': ('tenant_id', 'taller_id'),
    'ComisionTaller': ('taller_id',),
    'Cliente': ('tenant_id',),
    'Tecnico': ('taller_id',),
}

_ALLOWED_ROOT_KEYS = frozenset({'model', 'filters', 'aggregations', 'order_by', 'fields'})
_ALLOWED_AGGREGATIONS = frozenset({'count'})
_ALLOWED_LOOKUP_SUFFIXES = frozenset({
    'exact', 'iexact', 'contains', 'icontains',
    'gte', 'lte', 'gt', 'lt', 'in', 'isnull',
})
_FIELD_OR_LOOKUP_KEY = re.compile(
    r'^(?P<field>[a-zA-Z_][a-zA-Z0-9_]*)'
    r'(?:__(?P<lookup>[a-zA-Z_]+))?$',
)


class QBESafeQueryError(ValueError):
    """Entrada QBE inválida o modelo no autorizado."""


@dataclass(frozen=True)
class QBEScope:
    tenant_id: int | None = None
    taller_id: int | None = None


def _reject_dangerous_key(key: str) -> None:
    if '__' in key and key.count('__') > 1:
        raise QBESafeQueryError('No se permiten rutas de lookup anidadas.')
    for token in (';', '--', '/*', '*/', ' ', '\n', '\r', '\t'):
        if token in key:
            raise QBESafeQueryError(f'Caracteres no permitidos en clave de filtro: {key!r}.')


def _validate_filter_value(lookup: str | None, value: Any) -> None:
    if lookup == 'in':
        if not isinstance(value, (list, tuple)):
            raise QBESafeQueryError('Para __in el valor debe ser una lista o tupla.')
        if len(value) > 500:
            raise QBESafeQueryError('Lista __in demasiado grande.')
        for item in value:
            if not isinstance(item, (str, int, float, bool, type(None))):
                raise QBESafeQueryError('Valores en __in deben ser primitivos JSON.')
        return
    if isinstance(value, (dict, list)):
        raise QBESafeQueryError('No se permiten objetos o listas anidadas como valor de filtro.')
    if not isinstance(value, (str, int, float, bool, type(None))):
        raise QBESafeQueryError('Tipo de valor de filtro no permitido.')


def _normalize_filters(filters: Any) -> dict[str, Any]:
    if filters is None:
        return {}
    if not isinstance(filters, dict):
        raise QBESafeQueryError('"filters" debe ser un objeto JSON.')
    out: dict[str, Any] = {}
    for key, value in filters.items():
        if not isinstance(key, str):
            raise QBESafeQueryError('Las claves de filtro deben ser cadenas.')
        _reject_dangerous_key(key)
        m = _FIELD_OR_LOOKUP_KEY.match(key)
        if not m:
            raise QBESafeQueryError(f'Clave de filtro con formato no permitido: {key!r}.')
        lookup = m.group('lookup')
        if lookup is not None and lookup not in _ALLOWED_LOOKUP_SUFFIXES:
            raise QBESafeQueryError(f'Lookup no permitido en clave: {key!r}.')
        _validate_filter_value(lookup, value)
        out[key] = value
    if len(out) > 50:
        raise QBESafeQueryError('Demasiadas claves en filters.')
    return out


def _normalize_order_by(order_by: Any) -> list[str]:
    if order_by is None:
        return []
    if not isinstance(order_by, list):
        raise QBESafeQueryError('"order_by" debe ser una lista de cadenas.')
    for item in order_by:
        if not isinstance(item, str):
            raise QBESafeQueryError('order_by debe contener solo cadenas.')
        stripped = item.removeprefix('-')
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', stripped):
            raise QBESafeQueryError(f'Campo order_by no permitido: {item!r}.')
    return list(order_by)


def _normalize_fields_list(fields: Any) -> list[str] | None:
    if fields is None:
        return None
    if not isinstance(fields, list):
        raise QBESafeQueryError('"fields" debe ser una lista de cadenas o null.')
    if len(fields) == 0:
        return None
    out: list[str] = []
    for item in fields:
        if not isinstance(item, str) or not item.strip():
            raise QBESafeQueryError('Cada elemento de "fields" debe ser una cadena no vacía.')
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', item):
            raise QBESafeQueryError(f'Nombre de campo no permitido en fields: {item!r}.')
        out.append(item)
    if len(out) > 80:
        raise QBESafeQueryError('Demasiados campos en "fields".')
    return out


def validate_qbe_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise QBESafeQueryError('El payload QBE debe ser un objeto JSON.')
    extra = set(payload.keys()) - _ALLOWED_ROOT_KEYS
    if extra:
        raise QBESafeQueryError(f'Claves no permitidas en el payload: {sorted(extra)}.')
    model_name = payload.get('model')
    if not model_name or not isinstance(model_name, str):
        raise QBESafeQueryError('Se requiere "model" como cadena no vacía.')
    if model_name not in ALLOWED_MODELS:
        raise QBESafeQueryError(f'Modelo "{model_name}" no está autorizado para consultas QBE.')
    return {
        'model': model_name,
        'filters': _normalize_filters(payload.get('filters')),
        'aggregations': payload.get('aggregations') or [],
        'order_by': _normalize_order_by(payload.get('order_by')),
        'fields': _normalize_fields_list(payload.get('fields')),
    }


def _get_column(model_cls: type, name: str) -> InstrumentedAttribute:
    if not hasattr(model_cls, name):
        raise QBESafeQueryError(f'El campo "{name}" no existe en el modelo "{model_cls.__name__}".')
    col = getattr(model_cls, name)
    if not isinstance(col, InstrumentedAttribute):
        raise QBESafeQueryError(f'"{name}" no es un campo válido para filtrar.')
    return col


def _coerce_value(col: InstrumentedAttribute, value: Any) -> Any:
    if value is None:
        return None
    col_type = col.property.columns[0].type.python_type if col.property.columns else None
    if col_type is None:
        return value
    if isinstance(value, str) and col_type in (datetime, date):
        try:
            if 'T' in value or ' ' in value:
                return datetime.fromisoformat(value.replace('Z', '+00:00').split('+')[0])
            return date.fromisoformat(value)
        except ValueError:
            return value
    if issubclass(col_type, Enum) and isinstance(value, str):
        return value
    if col_type is Decimal and isinstance(value, (int, float, str)):
        return Decimal(str(value))
    return value


def _apply_filter(col: InstrumentedAttribute, lookup: str | None, value: Any):
    value = _coerce_value(col, value)
    if lookup is None or lookup == 'exact':
        return col == value
    if lookup == 'iexact':
        return func.lower(col) == func.lower(str(value))
    if lookup == 'contains':
        return col.contains(value)
    if lookup == 'icontains':
        return col.ilike(f'%{value}%')
    if lookup == 'gte':
        return col >= value
    if lookup == 'lte':
        return col <= value
    if lookup == 'gt':
        return col > value
    if lookup == 'lt':
        return col < value
    if lookup == 'in':
        return col.in_(list(value))
    if lookup == 'isnull':
        if value is True:
            return col.is_(None)
        if value is False:
            return col.is_not(None)
        raise QBESafeQueryError('__isnull requiere true o false.')
    raise QBESafeQueryError(f'Lookup no soportado: {lookup}')


def _serialize_value(val: Any) -> Any:
    if val is None:
        return None
    if isinstance(val, Enum):
        return val.value
    if isinstance(val, (datetime, date)):
        return val.isoformat()
    if isinstance(val, Decimal):
        return float(val)
    return val


class QBEEngine:
    MAX_ROWS = 500

    def __init__(self, scope: QBEScope | None = None):
        self.scope = scope or QBEScope()

    def _apply_scope(self, model_cls: type, conditions: list) -> None:
        scope_cols = SCOPE_COLUMNS.get(model_cls.__name__, ())
        if 'tenant_id' in scope_cols and self.scope.tenant_id is not None:
            conditions.append(_get_column(model_cls, 'tenant_id') == self.scope.tenant_id)
        if 'taller_id' in scope_cols and self.scope.taller_id is not None:
            conditions.append(_get_column(model_cls, 'taller_id') == self.scope.taller_id)

    def _build_select(self, normalized: dict[str, Any]) -> tuple[Select, type, list[str]]:
        model_name = normalized['model']
        model_cls = ALLOWED_MODELS[model_name]
        fields = normalized['fields'] or DEFAULT_FIELDS.get(model_name) or []
        for name in fields:
            _get_column(model_cls, name)

        conditions: list = []
        self._apply_scope(model_cls, conditions)

        for key, value in normalized['filters'].items():
            m = _FIELD_OR_LOOKUP_KEY.match(key)
            assert m
            field_name = m.group('field')
            lookup = m.group('lookup')
            col = _get_column(model_cls, field_name)
            conditions.append(_apply_filter(col, lookup, value))

        stmt = select(model_cls)
        if conditions:
            stmt = stmt.where(and_(*conditions))

        order_by = normalized['order_by']
        if order_by:
            order_exprs = []
            for item in order_by:
                desc = item.startswith('-')
                field_name = item.removeprefix('-')
                col = _get_column(model_cls, field_name)
                order_exprs.append(col.desc() if desc else col.asc())
            stmt = stmt.order_by(*order_exprs)

        return stmt, model_cls, fields

    async def execute(self, db: AsyncSession, payload: dict[str, Any]) -> dict[str, Any]:
        normalized = validate_qbe_payload(payload)
        stmt, model_cls, fields = self._build_select(normalized)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = int((await db.execute(count_stmt)).scalar_one())

        limited_stmt = stmt.limit(self.MAX_ROWS)
        result = await db.execute(limited_stmt)
        rows = result.scalars().all()

        data: list[dict[str, Any]] = []
        for row in rows:
            data.append({f: _serialize_value(getattr(row, f)) for f in fields})

        return {
            'meta': {
                'model': normalized['model'],
                'total_records': total,
                'columns': fields,
                'truncated': total > len(data),
            },
            'data': data,
        }
