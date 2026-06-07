# Sesión 2026-05-29 — Draw.io: comunicación Procesar pago pasarela

## Artefacto
- `docs/diagrams/procesar-pago-comunicacion.drawio`
- Plantilla idéntica a CU36 / seleccionar-taller (mensajes arriba, íconos centro, nombres abajo).

## Trazabilidad ficha CU20 → diagrama → código

| Paso | Mensaje | Implementación |
|------|---------|----------------|
| 1 | 1.AbrirPago | `pago_resumen_screen.dart`, seguimiento |
| 2 | 1.1 viewMonto | presupuesto_bob bloqueado en UI |
| 3 | 1.2 ElegirMetodo | `pago_metodo_screen.dart` |
| 4 | 1.3 iniciarPago | `POST /api/app/cliente/emergencias/{id}/pagos` |
| 4b | 1.2b ValidarPresupuesto | `crear_pago_solicitud` 422 si monto ≠ presupuesto |
| 5 | 1.4 crearPaymentIntent | `stripe_client.crear_payment_intent` (TARJETA) |
| 6 | 1.5 return + 1.6 presentPaymentSheet | `PagoIniciadoRead` + `flutter_stripe` |
| 7 | 1.7 confirmarStripe / 1.7b completarSimulado | `confirmar-stripe` / `completar-simulado` |
| 8 | 1.8 marcarPagado + 1.9 registrarComision | `service.py` estado PAGADO + comisión taller |
| 9 | 1.10 viewComprobante | `pago_resultado_screen.dart` |

## Excepciones
- 2.1 → HTTP 422 presupuesto
- 2.2 → sin Stripe: métodos simulados o error
- 2.3 → Sheet cancelado / FALLIDO
- 2.4 → `_coherentPagoIniciado` en mobile

## EA relacionado
- Análisis clases diagrama ID **28** (`docs/ai/sessions/2026-05-29-agent-ea-procesar-pago-pasarela.md`)
