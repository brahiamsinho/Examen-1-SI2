from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class QbePayload(BaseModel):
    model: str
    filters: dict[str, Any] = Field(default_factory=dict)
    fields: list[str] | None = None
    order_by: list[str] = Field(default_factory=list)
    aggregations: list[str] = Field(default_factory=list)


class ReportTemplateCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=200)
    descripcion: str = ""
    qbe_payload: QbePayload


class ReportTemplateUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=200)
    descripcion: str | None = None
    qbe_payload: QbePayload | None = None


class ReportTemplateRead(BaseModel):
    id: int
    nombre: str
    descripcion: str
    qbe_payload: dict[str, Any]
    is_system_report: bool
    tenant_id: int | None
    taller_id: int | None
    created_by_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReportExecuteIn(BaseModel):
    model: str
    filters: dict[str, Any] = Field(default_factory=dict)
    fields: list[str] | None = None
    order_by: list[str] = Field(default_factory=list)
    aggregations: list[str] = Field(default_factory=list)


class ReportMeta(BaseModel):
    model: str
    total_records: int
    columns: list[str]
    truncated: bool = False


class ReportExecuteOut(BaseModel):
    meta: ReportMeta
    data: list[dict[str, Any]]


class ReportRunTemplateOut(BaseModel):
    qbe: dict[str, Any]
    report: ReportExecuteOut


class NlQueryIn(BaseModel):
    query: str = Field(min_length=1, max_length=2000)


class NlQueryOut(BaseModel):
    qbe: dict[str, Any]
    export_formats: list[str]
    interpretation: str


class VoiceTranscribeOut(BaseModel):
    transcripcion: str
    confianza: float = 0.0
    provider: str = "gemini"


class VoiceQueryOut(NlQueryOut):
    transcripcion: str
    confianza: float = 0.0
