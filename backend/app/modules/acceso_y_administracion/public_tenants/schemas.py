from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PublicTenantItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    nombre: str


class PublicTenantByHost(BaseModel):
    slug: str
    nombre: str
    id: int
