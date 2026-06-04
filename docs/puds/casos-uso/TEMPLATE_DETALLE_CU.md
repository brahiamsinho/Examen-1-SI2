# Plantilla — Detalle de caso de uso (formato académico)

Este formato replica el entregable del examen SI2: **diagrama de caso de uso UML** + **tabla descriptiva**.

## Estructura obligatoria

### 1. Diagrama de caso de uso

Elementos:

| Elemento UML | Qué representa | En nuestro proyecto |
|--------------|--------------|---------------------|
| **Actor** (figura de palo) | Rol externo que interactúa con el sistema | Cliente, Técnico, Taller, Administrador |
| **Óvalo** | Un caso de uso (funcionalidad) | CU36, CU37, … |
| **Rectángulo / límite** | Frontera del sistema | «Plataforma de Emergencias Vehiculares» |
| **Asociación** (línea actor ↔ CU) | Quién inicia o participa | Línea simple sin flecha en UML use case |

Archivos PlantUML por CU: `docs/diagrams/uml/usecases/ciclo4/CUxx-*.puml`

### 2. Tabla «Descripción de caso de uso»

| Campo | Contenido |
|-------|-----------|
| **Caso de uso** | ID + nombre corto |
| **Propósito** | Objetivo en una frase |
| **Descripción** | Qué permite hacer al actor |
| **Actores** | Todos los roles involucrados |
| **Actor iniciador** | Quién dispara el flujo |
| **Precondición** | CUs o estados previos necesarios |
| **Proceso** | Pasos numerados (flujo principal) |
| **Post-condición** | Estado del sistema al terminar con éxito |
| **Excepciones** | Validaciones, errores, flujos alternos |

## Dónde está el detalle Ciclo 4

- **Tablas completas:** `CICLO4_DETALLE_CASOS_USO.md`
- **Resumen técnico + código:** `CICLO4_SEGUIMIENTO_TIEMPO_REAL.md`
- **Diagramas:** `docs/diagrams/uml/usecases/ciclo4/`

## Cómo llevarlo a Word / EA

1. Renderizar `.puml` con PlantUML o extensión VS Code → PNG/SVG.
2. Copiar cada tabla de `CICLO4_DETALLE_CASOS_USO.md` a Word.
3. Opcional: recrear el mismo CU en Enterprise Architect (Model Wizard → Use Case).
