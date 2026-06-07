# Sesión 2026-06-04 — Mobile reportes personalizados QBE

## Petición
Implementar reportes personalizados en mobile (no solo plantillas sistema).

## Implementación
- Modelos: `QbePayload`, `ReportMeta`, `ReportExecuteResult`, `ReportNlQueryResult`, `ReportVoiceTranscribeResult`, `ReportRunResult`, `ReportExportFormat`.
- Repository: execute, nl-query, voice multipart, export bytes, create/delete plantilla.
- UI: `taller_reportes_screen.dart` con TabBar Consulta | Plantillas | Dashboard.
- Export: `share_plus` para compartir Excel/PDF/CSV generados por backend.
- Voz: `record` + `POST /app/taller/reportes/voice` (mismo flujo que web).

## Paridad con portal web
| Función | Web | Mobile |
|---------|-----|--------|
| NL query | ✅ | ✅ |
| Voz | ✅ | ✅ |
| Vista previa | ✅ | ✅ (DataTable, máx 50 filas UI) |
| Export Excel/PDF/CSV | ✅ download | ✅ share |
| Guardar plantilla | ✅ | ✅ |
| Eliminar plantilla custom | ✅ | ✅ |
| Ejecutar plantillas | ✅ | ✅ |
| Dashboard operativo | ✅ | ✅ |
| Editor QBE visual | ❌ (NL) | ❌ (NL) |

## Verificación
`flutter analyze lib/taller` — sin errores.
