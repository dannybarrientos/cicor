Write-Host "Cargando imágenes locales hacia Minikube..."

# Lista de módulos
$modules = @("accounting", "commercial", "hr", "inventory", "operations")

Write-Host "Compilando frontend..."
docker build -t cicor-frontend:v3-local ./frontend

Write-Host "Cargando frontend..."
minikube image load cicor-frontend:v3-local

Write-Host "Applicando base..."
kubectl apply -f releases/base/web.yaml

foreach ($mod in $modules) {
    Write-Host "Compilando DB para modulo $mod..."
    docker build -t cicor-$mod-db:v3-local ./databases/$mod

    Write-Host "Compilando API para modulo $mod..."
    docker build -t cicor-$mod-api:v3-local ./apis/$mod

    Write-Host "Cargando DB y API para módulo: $mod..."
    minikube image load "cicor-$mod-db:v3-local"
    minikube image load "cicor-$mod-api:v3-local"

    Write-Host "Applicando modulos: $mod..."
    kubectl apply -f "kubernetes/$mod-bundle.yaml"
}

Write-Host "¡Todas las imágenes han sido cargadas y aplicadas exitosamente!"