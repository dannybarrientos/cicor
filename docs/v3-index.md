# Documentación de CICOR v3

> Índice de la documentación técnica y funcional del ERP CICOR. Cada documento está pensado para una audiencia específica.

## 📑 Documentos

| Documento | Descripción | Para quién |
|---|---|---|
| [`presentation.md`](presentation.md) | Visión ejecutiva, arquitectura general, demo funcional y roadmap | Stakeholders, arquitectos y nuevos devs |
| [`deployment.md`](deployment.md) | Guía paso a paso de despliegue local con Docker Compose y Minikube | DevOps y nuevos devs |
| [`aws-deployment.md`](aws-deployment.md) | Guía paso a paso de despliegue en AWS (EKS, RDS, ECR, Route 53) | DevOps, SRE, arquitectos cloud |
| [`api-reference.md`](api-reference.md) | Referencia completa de endpoints por módulo con ejemplos `curl` | Desarrolladores frontend y backend |
| [`database-schema.md`](database-schema.md) | Esquemas SQL de las 5 bases de datos, constraints, índices y reglas de negocio | Desarrolladores backend |
| [`design-system.md`](design-system.md) | Paleta de colores por módulo, tipografía, componentes Tailwind y guías visuales | Diseñadores y desarrolladores frontend |
| [`development.md`](development.md) | Setup de entorno, convenciones de código, guía de contribución | Desarrolladores |

## 📖 Orden de lectura recomendado

### Nuevo desarrollador
1. [`presentation.md`](presentation.md) — entendé qué hace el sistema y cómo se organiza
2. [`development.md`](development.md) — prepará tu entorno local
3. [`api-reference.md`](api-reference.md) — conocé los endpoints disponibles
4. [`database-schema.md`](database-schema.md) — entendé el modelo de datos
5. [`design-system.md`](design-system.md) — conocé la identidad visual

### Arquitecto / Tech Lead
1. [`presentation.md`](presentation.md) — arquitectura y decisiones técnicas
2. [`database-schema.md`](database-schema.md) — modelo de datos y reglas de negocio
3. [`api-reference.md`](api-reference.md) — contratos de API

### DevOps / SRE
1. [`presentation.md`](presentation.md) — arquitectura de despliegue
2. [`deployment.md`](deployment.md) — paso a paso con Minikube y Docker Compose
3. [`aws-deployment.md`](aws-deployment.md) — despliegue en AWS EKS
4. [`api-reference.md`](api-reference.md) — health checks y monitoreo

### Desarrollador frontend
1. [`presentation.md`](presentation.md) — contexto general
2. [`design-system.md`](design-system.md) — paleta, componentes y Tailwind
3. [`api-reference.md`](api-reference.md) — endpoints y respuestas esperadas
