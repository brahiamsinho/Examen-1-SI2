# Plan de rediseño — Landing VehiAssist

**Fecha:** 2026-05-28  
**Skill:** ui-ux-pro-max (B2B SaaS + logística/automotriz)  
**Problema actual:** fondo casi blanco (`#f4f7fb` / `#ffffff`), alto brillo, poco relieve visual → fatiga visual (“me voy a quedar ciego”).  
**Objetivo:** diseño **más moderno** (estructura + componentes + motion sutil), no solo cambiar 3 hex.

---

## 1. Diagnóstico rápido (qué no funciona hoy)

| Issue | Por qué molesta | Regla ui-ux-pro-max |
|-------|----------------|---------------------|
| Fondo muy claro | Reflejo y contraste extremo con naranja CTA | Evitar body text en gray-400; fondos no deben ser “blanco hospital” |
| Hero “plano” | Gradiente suave + tarjetas flotantes genéricas | Hero-Centric + profundidad (glass/sombra), no solo orbes |
| Mucho texto igual | Poca jerarquía entre secciones | B2B: Trust & Authority + bloques claros |
| Navbar flotante blanca | Otro rectángulo brillante encima del hero | Glass en **modo oscuro** o barra integrada con borde sutil |
| Módulos en grid 3×3 repetitivo | Parece “plantilla SaaS 2020” | Bento grid o filas alternadas con iconografía consistente |

---

## 2. Dirección de diseño moderno (independiente del color)

### 2.1 Estilo recomendado por el producto

Del reasoning **Automotive + B2B SaaS + Logistics**:

- **Patrón:** Hero-Centric → Features → Pricing → Social proof → Accesos → Footer  
- **Estilo:** Glassmorphism **suave** + Minimal (no neón, no cyberpunk)  
- **Anti-patrones a evitar:** fondo blanco puro, animaciones exageradas, gradientes en todo el H1, demasiados badges  

### 2.2 Cambios estructurales (layout)

```
[ Nav compacta — logo | 4 links | CTA ]

[ HERO — 55% copy / 45% “product frame” ]
  - H1 una sola línea fuerte + subcopy corto
  - 2 CTA (primario + secundario)
  - 3 métricas en fila (no bloques grandes)
  - Derecha: marco tipo “app/dashboard” (una sola UI, no 4 tarjetas flotantes)

[ LOGOS / confianza ] — “Operado con Angular · FastAPI · Flutter”

[ BENTO — 4 celdas grandes + 2 pequeñas ] — valor SaaS multi-tenant

[ CÓMO FUNCIONA — 3 pasos horizontales con línea conectora ]

[ PRICING — Free | Pro | Max — Pro elevada, fondo distinto ]

[ ACCESOS — cards con icono + flecha ]

[ MÓDULOS — acordeón o tabs por categoría (Core / Ops / Finance) ]

[ CTA FINAL — banda oscura “Registrar taller” ]

[ FOOTER — compacto ]
```

### 2.3 Componentes modernos a introducir

- **Product frame:** borde 1px + `border-radius` 16px + sombra media + screenshot real (taller/admin) cuando exista.  
- **Bento grid** en características (tamaños 2×1, 1×1).  
- **Pricing:** tarjeta Pro con borde glow **sutil** (no blanco sobre blanco).  
- **Section eyebrow** consistente (`OPERACIÓN`, `PRECIOS`, etc.).  
- **Iconos:** solo SVG (Heroicons/Lucide), 24px, un set.  
- **Hover:** `translateY(-2px)` + sombra, sin escalar layout del grid.  
- **`prefers-reduced-motion`:** desactivar pulse y scroll-wheel.

### 2.4 Tipografía (cambio propuesto)

| Rol | Actual | Propuesta |
|-----|--------|-----------|
| Display | Space Grotesk | **Sora** o **Outfit** (más “product 2024”) |
| Body | DM Sans | **Inter** o **Source Sans 3** (lectura larga) |

Mantener 2 familias máximo; cargar solo pesos 400–700.

---

## 3. Tres paletas candidatas (elige UNA como base)

### Opción A — **Dark Pro Soft** (recomendada para tus ojos)

*Inspiración: Fintech/OLED + B2B dashboard. Menos “developer cyan”, más slate.*

| Token | Hex | Uso |
|-------|-----|-----|
| `bg` | `#0B1020` | Fondo página |
| `surface` | `#141B2D` | Cards, nav glass |
| `surface-2` | `#1C2538` | Hover / bandas |
| `border` | `rgba(255,255,255,0.08)` | Separadores |
| `text` | `#E8EDF5` | Cuerpo |
| `muted` | `#94A3B8` | Secundario |
| `primary` | `#38BDF8` | Links, iconos |
| `cta` | `#F59E0B` | Botón principal (ámbar, no naranja quemado) |
| `success` | `#34D399` | Estados EN RUTA |

**Hero:** mesh gradient `#0B1020` → `#1a2744` (sin blanco).  
**CTA secundario:** outline `rgba(255,255,255,0.2)`.

---

### Opción B — **Warm Stone** (claro pero NO cegador)

*Inspiración: Soft UI — papel cálido, no #FFFFFF.*

| Token | Hex | Uso |
|-------|-----|-----|
| `bg` | `#EDE8E0` | Fondo (piedra clara) |
| `surface` | `#F7F4EF` | Cards |
| `surface-2` | `#FFFFFF` | Solo inputs/modales |
| `text` | `#292524` | Texto |
| `muted` | `#57534E` | Secundario |
| `primary` | `#1E40AF` | Azul profundo |
| `cta` | `#C2410C` | Terracota |

**Regla:** nunca usar `#FFFFFF` en más del 30% del viewport visible.

---

### Opción C — **Slate Enterprise** (corporativo B2B)

*Inspiración: Trust & Authority — banca / seguros.*

| Token | Hex | Uso |
|-------|-----|-----|
| `bg` | `#0F172A` | Navy |
| `surface` | `#1E293B` | Cards |
| `primary` | `#60A5FA` | Acento |
| `cta` | `#22C55E` | CTA verde confianza (alternativa al naranja) |
| `gold` | `#EAB308` | Badges “Pro” |

---

## 4. Imágenes y medios

| Zona | Actual | Propuesta |
|------|--------|-----------|
| Hero | Grúa Unsplash | **Mapa/ruta día** o **dashboard mock** con overlay oscuro 40% |
| Features | Taller | **Split** foto + diagrama flujo cliente→taller |
| Módulos | Solo color blocks | Iconos lineales + sin foto por card |
| Pricing | Sin imagen | OK solo cards |

**Tratamiento:** siempre `border-radius` + overlay en fotos sobre fondo oscuro (Opción A/C).

---

## 5. Plan de implementación por fases

### Fase 0 — Decisión (tú, 5 min)

- [ ] Elegir paleta: **A / B / C**  
- [ ] ¿Landing solo oscura o toggle claro/oscuro más adelante?

### Fase 1 — Design tokens (1 sesión)

- [ ] Crear `landing-page.component.scss` con mapa `$tokens` o CSS variables en `.landing { --lp-* }`  
- [ ] Actualizar `index.html` fuentes si cambian  
- [ ] Documentar en este archivo la paleta elegida  

**Archivos:** `landing-page.component.scss`, `index.html`

### Fase 2 — Shell (nav + hero) (1 sesión)

- [ ] Nav: glass oscuro (A/C) o barra stone (B), menos links visibles en desktop  
- [ ] Hero: quitar 3 tarjetas flotantes → 1 **product frame**  
- [ ] Reducir gradiente en H1 (solo última línea o ninguna)  
- [ ] Ajustar contraste WCAG (texto ≥ 4.5:1)

**Archivos:** `.html`, `.scss`, `.ts` (imágenes)

### Fase 3 — Secciones medias (1–2 sesiones)

- [ ] Bento “Una plataforma…”  
- [ ] Pasos con conector visual  
- [ ] Pricing cards con fondo de sección distinto al hero  
- [ ] Banda logos/stack  

### Fase 4 — Módulos + footer (1 sesión)

- [ ] Módulos: tabs o acordeón (9 ítems colapsables en mobile)  
- [ ] Footer alineado a paleta (no mezclar navy viejo con hero nuevo)

### Fase 5 — QA UX (media sesión)

- [ ] 375 / 768 / 1280 px  
- [ ] `prefers-reduced-motion`  
- [ ] Tab focus visible  
- [ ] Lighthouse contraste  

---

## 6. Criterios de “éxito” (cómo saber que quedó bien)

1. Puedes leer el hero **1 minuto** sin sensación de flash/blanco.  
2. Se entiende en **5 s**: qué es, para quién (taller SaaS), qué hacer (registro / precios).  
3. Pricing Free/Pro/Max se distingue sin depender solo del color.  
4. Misma familia visual que admin/taller (opcional fase 6).

---

## 7. Recomendación del agente

**Elegir Opción A (Dark Pro Soft)** para esta landing:

- Coherente con operación 24/7 y mapas/trackers.  
- Evita el problema del blanco actual.  
- Permite glass moderno sin parecer la landing cyan antigua.  
- El admin ya es oscuro → menos choque al navegar.

Si necesitas impresionar en contexto **académico/día**, Opción B (Stone) es el mejor “claro seguro”.

---

## 8. Siguiente paso

Responde con una línea, por ejemplo:

> `Implementa Fase 1+2 con paleta A`

y aplicamos el rediseño en código sobre `frontend/src/app/public/pages/landing/`.

---

## 9. Estado de implementación (2026-05-28)

| Fase | Estado | Notas |
|------|--------|-------|
| 0 — Paleta | ✅ **A elegida** | Dark Pro Soft |
| 1 — Tokens + fuentes | ✅ | `landing-page.component.scss`, Outfit + Inter en `index.html` |
| 2 — Nav + hero | ✅ | Product frame, sin floating cards |
| 3 — Bento + pricing + accesos | ✅ | Secciones en HTML/TS |
| 4 — Módulos / acordeón | ⏳ Opcional | Grid 3×3 actual |
| 5 — QA contraste | ⏳ | `docker compose up -d --build frontend` |

**Sesión código:** `docs/ai/sessions/2026-05-28-agent-landing-paleta-a-dark.md`  
**Documentación flujos CTAs:** `docs/ai/FLOWS_PORTAL_TALLER.md` § landing, `SEQUENCE_FLOWS.md`
