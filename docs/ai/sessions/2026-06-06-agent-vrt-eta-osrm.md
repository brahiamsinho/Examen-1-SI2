# Sesión 2026-06-06 — VRT + ETA con OSRM (CU36)

## Objetivo
Mostrar en mobile la **ruta real** del técnico hacia el cliente y **tiempo estimado de llegada (ETA)**, no solo línea recta.

## Investigación / decisión
| Opción | Pros | Contras | Decisión |
|--------|------|---------|----------|
| **OSRM** (Open Source Routing Machine) | Open source, Docker oficial, datos OSM, polyline + duración | Requiere preprocesar extracto regional | **Elegido** — contenedor `osrm` perfil `routing` |
| GraphHopper | Similar | Más pesado en setup | No |
| Google Directions API | Muy preciso | API key, costo, vendor lock | No |
| Solo haversine | Cero infra | No sigue calles | **Fallback** si OSRM caído |

**VRT** = Vehicle Routing & Tracking (ruta + seguimiento en mapa).

## Implementación
- `backend/app/core/routing/osrm_client.py` — consulta OSRM `/route/v1/driving/...` + fallback haversine (35 km/h urbano).
- `GET .../ubicacion-tecnico` enriquecido: `cliente_lat/lon`, `ruta { geometria, duracion_minutos, eta_llegada_at, proveedor }`.
- Docker: servicio `osrm` (perfil `routing`), script `scripts/osrm-setup.ps1` (Bolivia Geofabrik).
- Mobile: polyline OSRM en `EmergenciaUbicacionOsmMap`, tarjeta `RutaVrtEtaCard`.

## Activar rutas por calles
```powershell
.\scripts\osrm-setup.ps1
docker compose --profile routing up -d osrm backend
```
Sin OSRM: sigue funcionando con línea directa + ETA aproximado (`proveedor: haversine`).

## QA
1. Solicitud con ubicación cliente + técnico compartiendo GPS + estado EN_CAMINO.
2. Cliente → Ver ubicación del técnico.
3. Con OSRM: polyline curva + «Ruta por calles (OSRM)».
4. Sin OSRM: línea recta + «Aproximación directa».
