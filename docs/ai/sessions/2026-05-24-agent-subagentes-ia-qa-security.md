# Sesión 2026-05-24 — Subagentes ai-inference, qa-testing, security

## Objetivo

Ampliar el equipo de subagentes del proyecto para cubrir dominios que no encajaban bien solo en backend/reviewer.

## Cambios

| Archivo | Acción |
|---------|--------|
| `.cursor/agents/ai-inference.md` | Creado |
| `.cursor/agents/qa-testing.md` | Creado |
| `.cursor/agents/security.md` | Creado |
| `.cursor/agents/orchestrator.md` | Tabla delegación + clasificación ia/qa/seguridad |
| `docs/ai/CURRENT_STATE.md` | Estado subagentes |
| `docs/ai/HANDOFF_LATEST.md` | Handoff |
| `docs/ai/NEXT_STEPS.md` | Paso 0 subagentes |
| `docs/ai/DECISIONS_LOG.md` | DEC-022 |

## Distinción clave

- **ai-researcher** → investigar y comparar tecnologías antes de adoptar.
- **ai-inference** → implementar, depurar y operar el stack IA ya presente en el repo.

## Uso sugerido

```
@.cursor/agents/orchestrator.md  → clasificar tarea
@.cursor/agents/ai-inference.md  → 502 YOLO, ai_payload, rebuild worker
@.cursor/agents/qa-testing.md    → pytest, flutter test, TESTING_STRATEGY
@.cursor/agents/security.md      → secretos, permisos, Stripe, FCM
```

## Pendiente

- No requiere cambios de código de aplicación; solo tooling de agentes.
- Opcional futuro: registrar en `SKILLS_REGISTRY.md` si se crea ese archivo.
