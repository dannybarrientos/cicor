#!/bin/sh
# ============================================================
# CICOR ERP - entrypoint.sh
# Módulo: operations
# Descripción: Inicializa PostgreSQL y ejecuta init.sql
# ============================================================

set -e

echo "🚀 [operations-db] Iniciando contenedor PostgreSQL..."
echo "   DB:   ${POSTGRES_DB}"
echo "   USER: ${POSTGRES_USER}"

exec docker-entrypoint.sh postgres "$@"
