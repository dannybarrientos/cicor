# CICOR Kubernetes Manifests

Este directorio contiene los manifiestos de Kubernetes para ejecutar CICOR en Minikube.

Estructura:

- `base-web.yaml`: Deployment y Service compartido de la interfaz web principal.
- `accounting-bundle.yaml`, `commercial-bundle.yaml`, `hr-bundle.yaml`, `inventory-bundle.yaml`, `operations-bundle.yaml`: Bundle de cada módulo con su API, base de datos, ConfigMap, Secret, PVC e Ingress local.

Orden recomendado de aplicación:

1. `kubectl apply -f kubernetes/base-web.yaml`
2. `kubectl apply -f kubernetes/commercial-bundle.yaml` (y los demás bundles)

O usar el script automatizado:

```bash
# En Linux/Mac
./scripts/load-images.sh

# En Windows PowerShell
./scripts/load-images.ps1
```

La UI y las APIs usan `cicor.local` como host de Ingress. En Minikube, apunta ese host a la IP del clúster antes de probar en navegador o con `curl`.
