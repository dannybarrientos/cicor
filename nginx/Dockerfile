FROM nginx:alpine

# Instalar curl para healthcheck
RUN apk add --no-cache curl

# Copiar config (no montar como :ro)
COPY default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]