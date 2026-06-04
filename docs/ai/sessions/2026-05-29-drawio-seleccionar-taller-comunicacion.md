# Sesión 2026-05-29 — Draw.io: comunicación Seleccionar taller

## Artefacto
- `docs/diagrams/seleccionar-taller-comunicacion.drawio`
- Misma plantilla que `CU36-comunicacion-ubicacion-tecnico.drawio` (franjas: mensajes arriba, íconos centro, nombres abajo).

## Trazabilidad ficha → diagrama → código

| Paso ficha | Mensaje diagrama | Código |
|------------|------------------|--------|
| 1 | 1.1 CompletarReporte | `crear_solicitud` + wizard mobile |
| 2 | 1.2 SolicitarCandidatos | `POST /api/ai/assignment/rank` |
| 2b | 1.2b ValidarSolicitud | permisos + solicitud del cliente |
| 3 | 1.3 rankTalleres | `rank_talleres` + `list_talleres_for_assignment` |
| 4–5 | 1.5 viewLista, 1.6 Seleccionar, 1.7 Confirmar | UI `V.SeleccionTaller` (pendiente dedicada; hoy sugerencia en `ai_payload`) |
| 6–7 | 1.8 crearBandejaPendiente, 1.9 notificarTaller | `insert_bandeja_*` (hoy todos los talleres al crear; ideal: solo taller elegido) |
| 8 | subtítulo CU26 | `aceptar_solicitud` en `bandeja.py` |

## Excepciones (2.x)
- 2.1 SinTalleresEnZona → `AssignmentRankOut` vacío
- 2.2 TallerDesactivadoReintentar → re-ranking
- 2.3 ClienteCancela → sin `taller_id`

## Gap documentado
Falta endpoint cliente “confirmar taller”; bandeja se llena para todos los talleres en `crear_solicitud`.
