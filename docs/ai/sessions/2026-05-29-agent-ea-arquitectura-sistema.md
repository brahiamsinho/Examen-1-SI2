# Sesión 2026-05-29 — EA diagrama arquitectura del sistema

## Objetivo

Replicar en Enterprise Architect el diagrama de arquitectura “Sistema” (FastAPI central, módulos de dominio, capas, PostgreSQL, servicios externos, apps cliente).

## Hecho

- Paquete **`Model/Arquitectura`** (packageID **28**).
- Diagrama **`component Arquitectura del sistema`** (diagramID **31**, tipo Component).
- **23 componentes** (elementID 174–196): hub API, 3 clientes, 11 módulos, transversales, capas, infra.
- **24 conectores** (366–389): Dependency / Assembly según guía.
- Guía: `docs/ai/EA_ARCHITECTURE_SYSTEM_GUIDE.md`.

## Layout aproximado

- Izquierda: apps + columna de módulos.
- Centro: Backend API FastAPI.
- Arriba: JWT + HTTP/WS.
- Derecha: Core + bloque capas.
- Abajo: PostgreSQL (ancho), medios y externos a los lados, AI worker arriba de externos.

## Pendiente / manual en EA

- Abrir diagrama 31 en EA si `open_diagrams` MCP falla.
- Ajustar colores o **Boundary** visual si el docente exige parecerse al slide.
- Opcional: diagrama **Deployment** con contenedores Docker.
- Componente **Portal Angular Taller** si se quiere simetría con admin.

## Referencia código

`docs/ai/ARCHITECTURE.md`, `backend/app/main.py`.
