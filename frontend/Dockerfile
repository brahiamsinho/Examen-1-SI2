# syntax=docker/dockerfile:1
# Frontend Angular — build cache mount, nginx alpine runtime

FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --legacy-peer-deps

COPY . .
RUN --mount=type=cache,target=/root/.npm \
    npm run build -- --configuration production

# ── Stage 2: Servidor nginx ───────────────────────────────
FROM nginx:alpine AS runtime

# Copiar build de Angular al directorio de nginx
COPY --from=builder /app/dist/emergencias-frontend/browser /usr/share/nginx/html

# Plantilla nginx (envsubst): BACKEND_UPSTREAM desde compose / runtime
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
