# 4.3.1.1 — Diseño físico (diagrama de despliegue)

**Sistema:** Plataforma Inteligente de Atención de Emergencias Vehiculares  
**Fase PUDS:** Diseño — vista de **infraestructura física / despliegue** (UML 2.5+).

| Artefacto | Ubicación |
|-----------|-----------|
| **PlantUML (fuente Git)** | `docs/diagrams/uml/deployment-docker-azure.puml` (D-006) |
| **draw.io (puente MCP)** | `docs/diagrams/uml/../drawio/mermaid/deployment-docker-azure-uml.mmd` |
| **Enterprise Architect** | `Model` → **Despliegue** (package **4**) → **Despliegue Azure UML** (diagramID **9**) |
| **Implementación** | `docker-compose.yml` (raíz del repo) |
| **Guía UML** | `docs/diagrams/agent-memory/DEPLOYMENT_DIAGRAM_UML_GUIDE.md` |

---

## Qué responde este diagrama (nivel 0)

| Pregunta | Respuesta en el diagrama |
|----------|--------------------------|
| ¿Dónde corre el sistema? | **VM Microsoft Azure** con **Ubuntu Server** |
| ¿Cómo se empaqueta? | **Docker / Docker Compose** (contenedores) |
| ¿Quién accede? | **Navegador web** (Angular) y **app móvil** (Flutter) vía **Internet** |
| ¿Qué servicios externos usa? | **Stripe** (pagos/SaaS), **Firebase FCM** (push) |
| ¿Cómo se comunican? | **CommunicationPath** con protocolo (HTTPS, REST, PostgreSQL, SMTP) |

**No confundir** con diagrama **C4 Container**: C4 es arquitectura lógica; este es **UML Deployment** para la materia.

---

## Estructura (como plantilla académica)

```
[Web] ──HTTPS──┐
               ├──► [Internet] ──HTTPS──► [Azure]
[Móvil] ─HTTPS─┘                              └── VM Ubuntu
                                                    └── Docker Compose
                                                          ├── Frontend (nginx+Angular) :80
                                                          ├── Backend (FastAPI) :8000
                                                          ├── PostgreSQL (red interna)
                                                          ├── Mailhog (solo desarrollo)
                                                          └── AI Inference (profile ai, opcional)
```

---

## Mapeo docker-compose → nodos UML

| Servicio `docker-compose` | Contenedor | Puerto host (típico) | Nodo UML | Artefacto |
|---------------------------|------------|----------------------|----------|-----------|
| `frontend` | emergencias_frontend | **80** | Frontend | nginx + Angular SPA |
| `backend` | emergencias_backend | **8000** | Backend | FastAPI + uvicorn |
| `db` | emergencias_db | 5432 (solo red Docker) | Base de datos | PostgreSQL 15 |
| `mailhog` | emergencias_mailhog | 1025 / 8025 | Mailhog (dev) | SMTP / Web UI pruebas |
| `ai-inference` | emergencias_ai_inference | (interno) | Microservicio IA | YOLO / Whisper |
| — | red `emergencias_net` | — | Docker Compose | bridge |

---

## Rutas de comunicación

| Origen | Destino | Protocolo | Notas |
|--------|---------|-----------|-------|
| Web | Internet | HTTPS | Admin / taller Angular |
| Dispositivo móvil | Internet | HTTPS | Cliente y técnico Flutter |
| Internet | Frontend | HTTPS | Puerto **80** publicado en VM |
| Internet | Backend | HTTPS | Puerto **8000** (API directa o vía proxy) |
| Frontend | Backend | REST/HTTP | `BACKEND_UPSTREAM` en contenedor frontend |
| Backend | PostgreSQL | PostgreSQL | `DATABASE_URL` → host `db:5432` |
| Backend | Microservicio IA | REST/HTTP | `AI_INFERENCE_BASE_URL` (profile `ai`) |
| Backend | Mailhog | SMTP | Desarrollo; producción → SMTP real |
| Backend | Stripe | HTTPS API | Billing SaaS fase 3 |
| Backend | Firebase FCM | HTTPS | Notificaciones push |

---

## Variables y entornos (sin hardcode)

| Concepto | Configuración |
|----------|---------------|
| URL pública API | `API_PUBLIC_URL`, `APP_PUBLIC_URL` |
| URL frontend | `FRONTEND_PUBLIC_URL` |
| CORS | `CORS_ORIGINS` |
| BD | `POSTGRES_*`, `DATABASE_URL` |
| Azure | IP elástica / dominio en `.env` de la VM (no en código) |

Mismo `docker-compose.yml` sirve **local** y **Azure** cambiando `.env` y puertos expuestos en el firewall de la VM.

---

## Enterprise Architect

| Diagrama | diagramID | Uso |
|----------|-----------|-----|
| **Despliegue Azure UML** | **9** | **Canónico** para 4.3.1.1 y examen |
| Otros en package 4 (3, 4, 5, 7, 10) | — | Obsoletos — no usar |

**Layout versionado:** `docs/diagrams/ea-templates/layouts/despliegue-azure-d006.layout.json`

**Pasos manuales si el canvas se ve tapado:**

1. Quitar del diagrama elementID **47** (OBSOLETO).  
2. **View → Zoom → Fit in Window**.  
3. Opcional: **Insert → Boundary** para agrupar visualmente Docker dentro de la VM (tutorial Sparx).

---

## Cómo defenderlo en oral

1. “El diseño físico muestra **dónde** se despliega cada pieza, no las clases ni los casos de uso.”  
2. “Usamos **Docker Compose** en una **VM Azure Ubuntu** para reproducir local y producción.”  
3. “La base de datos queda en **red interna**; solo **80** y **8000** suelen exponerse al Internet.”  
4. “El microservicio de **IA** es opcional (`docker compose --profile ai`) para no cargar la VM si no hace falta.”  
5. “Trazabilidad: requisito de despliegue en nube → este diagrama → `docker-compose.yml`.”

---

## Exportar para el Word

1. EA: diagrama **9** → export PNG.  
2. O PlantUML: `plantuml -tpng docs/diagrams/uml/deployment-docker-azure.puml -o docs/diagrams/output/`  
3. Pegar en sección **4.3.1.1 Diseño físico**.
