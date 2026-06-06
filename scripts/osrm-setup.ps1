# Setup OSRM (Bolivia) para rutas VRT/ETA en CU36.
# Requiere Docker. Genera ./data/osrm/bolivia-latest.osrm*
#
# Uso:
#   .\scripts\osrm-setup.ps1
#   docker compose --profile routing up -d osrm backend

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$DataDir = Join-Path $Root 'data\osrm'
$Pbf = Join-Path $DataDir 'bolivia-latest.osm.pbf'
$OsrmImage = 'ghcr.io/project-osrm/osrm-backend:latest'

New-Item -ItemType Directory -Force -Path $DataDir | Out-Null

if (-not (Test-Path $Pbf)) {
  Write-Host 'Descargando extracto OSM Bolivia (~50 MB)...'
  $url = 'https://download.geofabrik.de/south-america/bolivia-latest.osm.pbf'
  Invoke-WebRequest -Uri $url -OutFile $Pbf
} else {
  Write-Host "Ya existe $Pbf - omitiendo descarga."
}

Write-Host 'Extrayendo grafo OSRM (puede tardar varios minutos)...'
docker run --rm -v "${DataDir}:/data" $OsrmImage osrm-extract -p /opt/car.lua /data/bolivia-latest.osm.pbf

Write-Host 'Particionando...'
docker run --rm -v "${DataDir}:/data" $OsrmImage osrm-partition /data/bolivia-latest.osrm

Write-Host 'Customizando (MLD)...'
docker run --rm -v "${DataDir}:/data" $OsrmImage osrm-customize /data/bolivia-latest.osrm

Write-Host 'Listo. Levanta el servicio con:'
Write-Host '  docker compose --profile routing up -d osrm'
