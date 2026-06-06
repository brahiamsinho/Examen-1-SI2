# Schemas — horarios de atención por taller.
from __future__ import annotations

from datetime import time

from pydantic import BaseModel, Field, model_validator


NOMBRES_DIA: tuple[str, ...] = (
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado",
    "Domingo",
)


class TallerHorarioDiaRead(BaseModel):
    dia_semana: int = Field(ge=0, le=6)
    nombre_dia: str
    hora_apertura: time | None = None
    hora_cierre: time | None = None
    activo: bool


class TallerHorariosRead(BaseModel):
    horarios: list[TallerHorarioDiaRead]
    abierto_ahora: bool
    zona_horaria: str = "America/La_Paz"


class TallerHorarioDiaUpdateIn(BaseModel):
    dia_semana: int = Field(ge=0, le=6)
    hora_apertura: time | None = None
    hora_cierre: time | None = None
    activo: bool = True

    @model_validator(mode="after")
    def _validar_franja(self) -> TallerHorarioDiaUpdateIn:
        if not self.activo:
            return self
        if self.hora_apertura is None or self.hora_cierre is None:
            raise ValueError("Si el día está activo, hora_apertura y hora_cierre son obligatorias.")
        if self.hora_apertura >= self.hora_cierre:
            raise ValueError("hora_apertura debe ser anterior a hora_cierre.")
        return self


class TallerHorariosUpdateIn(BaseModel):
    horarios: list[TallerHorarioDiaUpdateIn] = Field(min_length=1, max_length=7)

    @model_validator(mode="after")
    def _dias_unicos(self) -> TallerHorariosUpdateIn:
        dias = [h.dia_semana for h in self.horarios]
        if len(dias) != len(set(dias)):
            raise ValueError("Cada dia_semana debe aparecer una sola vez.")
        return self
