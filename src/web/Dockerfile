# ── Build stage ──────────────────────────────────────────────────────────────
FROM node:22.12-alpine AS builder

WORKDIR /app

# Build-time environment variables (injected via docker build --build-arg)
ARG PUBLIC_MODULE_NAME=App
ARG PUBLIC_PRIMARY_COLOR=#6366f1
ARG PUBLIC_PRIMARY_DARK=#4f46e5
ARG PUBLIC_API_URL=http://api:8000

ENV PUBLIC_MODULE_NAME=$PUBLIC_MODULE_NAME \
    PUBLIC_PRIMARY_COLOR=$PUBLIC_PRIMARY_COLOR \
    PUBLIC_PRIMARY_DARK=$PUBLIC_PRIMARY_DARK \
    PUBLIC_API_URL=$PUBLIC_API_URL

COPY package.json ./
RUN npm install

COPY . .
RUN npm run astro telemetry disable
RUN npm run build

# ── Serve stage ───────────────────────────────────────────────────────────────
FROM node:22.12-alpine AS runner

WORKDIR /app

ENV HOST=0.0.0.0 \
    PORT=80

COPY --from=builder /app/dist ./dist

EXPOSE 80

CMD ["node", "./dist/server/entry.mjs"]
