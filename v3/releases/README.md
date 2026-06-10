# CICOR Releases Locales

Este directorio contiene los manifiestos de Kubernetes para ejecutar CICOR en Minikube.

Estructura:

- `base/`: bundle compartido de la interfaz web principal;
- `commercial/`, `inventory/`, `accounting/`, `operations/`, `hr/`: bundle de cada módulo con su API, base de datos, ConfigMap, Secret, PVC e Ingress local.

Orden recomendado de aplicación:

1. `base/web.yaml`;
2. Los bundles de cada módulo.

La UI y las APIs usan `cicor.local` como host de Ingress. En Minikube, apunta ese host a la IP del clúster antes de probar en navegador o con `curl`.
