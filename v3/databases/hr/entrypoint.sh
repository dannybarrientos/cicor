#!/bin/sh
# ============================================================
# CICOR ERP - entrypoint.sh
# Módulo: hr (Recursos Humanos)
# Descripción: Inicializa PostgreSQL y ejecuta init.sql
# ============================================================

set -e

echo "🚀 [hr-db] Iniciando contenedor PostgreSQL..."
echo "   DB:   ${POSTGRES_DB}"
echo "   USER: ${POSTGRES_USER}"

exec docker-entrypoint.sh postgres "$@"
