# =========================================================
# Dockerfile — Frontend Angular
# Build con Node, servir con nginx
# =========================================================

# ── Stage 1: Build ────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Copiar manifests de dependencias primero (cache layer)
COPY package.json package-lock.json ./
RUN npm ci --legacy-peer-deps

# Copiar código fuente y construir
COPY . .
RUN npm run build -- --configuration production

# ── Stage 2: Servidor nginx ───────────────────────────────
FROM nginx:alpine AS runtime

# Copiar build de Angular al directorio de nginx
COPY --from=builder /app/dist/emergencias-frontend/browser /usr/share/nginx/html

# Configuración de nginx para SPA (Angular Router)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
