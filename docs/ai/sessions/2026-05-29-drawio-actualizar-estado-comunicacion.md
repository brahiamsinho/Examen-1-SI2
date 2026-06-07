# Sesión 2026-05-29 — Draw.io: comunicación Actualizar estado atención

## Artefacto
- `docs/diagrams/actualizar-estado-atencion-comunicacion.drawio`

## Trazabilidad ficha → diagrama → código

| Paso | Mensaje | Código |
|------|---------|--------|
| 1 | 1.AbrirServicioAsignado | CU32 lista/detalle técnico |
| 2 | 1.1 AbrirActualizarEstado | `tecnico_servicio_actualizar_estado_screen.dart` |
| 3 | 1.2 ElegirEstado | EN_CAMINO → EN_ATENCION → FINALIZADA |
| 4 | 1.3 IngresarPresupuesto | diálogo BOB si EN_ATENCION |
| 5 | 1.4 patchEstado | `PATCH .../solicitudes/{id}/estado` |
| 5b | 1.2b ValidarTransicion | `_ALLOWED_TRANSITIONS`, schema Pydantic |
| 6 | 1.5 persistirEstado | `SolicitudEmergencia.estado`, `presupuesto_bob` |
| 6b | 1.6 registrarHistorial | `insert_historial_estado` |
| 7 | 1.7 notificarCliente | `notificar_cliente_solicitud_emergencia` |
| 8 | 1.8 viewDetalle | `context.pop()` tras éxito |

## Transiciones (backend)
`TECNICO_ASIGNADO` → `EN_CAMINO` → `EN_ATENCION` → `FINALIZADA`

## Excepciones
- 2.1 → 409 transición no permitida
- 2.2 → ValueError / bloqueo UI sin presupuesto
- 2.3 → 409 estado terminal

## EA
- Análisis clases ID **29** — `docs/ai/sessions/2026-05-29-agent-ea-actualizar-estado-atencion.md`
- Router comenta CU34

## Postcondición
`presupuesto_bob` habilita CU38 (Procesar pago).
