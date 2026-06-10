# Guía de Despliegue Local de CICOR con Minikube

Esta guía detalla el paso a paso para desplegar completamente el sistema CICOR en un entorno local utilizando Minikube y Kubernetes. Está diseñada para que cualquier persona pueda realizar el despliegue sin necesidad de conocimientos previos en desarrollo de software.

## 1. Requisitos Previos

Antes de comenzar, asegúrate de tener instalados los siguientes programas en tu computadora:
* **Docker Desktop** (o un motor de contenedores compatible).
* **Minikube**: La herramienta que ejecuta un clúster de Kubernetes de un solo nodo en tu computadora.
* **kubectl**: La herramienta de línea de comandos que permite controlar los clústeres de Kubernetes.

Abre tu terminal (Símbolo del sistema, PowerShell o Git Bash) en la carpeta raíz de tu proyecto, donde se encuentra la carpeta `v3` y sigue los pasos a continuación.

## 2. Iniciar y Configurar Minikube

El primer paso es iniciar tu entorno de Kubernetes local.

1. **Inicia Minikube:** Ejecuta el siguiente comando para arrancar el clúster.
```bash
    minikube start
```

2. **Habilita el complemento Ingress:** Ingress es necesario para permitir que las peticiones desde tu navegador web lleguen correctamente a los módulos de CICOR.
```bash
    minikube addons enable ingress
```

3. **Levanta el túnel de Minikube:** En Docker Desktop para Windows, las IPs de Minikube no son accesibles directamente, por lo que Ingress requiere un túnel. Abre otra ventana de terminal como Administrador, ejecuta el siguiente comando y **déjalo corriendo de fondo**:
```bash
    minikube tunnel
```

## 3. Configurar el Dominio Local

El sistema CICOR utiliza el dominio local `cicor.local` para funcionar. Debes indicarle a tu computadora que este dominio apunta a la IP local expuesta por el túnel (`127.0.0.1`).

1. Abre el bloc de notas (Notepad) **como Administrador**.
2. Ve a `Archivo > Abrir` y navega a la siguiente ruta:
   `C:\Windows\System32\drivers\etc\`
3. En la parte inferior derecha, cambia la opción "Documentos de texto (*.txt)" a "Todos los archivos (*.*)".
4. Abre el archivo llamado `hosts`.
5. Al final del archivo, agrega una nueva línea con la IP local y el dominio:
```text
    127.0.0.1 cicor.local
```
6. Guarda el archivo y ciérralo.

---

## 4. Construir Imágenes Docker en Minikube

Dado que los manifiestos de Kubernetes buscan imágenes locales (`imagePullPolicy: Never`), necesitas construir las imágenes dentro del entorno de Docker de Minikube.

1. En tu terminal (PowerShell), ejecuta el script.
```powershell
    powershell -ExecutionPolicy Bypass -File .\load_images.ps1
```
2. Espera a que el script termine de cargar todas las imágenes. Debería mostrar un mensaje indicando que todas las imágenes han sido cargadas exitosamente.

---

## 5. Verificación del Despliegue

Una vez que hayas ejecutado todos los comandos anteriores, el clúster comenzará a descargar y configurar todo internamente. Este proceso puede tardar unos minutos. 

Para verificar que todos los componentes se están ejecutando correctamente, puedes usar el siguiente comando:

```bash
    kubectl get pods
```
Deberías ver una lista de elementos donde la columna "STATUS" dice `Running`. (Si algunos dicen `ContainerCreating`, espera un par de minutos y vuelve a ejecutar el comando).

## 6. Acceder al Sistema

Una vez que todos los módulos estén en estado `Running`, abre tu navegador web de preferencia (Chrome, Edge, Firefox) e ingresa la siguiente dirección:

```text
    http://cicor.local
```

¡Felicidades! Has desplegado y configurado exitosamente todos los módulos de CICOR en tu entorno local.