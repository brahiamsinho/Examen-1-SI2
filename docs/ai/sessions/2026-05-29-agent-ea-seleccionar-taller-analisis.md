# Sesión 2026-05-29 — Análisis de clases: Seleccionar taller

## Ubicación EA
- Paquete: **`/Model/Clase`** (27)
- Diagrama: **`class Seleccionar taller servicio`** (ID **26**) — simplificado
- Obsoleto: ID **25** (`_obsoleto_Seleccionar_taller_v1`)

## Simplificación (2026-05-29)
- 4 vistas → **1** `V.SeleccionTaller`
- Sin `V.WizardEmergencia`, `V.Error`, entidad Cliente duplicada
- Patrón guardado en **`docs/ai/EA_ANALYSIS_CLASS_GUIDE.md`**

## Trazabilidad CU → diagrama → código

| Paso | Análisis | Implementación actual |
|------|----------|------------------------|
| 1 | V.WizardEmergencia | `emergencia_wizard_screen.dart`, `POST /app/cliente/emergencias` |
| 2 | AssignmentRankService | `POST /api/ai/assignment/rank`, también `enrich_solicitud_ai_after_create` |
| 3–4 | V.ListaTalleres | UI dedicada pendiente; ranking en `ai_payload.sugerencia_asignacion` |
| 5–6 | TallerSeleccionController + SolicitudTallerBandeja | **Gap:** hoy `insert_bandeja_pendiente_por_cada_taller` al crear (todos los talleres); falta endpoint cliente “confirmar taller” |
| 7 | (notificación) | `notificaciones_service` tras aceptación taller (CU26) |
| 8 | — | CU26 `aceptar_solicitud` en `taller_emergencias/service/bandeja.py` |

## Elementos (IDs 142–152)
Actor Cliente; boundaries V.WizardEmergencia, V.ListaTalleres, V.ConfirmacionTaller, V.Error; controls TallerSeleccionController, AssignmentRankService; entities SolicitudEmergencia, Taller, Cliente, SolicitudTallerBandeja.

## Relaciones ER
- Cliente `solicita` SolicitudEmergencia (1 .. 0..*)
- Taller `atiende` SolicitudEmergencia (1 .. 0..*)
- SolicitudEmergencia `genera` SolicitudTallerBandeja (1 .. 0..*)
- Taller `recibe` SolicitudTallerBandeja (1 .. 0..*)
