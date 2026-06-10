# Stage 1: Build
FROM node:18-alpine AS builder

ARG VITE_API_BASE_URL=http://localhost

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci --silent

COPY . .
RUN VITE_API_BASE_URL=$VITE_API_BASE_URL npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# ✅ INSTALAR CURL PARA HEALTHCHECK
RUN apk add --no-cache curl

# Run as non-root
# # #RUN addgroup -S cicor && adduser -S cicor -G cicor

# ✅ ELIMINAR default.conf de la imagen base para evitar conflictos
RUN rm -f /etc/nginx/conf.d/default.conf

# ✅ COPIAR nuestra configuración COMO default.conf (no app.conf)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# ✅ COPIAR archivos estáticos
COPY --from=builder /app/dist /usr/share/nginx/html

# # #RUN chown -R cicor:cicor /usr/share/nginx/html \
# # #    && chown -R cicor:cicor /var/cache/nginx \
# # #    && chown -R cicor:cicor /var/log/nginx \
# # #    && touch /var/run/nginx.pid \
# # #    && chown -R cicor:cicor /var/run/nginx.pid

# # #USER cicor
# ✅ DAR PERMISOS
RUN chmod -R 755 /usr/share/nginx/html

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
