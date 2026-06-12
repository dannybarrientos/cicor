#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════
# CICOR ERP - Minikube Image Loader
# Uso: ./scripts/load-images.sh
# Compatible: Linux, macOS
# ════════════════════════════════════════════════════════════
set -euo pipefail

echo "Cargando imágenes locales hacia Minikube..."

# Lista de módulos
modules=("accounting" "commercial" "hr" "inventory" "operations")

echo "Compilando frontend..."
docker build -t cicor-frontend:v3-local ./frontend

echo "Cargando frontend..."
minikube image load cicor-frontend:v3-local

echo "Aplicando base..."
kubectl apply -f kubernetes/base-web.yaml

for mod in "${modules[@]}"; do
    echo "Compilando DB para módulo $mod..."
    docker build -t "cicor-${mod}-db:v3-local" "./databases/${mod}"

    echo "Compilando API para módulo $mod..."
    docker build -t "cicor-${mod}-api:v3-local" "./apis/${mod}"

    echo "Cargando DB y API para módulo: $mod..."
    minikube image load "cicor-${mod}-db:v3-local"
    minikube image load "cicor-${mod}-api:v3-local"

    echo "Aplicando módulo: $mod..."
    kubectl apply -f "kubernetes/${mod}-bundle.yaml"
done

echo "¡Todas las imágenes han sido cargadas y aplicadas exitosamente!"
