# ☁️ CICOR ERP — Guía de Despliegue en AWS

Guía paso a paso para llevar CICOR de desarrollo local a producción en AWS usando EKS (Elastic Kubernetes Service).

---

## Arquitectura en AWS

```
                     ┌──────────────────────────────────────────┐
                     │              AWS Cloud                    │
                     │                                          │
  Usuario ──▶ Route53 ──▶ ALB Ingress ──▶ EKS Cluster          │
                     │       (ACM TLS)     │                    │
                     │                     ├── cicor-commercial │
                     │                     ├── cicor-inventory  │
                     │                     ├── cicor-accounting │
                     │                     ├── cicor-operations │
                     │                     └── cicor-hr         │
                     │                          │               │
                     │                     ┌────┴────┐          │
                     │                     │  RDS    │          │
                     │                     │PostgreSQL│         │
                     │                     └─────────┘          │
                     │                                          │
                     │  ECR ──── imágenes Docker                │
                     └──────────────────────────────────────────┘
```

| Servicio AWS | Uso en CICOR |
|---|---|
| **EKS** | Orquestación de los 5 microservicios + frontend + nginx |
| **ECR** | Registro privado de imágenes Docker |
| **RDS PostgreSQL** | 5 bases de datos (una por módulo) |
| **Route 53** | DNS para `cicor.tudominio.com` |
| **ACM** | Certificado TLS gratuito |
| **ALB Ingress** | Load balancer que expone las APIs y el frontend |
| **Secrets Manager** | Credenciales de base de datos (opcional, alternativa a K8s Secrets) |

---

## Prerrequisitos

Instalá estas herramientas (todas funcionan en Linux, Mac y Windows):

```bash
# AWS CLI
aws --version

# eksctl — crear y gestionar clusters EKS
eksctl version

# kubectl — interactuar con el cluster
kubectl version --client

# Docker — buildear imágenes
docker --version

# Helm — instalar AWS Load Balancer Controller
helm version
```

Configurá tus credenciales AWS:

```bash
aws configure
# Ingresá: AWS Access Key ID, Secret Access Key, región (ej: us-east-1)
```

---

## Paso 1: Crear repositorios ECR

Cada módulo necesita su propio repositorio de imágenes:

```bash
# Crear repositorios (uno por imagen)
for service in frontend nginx commercial inventory accounting operations hr; do
  aws ecr create-repository \
    --repository-name "cicor/${service}" \
    --image-tag-mutability MUTABLE \
    --region us-east-1
done
```

### Buildear y pushear imágenes

```bash
# Login a ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com

# Account ID
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
REGION=us-east-1
ECR="${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com/cicor"

# Buildear y pushear cada módulo
docker build -t ${ECR}/frontend:latest ./frontend && docker push ${ECR}/frontend:latest
docker build -t ${ECR}/nginx:latest   ./nginx   && docker push ${ECR}/nginx:latest

for mod in commercial inventory accounting operations hr; do
  docker build -t ${ECR}/${mod}-api:latest ./apis/${mod} && docker push ${ECR}/${mod}-api:latest
  docker build -t ${ECR}/${mod}-db:latest  ./databases/${mod} && docker push ${ECR}/${mod}-db:latest
done
```

---

## Paso 2: Crear bases de datos RDS PostgreSQL

Creá una instancia RDS PostgreSQL con 5 bases de datos (una por módulo):

```bash
# Crear subnet group (necesita al menos 2 subnets en distintas AZs)
aws rds create-db-subnet-group \
  --db-subnet-group-name cicor-subnet-group \
  --db-subnet-group-description "CICOR subnets" \
  --subnet-ids subnet-xxx subnet-yyy

# Crear instancia RDS (db.t3.micro = ~$15/mes, suficiente para empezar)
aws rds create-db-instance \
  --db-instance-identifier cicor-postgres \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15 \
  --allocated-storage 20 \
  --master-username cicor_admin \
  --master-user-password TuPasswordSegura123! \
  --db-subnet-group-name cicor-subnet-group \
  --vpc-security-group-ids sg-xxx \
  --backup-retention-period 7 \
  --no-multi-az \
  --region us-east-1
```

Una vez creada, conectate y creá las 5 bases de datos:

```bash
# Obtener el endpoint
aws rds describe-db-instances \
  --db-instance-identifier cicor-postgres \
  --query "DBInstances[0].Endpoint.Address" \
  --output text

# Conectarse y crear las bases
psql -h <rds-endpoint> -U cicor_admin -d postgres

CREATE DATABASE cicor_commercial_db;
CREATE DATABASE cicor_inventory_db;
CREATE DATABASE cicor_accounting_db;
CREATE DATABASE cicor_operations_db;
CREATE DATABASE cicor_hr_db;
\q

# Ejecutar los scripts de inicialización por base
for mod in commercial inventory accounting operations hr; do
  psql -h <rds-endpoint> -U cicor_admin -d cicor_${mod}_db -f databases/${mod}/init.sql
done
```

---

## Paso 3: Crear el cluster EKS

```bash
# Crear cluster (tarda ~15 minutos)
eksctl create cluster \
  --name cicor-prod \
  --region us-east-1 \
  --nodegroup-name cicor-workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 3 \
  --nodes-max 6 \
  --managed
```

Verificá que kubectl apunte al cluster nuevo:

```bash
kubectl config current-context
kubectl get nodes
```

---

## Paso 4: Actualizar los manifests para AWS

Los manifests en `kubernetes/` están listos para Minikube. Para AWS necesitás cambiar las referencias de imágenes y las URLs del ConfigMap.

### 4.1 Cambiar imágenes: Minikube → ECR

En cada `kubernetes/*-bundle.yaml`, cambiá las imágenes. Ejemplo para Comercial:

```yaml
# Antes (Minikube):
image: cicor-commercial-api:v3-local

# Después (ECR):
image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/cicor/commercial-api:latest
```

También necesitás crear un Secret para que EKS pueda pull de ECR:

```bash
kubectl create secret docker-registry ecr-registry \
  --docker-server=${ACCOUNT}.dkr.ecr.us-east-1.amazonaws.com \
  --docker-username=AWS \
  --docker-password=$(aws ecr get-login-password --region us-east-1)
```

### 4.2 Cambiar ConfigMap — dominio y host de BD

```yaml
# Antes (local):
API_PUBLIC_BASE_URL: http://cicor.local/api/commercial
POSTGRES_HOST: cicor-commercial-db-svc

# Después (AWS):
API_PUBLIC_BASE_URL: https://api.tudominio.com/api/commercial
POSTGRES_HOST: <rds-endpoint>.rds.amazonaws.com
POSTGRES_PORT: "5432"
```

---

## Paso 5: Instalar AWS Load Balancer Controller

Necesario para que los Ingress de Kubernetes creen un ALB automáticamente:

```bash
# Crear política IAM para el controlador
curl -O https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json

aws iam create-policy \
  --policy-name AWSLoadBalancerControllerIAMPolicy \
  --policy-document file://iam_policy.json

# Asociar política al service account
eksctl create iamserviceaccount \
  --cluster=cicor-prod \
  --namespace=kube-system \
  --name=aws-load-balancer-controller \
  --role-name AmazonEKSLoadBalancerControllerRole \
  --attach-policy-arn=arn:aws:iam::${ACCOUNT}:policy/AWSLoadBalancerControllerIAMPolicy \
  --approve

# Instalar con Helm
helm repo add eks https://aws.github.io/eks-charts
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=cicor-prod \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller
```

---

## Paso 6: Aplicar los manifests

```bash
# Aplicar todo en orden
kubectl apply -f kubernetes/base-web.yaml
kubectl apply -f kubernetes/commercial-bundle.yaml
kubectl apply -f kubernetes/inventory-bundle.yaml
kubectl apply -f kubernetes/accounting-bundle.yaml
kubectl apply -f kubernetes/operations-bundle.yaml
kubectl apply -f kubernetes/hr-bundle.yaml
```

Verificar que todo arrancó:

```bash
kubectl get pods -A | grep cicor
kubectl get ingress -A | grep cicor
```

Anotá la URL del ALB que aparece en el Ingress:

```bash
kubectl get ingress -n cicor-web -o jsonpath='{.items[0].status.loadBalancer.ingress[0].hostname}'
```

---

## Paso 7: Configurar dominio y TLS

### 7.1 Crear dominio en Route 53

```bash
# Crear zona hospedada (si no existe)
aws route53 create-hosted-zone \
  --name tudominio.com \
  --caller-reference $(date +%s)
```

### 7.2 Solicitar certificado TLS en ACM

```bash
aws acm request-certificate \
  --domain-name api.tudominio.com \
  --validation-method DNS \
  --region us-east-1
```

Seguí las instrucciones de validación DNS que aparecen en la consola de ACM.

### 7.3 Apuntar el dominio al ALB

```bash
# Crear registro A (alias) apuntando al ALB
ALB_DNS=$(kubectl get ingress -n cicor-web -o jsonpath='{.items[0].status.loadBalancer.ingress[0].hostname}')
HOSTED_ZONE_ID=$(aws route53 list-hosted-zones --query "HostedZones[0].Id" --output text)

aws route53 change-resource-record-sets \
  --hosted-zone-id ${HOSTED_ZONE_ID} \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "api.tudominio.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "'"$(aws elbv2 describe-load-balancers --query 'LoadBalancers[0].CanonicalHostedZoneId' --output text)"'",
          "DNSName": "'"${ALB_DNS}"'",
          "EvaluateTargetHealth": true
        }
      }
    }]
  }'
```

---

## Paso 8: CI/CD con GitHub Actions

Agregá este job a `.github/workflows/ci.yml`:

```yaml
  deploy-aws:
    needs: [test-python, lint-python, lint-js]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Login to ECR
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push images
        run: |
          ACCOUNT=${{ secrets.AWS_ACCOUNT_ID }}
          ECR="${ACCOUNT}.dkr.ecr.us-east-1.amazonaws.com/cicor"
          for mod in commercial inventory accounting operations hr; do
            docker build -t ${ECR}/${mod}-api:latest ./apis/${mod}
            docker push ${ECR}/${mod}-api:latest
          done
          docker build -t ${ECR}/frontend:latest ./frontend
          docker push ${ECR}/frontend:latest

      - name: Deploy to EKS
        run: |
          aws eks update-kubeconfig --name cicor-prod --region us-east-1
          kubectl apply -f kubernetes/
          kubectl rollout status deployment -A -l app.kubernetes.io/part-of=cicor
```

Configurá estos secrets en GitHub → Settings → Secrets and variables → Actions:

| Secret | Valor |
|--------|-------|
| `AWS_ACCESS_KEY_ID` | Access key del usuario IAM de deploy |
| `AWS_SECRET_ACCESS_KEY` | Secret key correspondiente |
| `AWS_ACCOUNT_ID` | Tu account ID de AWS (12 dígitos) |

---

## Costos estimados (mensuales)

| Servicio | Configuración | Costo aprox. |
|----------|--------------|-------------|
| EKS Cluster | 3 x t3.medium | ~$120 |
| RDS PostgreSQL | db.t3.micro, 20GB | ~$25 |
| ECR | 7 imágenes, ~500MB c/u | ~$5 |
| ALB | 1 load balancer | ~$20 |
| Route 53 | 1 zona hospedada | ~$0.50 |
| ACM | 1 certificado | Gratis |
| **Total mensual** | | **~$170** |

> 💡 Para desarrollo/pruebas, usá `eksctl delete cluster --name cicor-prod` cuando no lo necesites. El cluster se recrea en 15 minutos con `eksctl create cluster`.

---

## Solución de problemas

### Los pods no arrancan (ImagePullBackOff)

```bash
# Verificar que EKS puede autenticarse con ECR
kubectl describe pod -n cicor-commercial <pod-name> | grep -A5 Events

# Renovar el token de ECR (vence cada 12 horas)
kubectl delete secret ecr-registry --all-namespaces
kubectl create secret docker-registry ecr-registry \
  --docker-server=${ACCOUNT}.dkr.ecr.us-east-1.amazonaws.com \
  --docker-username=AWS \
  --docker-password=$(aws ecr get-login-password --region us-east-1)
```

### Las APIs no se conectan a RDS

```bash
# Verificar que el security group de RDS acepta tráfico del cluster EKS
aws ec2 describe-security-groups --group-ids sg-xxx

# Agregar regla de entrada para PostgreSQL desde el VPC del cluster
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxx \
  --protocol tcp \
  --port 5432 \
  --cidr 10.0.0.0/16  # CIDR del VPC de EKS
```

### El Ingress no crea el ALB

```bash
# Verificar logs del AWS Load Balancer Controller
kubectl logs -n kube-system deployment/aws-load-balancer-controller -f

# Verificar que la subnet tiene tags correctos
# Necesitan: kubernetes.io/cluster/cicor-prod: shared
#           kubernetes.io/role/elb: 1 (para ALB público)
```

---

## Resumen de pasos

| # | Paso | Comando clave | Tiempo |
|---|------|--------------|--------|
| 1 | Crear ECR | `aws ecr create-repository` | 2 min |
| 2 | Build + push imágenes | `docker build && docker push` | 5 min |
| 3 | Crear RDS | `aws rds create-db-instance` | 10 min |
| 4 | Crear EKS | `eksctl create cluster` | 15 min |
| 5 | Instalar ALB Controller | `helm install` | 2 min |
| 6 | Aplicar manifests | `kubectl apply -f kubernetes/` | 1 min |
| 7 | Configurar dominio + TLS | Route 53 + ACM | 5 min |
| 8 | CI/CD | GitHub Actions | — |
| | **Total primera vez** | | **~40 min** |
