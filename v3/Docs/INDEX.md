# Documentación de CICOR v3

> Índice de la documentación técnica y funcional del ERP CICOR. Cada documento está pensado para una audiencia específica.

## 📑 Documentos

| Documento | Descripción | Para quién |
|---|---|---|
| [`PRESENTACION.md`](PRESENTACION.md) | Visión ejecutiva, arquitectura general, demo funcional y roadmap | Stakeholders, arquitectos y nuevos devs |
| [`DESPLIEGUE.md`](DESPLIEGUE.md) | Guía paso a paso de despliegue local con Docker Compose y Minikube | DevOps y nuevos devs |
| [`REFERENCIA-API.md`](REFERENCIA-API.md) | Referencia completa de endpoints por módulo con ejemplos `curl` | Desarrolladores frontend y backend |
| [`ESQUEMA-BD.md`](ESQUEMA-BD.md) | Esquemas SQL de las 5 bases de datos, constraints, índices y reglas de negocio | Desarrolladores backend |
| [`SISTEMA-DISEÑO.md`](SISTEMA-DISEÑO.md) | Paleta de colores por módulo, tipografía, componentes Tailwind y guías visuales | Diseñadores y desarrolladores frontend |
| [`DESARROLLO.md`](DESARROLLO.md) | Setup de entorno, convenciones de código, guía de contribución | Desarrolladores |

## 📖 Orden de lectura recomendado

### Nuevo desarrollador
1. [`PRESENTACION.md`](PRESENTACION.md) — entendé qué hace el sistema y cómo se organiza
2. [`DESARROLLO.md`](DESARROLLO.md) — prepará tu entorno local
3. [`REFERENCIA-API.md`](REFERENCIA-API.md) — conocé los endpoints disponibles
4. [`ESQUEMA-BD.md`](ESQUEMA-BD.md) — entendé el modelo de datos
5. [`SISTEMA-DISEÑO.md`](SISTEMA-DISEÑO.md) — conocé la identidad visual

### Arquitecto / Tech Lead
1. [`PRESENTACION.md`](PRESENTACION.md) — arquitectura y decisiones técnicas
2. [`ESQUEMA-BD.md`](ESQUEMA-BD.md) — modelo de datos y reglas de negocio
3. [`REFERENCIA-API.md`](REFERENCIA-API.md) — contratos de API

### DevOps / SRE
1. [`PRESENTACION.md`](PRESENTACION.md) — arquitectura de despliegue
2. [`DESPLIEGUE.md`](DESPLIEGUE.md) — paso a paso con Minikube y Docker Compose
3. [`REFERENCIA-API.md`](REFERENCIA-API.md) — health checks y monitoreo

### Desarrollador frontend
1. [`PRESENTACION.md`](PRESENTACION.md) — contexto general
2. [`SISTEMA-DISEÑO.md`](SISTEMA-DISEÑO.md) — paleta, componentes y Tailwind
3. [`REFERENCIA-API.md`](REFERENCIA-API.md) — endpoints y respuestas esperadas
