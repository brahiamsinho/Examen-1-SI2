# -*- coding: utf-8 -*-
"""Definiciones de 6 organizaciones demo SaaS (2 Free, 2 Pro, 2 Max).

Dominio de correo: `{local}@{slug}.demo.test` (RFC 2606).
Contraseña compartida: `scdemo1` (igual que demo-sc).
Teléfonos: bloque +5917703xxxxx reservado para desarrollo.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.modules.acceso_y_administracion.tenants.models import PlanTenantEnum

from app.seeds.identidades_demo_sc import DEMO_PASSWORD

MULTI_ORG_PASSWORD = DEMO_PASSWORD


@dataclass(frozen=True)
class PersonaSeed:
    local: str
    nombres: str
    apellidos: str
    telefono: str


@dataclass(frozen=True)
class OrgSeed:
    slug: str
    nombre: str
    plan: PlanTenantEnum
    ciudad: str
    taller_nombre: str
    taller_direccion: str
    taller_descripcion: str
    lat: Decimal
    lng: Decimal
    responsable: PersonaSeed
    tecnicos: tuple[PersonaSeed, ...]
    clientes: tuple[PersonaSeed, ...]
    placas: tuple[str, ...]

    def email(self, persona: PersonaSeed) -> str:
        return f"{persona.local}@{self.slug}.demo.test"


def _tel(org_idx: int, person_idx: int) -> str:
    """org_idx 1..6, person_idx 1..9 — único en todo el seed."""
    return f"+5917703{org_idx:01d}{person_idx:02d}"


MULTI_ORGS: tuple[OrgSeed, ...] = (
    OrgSeed(
        slug="org-free-equipetrol",
        nombre="Equipetrol — plan Free",
        plan=PlanTenantEnum.FREE,
        ciudad="Santa Cruz de la Sierra",
        taller_nombre="Taller Equipetrol Express",
        taller_direccion="Av. San Martín 420, Equipetrol",
        taller_descripcion="Auxilio vial y mecánica ligera — tier Free.",
        lat=Decimal("-17.7612"),
        lng=Decimal("-63.1944"),
        responsable=PersonaSeed("responsable", "Ana", "Mendoza", _tel(1, 1)),
        tecnicos=(
            PersonaSeed("tecnico1", "Jorge", "Ríos", _tel(1, 2)),
            PersonaSeed("tecnico2", "Paola", "Vargas", _tel(1, 3)),
        ),
        clientes=(
            PersonaSeed("cliente1", "Miguel", "Torres", _tel(1, 4)),
            PersonaSeed("cliente2", "Lucía", "Paredes", _tel(1, 5)),
        ),
        placas=("SCF101A", "SCF102B"),
    ),
    OrgSeed(
        slug="org-free-urbari",
        nombre="Urbari — plan Free",
        plan=PlanTenantEnum.FREE,
        ciudad="Santa Cruz de la Sierra",
        taller_nombre="Urbari Mecánica Rápida",
        taller_direccion="Calle Urbari 118, zona norte",
        taller_descripcion="Baterías y cambio de llantas — tier Free.",
        lat=Decimal("-17.7480"),
        lng=Decimal("-63.1780"),
        responsable=PersonaSeed("responsable", "Carlos", "Guerrero", _tel(2, 1)),
        tecnicos=(
            PersonaSeed("tecnico1", "Sandra", "Limachi", _tel(2, 2)),
            PersonaSeed("tecnico2", "René", "Justiniano", _tel(2, 3)),
        ),
        clientes=(
            PersonaSeed("cliente1", "Elena", "Morales", _tel(2, 4)),
            PersonaSeed("cliente2", "Héctor", "Saavedra", _tel(2, 5)),
        ),
        placas=("SCU201A", "SCU202B"),
    ),
    OrgSeed(
        slug="org-pro-anillo",
        nombre="4to Anillo — plan Pro",
        plan=PlanTenantEnum.PRO,
        ciudad="Santa Cruz de la Sierra",
        taller_nombre="Auxilio Vial 4to Anillo Pro",
        taller_direccion="Radial 27, Galpón 8, 4to anillo",
        taller_descripcion="Grúa liviana y finanzas integradas — tier Pro.",
        lat=Decimal("-17.7320"),
        lng=Decimal("-63.1650"),
        responsable=PersonaSeed("responsable", "Rodrigo", "Torrez", _tel(3, 1)),
        tecnicos=(
            PersonaSeed("tecnico1", "Marco", "Salas", _tel(3, 2)),
            PersonaSeed("tecnico2", "Daniela", "Flores", _tel(3, 3)),
        ),
        clientes=(
            PersonaSeed("cliente1", "Carlos", "Vega", _tel(3, 4)),
            PersonaSeed("cliente2", "Patricia", "Navia", _tel(3, 5)),
        ),
        placas=("SCP301A", "SCP302B"),
    ),
    OrgSeed(
        slug="org-pro-plan3000",
        nombre="Plan 3000 — plan Pro",
        plan=PlanTenantEnum.PRO,
        ciudad="Santa Cruz de la Sierra",
        taller_nombre="Taller Plan 3000 Pro",
        taller_direccion="Av. Paragua casi 3er anillo, Plan 3000",
        taller_descripcion="Mecánica general con reportes avanzados — tier Pro.",
        lat=Decimal("-17.7890"),
        lng=Decimal("-63.2100"),
        responsable=PersonaSeed("responsable", "Luis", "Rivera", _tel(4, 1)),
        tecnicos=(
            PersonaSeed("tecnico1", "Felipe", "Cortés", _tel(4, 2)),
            PersonaSeed("tecnico2", "Gabriela", "Montaño", _tel(4, 3)),
        ),
        clientes=(
            PersonaSeed("cliente1", "Roberto", "Aguilar", _tel(4, 4)),
            PersonaSeed("cliente2", "Verónica", "Soliz", _tel(4, 5)),
        ),
        placas=("SCP401A", "SCP402B"),
    ),
    OrgSeed(
        slug="org-max-centro",
        nombre="Centro SC — plan Max",
        plan=PlanTenantEnum.ENTERPRISE,
        ciudad="Santa Cruz de la Sierra",
        taller_nombre="Centro Max Asistencia Vial",
        taller_direccion="Calle Ñuflo de Chávez 250, centro",
        taller_descripcion="Operación regional y facturación avanzada — tier Max.",
        lat=Decimal("-17.7835"),
        lng=Decimal("-63.1821"),
        responsable=PersonaSeed("responsable", "Patricio", "Méndez", _tel(5, 1)),
        tecnicos=(
            PersonaSeed("tecnico1", "Oscar", "Bustillos", _tel(5, 2)),
            PersonaSeed("tecnico2", "Natalia", "Romero", _tel(5, 3)),
        ),
        clientes=(
            PersonaSeed("cliente1", "Juan", "Pérez", _tel(5, 4)),
            PersonaSeed("cliente2", "María", "López", _tel(5, 5)),
        ),
        placas=("SCM501A", "SCM502B"),
    ),
    OrgSeed(
        slug="org-max-el-torno",
        nombre="El Torno — plan Max",
        plan=PlanTenantEnum.ENTERPRISE,
        ciudad="Santa Cruz de la Sierra",
        taller_nombre="El Torno Max Vial",
        taller_direccion="Carretera a Warnes km 12, El Torno",
        taller_descripcion="Cobertura extendida y multi-sucursal — tier Max.",
        lat=Decimal("-17.8200"),
        lng=Decimal("-63.2500"),
        responsable=PersonaSeed("responsable", "Eduardo", "Roca", _tel(6, 1)),
        tecnicos=(
            PersonaSeed("tecnico1", "Iván", "Quispe", _tel(6, 2)),
            PersonaSeed("tecnico2", "Camila", "Duran", _tel(6, 3)),
        ),
        clientes=(
            PersonaSeed("cliente1", "Andrés", "Mamani", _tel(6, 4)),
            PersonaSeed("cliente2", "Rosa", "Condori", _tel(6, 5)),
        ),
        placas=("SCM601A", "SCM602B"),
    ),
)
