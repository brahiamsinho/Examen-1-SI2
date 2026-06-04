# EA — Model Wizard y documentación oficial (obligatorio antes de implementar)

Última actualización: **2026-05-28**  
**Regla del proyecto:** antes de crear diagramas o elementos en EA (MCP o manual), **revisar Model Wizard** y **leer la documentación Sparx** aplicable al tipo de diagrama.

---

## Por qué esta regla

| Sin Wizard / sin docs | Con Wizard + docs |
|----------------------|-------------------|
| Lifelines `Object`/`Class` genéricos | **Boundary**, **Control**, **Entity** con iconos UML |
| MCP crea tipos incorrectos | Partimos del patrón académico (ej. CU2 categorías) |
| Fragmentos `alt` ausentes | Plantillas ya incluyen estructura de interacción |
| Duplicados y “efecto escoba” | Un diagrama canónico por CU |

---

## Acceso al Model Wizard en EA

| Vía | Acción |
|-----|--------|
| Atajo | **Ctrl+Shift+M** |
| Ribbon | **Design → Package → Insert → Insert using Model Wizard** |
| Menú contextual | Clic derecho en paquete → **Add a Model using Wizard** |
| Project Browser | Barra del browser → **New Model from Pattern** |

Pestañas relevantes para este proyecto:

| Pestaña | Uso |
|---------|-----|
| **Model Patterns** | Paquetes UML / análisis (estructura bajo un paquete) |
| **Diagram** | **Patrones de un solo diagrama** (secuencia, clases, despliegue, etc.) |
| Process Guidance | Checklists de proceso (solo si el curso lo pide) |

Fuente: [Model Wizard — EA User Guide](https://sparxsystems.com/enterprise_architect_user_guide/14.0/modeling/model_wizard.html)

---

## Flujo obligatorio del agente (antes de MCP o PlantUML)

```
1. Clasificar diagrama (secuencia BCE, clases, despliegue UML 2.5, C4, …)
2. Abrir Model Wizard → pestaña "Diagram" (o Model Patterns si es paquete completo)
3. Filtrar Perspective: "All UML" o perspectiva del curso
4. Leer descripción del patrón en panel derecho (RTF Sparx)
5. Elegir patrón más cercano (ej. Sequence + Boundary/Control/Entity)
6. Create Pattern(s) bajo paquete destino (ej. Acceso y autenticacion)
7. Ajustar nombres al código real (grep backend/app/modules)
8. Solo entonces: MCP place_elements / messages O export a Git .puml
```

**No** empezar creando elementos sueltos con MCP sin haber revisado si el Wizard ya ofrece el patrón.

---

## Patrones recomendados por tipo (Examen-1-SI2)

| Tipo académico | Wizard (pestaña Diagram) | Documentación EA |
|----------------|--------------------------|------------------|
| Secuencia BCE (login, emergencias) | Sequence / Analysis patterns con Actor + Boundary + Control + Entity | [Sequence Diagram](https://sparxsystems.com/enterprise_architect_user_guide/14.0/model_domains/sequencediagram.html) |
| Clases (login D-010) | Class diagram pattern | [Class Diagram](https://sparxsystems.com/enterprise_architect_user_guide/14.0/model_domains/classdiagram.html) |
| Despliegue UML 2.5 | Deployment diagram pattern | `DEPLOYMENT_DIAGRAM_UML_GUIDE.md` + [Deployment](https://sparxsystems.com/enterprise_architect_user_guide/14.0/model_domains/deploymentdiagram.html) |
| Paquetes lógicos | Model Patterns → Basic UML / Package | [Package](https://sparxsystems.com/enterprise_architect_user_guide/14.0/model_domains/package.html) |

### Secuencia — elementos BCE (documentación oficial)

Sparx define en diagramas de secuencia:

| Elemento | Rol | En nuestro login |
|----------|-----|------------------|
| **Actor** | Usuario externo | Usuario |
| **Boundary** | Pantallas, flujos UI | V.Login |
| **Control** | Orquesta lógica del caso de uso | AuthController |
| **Entity** | Persistencia / datos | M.Usuario, M.Sesion, M.Tenant |

Reglas de comunicación (ECB, defensa oral):

- Actor → solo Boundary o Control (en análisis estricto: Actor → Boundary).
- Boundary ↔ Control.
- Control ↔ Entity.
- Entity no llama a Boundary.

Fuente: [Boundary](https://sparxsystems.com/enterprise_architect_user_guide/14.0/model_domains/boundary.html), [Control](https://sparxsystems.com/enterprise_architect_user_guide/14.0/model_domains/control.html), [Entity](https://sparxsystems.com/enterprise_architect_user_guide/14.0/model_domains/entity.html)

---

## MCP Sparx (después del Wizard)

1. Prompt MCP **`UML_creation_rules`** (servidor Enterprise Architect en Cursor).
2. `args`: `["-enableEdit", "-setTimeout", "30"]`.
3. Backup `.eapx` antes de edición masiva.
4. Preferir **ajustar** diagrama generado por Wizard que crear diagrama paralelo (evitar IDs 11 vs 12 duplicados).

Ver `EA_INTEGRATION.md`, `EA_MCP_LAYOUT_PIPELINE.md`.

---

## Documentación EA — enlaces de consulta rápida

| Tema | URL |
|------|-----|
| Model Wizard | https://sparxsystems.com/enterprise_architect_user_guide/14.0/modeling/model_wizard.html |
| Sequence Diagram | https://sparxsystems.com/enterprise_architect_user_guide/14.0/model_domains/sequencediagram.html |
| Combined Fragments (alt/opt) | https://sparxsystems.com/enterprise_architect_user_guide/14.0/model_domains/combinedfragment.html |
| MCP Server Sparx | https://www.sparxsystems.jp/en/MCP/ |
| Guía secuencia (tutorial) | https://www.sparxsystems.us/guides/uml-with-sparx-ea/diagrams/sequence-diagram/ |

---

## Checklist pre-implementación (copiar en cada sesión EA)

- [ ] Model Wizard abierto y patrón candidato leído (descripción derecha)
- [ ] Tipo de diagrama UML 2.5+ confirmado (no C4 en despliegue)
- [ ] Nombres verificados contra código (`ARCHITECTURE.md`, grep módulos)
- [ ] Un solo diagramID canónico por CU/diagrama
- [ ] PlantUML `.puml` en Git planificado como respaldo
- [ ] `CURRENT_STATE.md` y `LEARNINGS.md` revisados

---

## Relación con otros artefactos del repo

| Archivo | Rol |
|---------|-----|
| `EA_LOGIN_SEQUENCE_RUNBOOK.md` | IDs diagrama login BCE (12) |
| `EA_INTEGRATION.md` | MCP `-enableEdit` |
| `RULES.md` | Prohibiciones globales |
| `uml/sequence-auth-login-bce.puml` | Fuente Git alineada a Wizard |
