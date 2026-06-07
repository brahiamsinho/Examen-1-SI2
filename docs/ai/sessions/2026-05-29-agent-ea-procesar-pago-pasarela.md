# Sesión 2026-05-29 — Análisis CU: Procesar pago pasarela

## EA
- Paquete: `/Model/Clase` (27)
- Diagrama: **`class Procesar pago pasarela`** (ID **28**)

## Patrón BCE (máx. 2 vistas)
| Artefacto | ID | Código |
|-----------|-----|--------|
| Actor Cliente | 134 | — |
| V.PagoResumen | 154 | `pago_resumen_screen.dart` |
| V.PagoPasarela | 155 | `pago_metodo_screen` + `pago_confirmacion_screen` + Stripe Sheet |
| PagoController | 156 | `pagos/router.py`, `pagos/service.py` |
| StripePasarelaService | 157 | `stripe_client.py`, PaymentIntent |
| SolicitudEmergencia | 139 | valida `presupuesto_bob`, estado pagable |
| Pago | 158 | tabla `pagos` |
| ComisionTaller | 159 | tras PAGADO |

## API
- `POST .../emergencias/{id}/pagos`
- `POST .../pagos/{pago_id}/confirmar-stripe`
- `POST .../pagos/{pago_id}/completar-simulado` (no tarjeta)

## ER en diagrama
- SolicitudEmergencia `genera` Pago (1 .. 0..*)
- Pago `registra_comision` ComisionTaller (1 .. 0..1)

## Dependencias (solo las necesarias)
- PagoController → SolicitudEmergencia (validar presupuesto/estado)
- PagoController → Pago (crear/confirmar)
- StripePasarelaService → Pago (PaymentIntent)
- **Sin** PagoController → ComisionTaller (se sobreentiende vía Pago)

## Excepciones (solo ficha CU)
- 422 monto ≠ presupuesto
- Stripe no configurado
- Pago cancelado → FALLIDO/ANULADO
- Duplicar POST → reutilizar intent (mobile)
