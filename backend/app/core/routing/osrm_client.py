"""Cálculo de ruta y ETA técnico → cliente vía OSRM (contenedor) o fallback haversine."""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from datetime import datetime, timedelta

import httpx

from app.core.config import settings
from app.core.timeutil import utc_now_naive

_log = logging.getLogger(__name__)


@dataclass(frozen=True)
class RutaSeguimientoResult:
    distancia_metros: float
    duracion_segundos: int
    eta_llegada_at: datetime
    geometria: list[list[float]]
    proveedor: str


def _haversine_metros(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6_371_000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))


def _fallback_route(
    *,
    origen_lat: float,
    origen_lon: float,
    destino_lat: float,
    destino_lon: float,
) -> RutaSeguimientoResult:
    dist = _haversine_metros(origen_lat, origen_lon, destino_lat, destino_lon)
    speed_m_s = max(settings.OSRM_FALLBACK_SPEED_KMH, 5.0) * 1000.0 / 3600.0
    dur = int(dist / speed_m_s) if speed_m_s > 0 else 0
    now = utc_now_naive()
    return RutaSeguimientoResult(
        distancia_metros=round(dist, 1),
        duracion_segundos=max(dur, 0),
        eta_llegada_at=now + timedelta(seconds=max(dur, 0)),
        geometria=[[origen_lat, origen_lon], [destino_lat, destino_lon]],
        proveedor="haversine",
    )


async def calcular_ruta_tecnico_cliente(
    *,
    origen_lat: float,
    origen_lon: float,
    destino_lat: float,
    destino_lon: float,
) -> RutaSeguimientoResult:
    """
    Devuelve polyline [[lat, lon], ...], distancia, duración y ETA.
    Origen = técnico, destino = cliente (CU36 VRT).
    """
    base = (settings.OSRM_BASE_URL or "").strip().rstrip("/")
    if settings.OSRM_ENABLED and base:
        url = (
            f"{base}/route/v1/driving/"
            f"{origen_lon},{origen_lat};{destino_lon},{destino_lat}"
        )
        params = {"overview": "full", "geometries": "geojson", "steps": "false"}
        try:
            async with httpx.AsyncClient(timeout=settings.OSRM_TIMEOUT_SECONDS) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
            if data.get("code") == "Ok" and data.get("routes"):
                route = data["routes"][0]
                coords = route["geometry"]["coordinates"]
                geometria = [[float(c[1]), float(c[0])] for c in coords]
                dur = int(route["duration"])
                now = utc_now_naive()
                return RutaSeguimientoResult(
                    distancia_metros=round(float(route["distance"]), 1),
                    duracion_segundos=max(dur, 0),
                    eta_llegada_at=now + timedelta(seconds=max(dur, 0)),
                    geometria=geometria,
                    proveedor="osrm",
                )
            _log.warning("OSRM sin ruta: code=%s", data.get("code"))
        except Exception:
            _log.exception("Fallo consulta OSRM (%s)", base)

    return _fallback_route(
        origen_lat=origen_lat,
        origen_lon=origen_lon,
        destino_lat=destino_lat,
        destino_lon=destino_lon,
    )
