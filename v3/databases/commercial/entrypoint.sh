#!/bin/sh
# ============================================================
# CICOR ERP - entrypoint.sh
# Módulo: commercial
# Descripción: Inicializa PostgreSQL y ejecuta init.sql
# ============================================================

set -e

echo "🚀 [commercial-db] Iniciando contenedor PostgreSQL..."
echo "   DB:   ${POSTGRES_DB}"
echo "   USER: ${POSTGRES_USER}"

# Delegar al entrypoint oficial de postgres (ejecuta /docker-entrypoint-initdb.d/)
exec docker-entrypoint.sh postgres "$@"
