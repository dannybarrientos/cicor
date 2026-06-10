# CICOR Local Project Generator Prompt

You are a senior full-stack and platform engineer responsible for generating a complete local-development codebase for CICOR, a modular ERP. Your task is to create a repository structure and the initial implementation for multiple modules using best practices for maintainability, containerization, and Kubernetes deployment in a local Minikube environment.

## Mission
Generate a clean, modular project that includes:
- A FastAPI backend for each module;
- A React frontend for each module;
- A shared Astro-based dashboard;
- PostgreSQL database initialization scripts with migration support;
- Dockerfiles for every buildable component;
- Kubernetes manifests organized under a `releases` directory;
- A root deployment guide in Markdown that explains the exact Minikube release flow and then the module customization process.

## Business context
CICOR is an ERP made of independent modules. For this initial project, the modules to be generated are:
- accounting;
- inventory;
- commercial;
- operations;
- human-resources.

The implementation must remain modular and reusable so that each module can be deployed independently while sharing the same architectural conventions.

## Hard constraints
- Do not generate AWS resources, ECS, EKS, or any cloud-managed services in this version;
- Use Minikube as the only orchestrator;
- Do not open command prompts, run shell commands, compile code, or execute deployment scripts;
- Do not add services that are not explicitly required;
- Do not add business logic beyond the minimum needed to demonstrate structure, configuration, and module customization;
- Keep the output focused and avoid unrelated explanations or digressions;
- Use English for all code, identifiers, file names, YAML manifests, environment variable names, comments in code, and technical resource names;
- Write user-facing application text and documentation in Spanish;
- Use lowercase English names for all generated Kubernetes resources, Docker artifacts, database objects, and file paths where naming is under your control;
- Separate responsibilities cleanly across frontend, backend, database, and deployment assets;
- Use Tailwind CSS in every frontend, including the dashboard;
- Use PostgreSQL for the databases;
- Use ConfigMaps and Secrets correctly;
- Include database migration support so that missing schema objects are created safely on first run;
- Validate your own deliverables before presenting them.

## Required repository structure
Create a repository structure similar to the following, adapting only when necessary for best practice:
- `modules/<module-name>/api`
- `modules/<module-name>/web`
- `modules/dashboard`
- `modules/<module-name>/db`
- `releases/<module-name>/`
- `releases/base/`
- `docs/`

Each module folder must be self-contained and must include its Dockerfile(s), source code, environment examples, and any module-specific configuration.

## Backend requirements
For each module API:
- Use FastAPI with Python;
- Keep the code clean, typed, and maintainable;
- Read configuration from environment variables only;
- Include the database connection variable and any module-specific values required by the frontend and deployment manifests;
- Support a safe startup migration path for PostgreSQL so missing tables are created automatically when appropriate;
- Use a clear separation between routes, schemas, services, and infrastructure concerns;
- Return module metadata and health information in a predictable way;
- Avoid hardcoded environment-specific values;
- Ensure the API can differentiate environments through environment variables passed by Kubernetes.

The API should be prepared to receive, at minimum, the following kinds of environment values:
- database connection string or equivalent PostgreSQL settings;
- module name;
- environment name;
- application title;
- any module-specific feature colors or labels if needed.

## Frontend requirements
For each module web application:
- Use React with Tailwind CSS;
- Build a simple but visually modern and creative ToDo List experience;
- Include smooth, professional animations;

## Dashboard requirements
Create a separate `Dashboard` application using Astro:
- Keep it lightweight and focused on module navigation;
- Reuse the same visual language and Tailwind styling conventions used by the module web applications;
- Show the five available CICOR modules in a clean menu or grid;
- Keep logic simple;
- Use Spanish text in the UI;
- Avoid making the dashboard look like an administrative clone of the module apps; it should feel aligned but simpler.

## Database and migration requirements
Generate PostgreSQL SQL scripts under the database folders:
- Include table definitions using best practices;
- Use primary keys, foreign keys, indexes, timestamps, and audit-friendly columns where appropriate;
- Include the migration or initialization scripts needed to create the schema when the database is empty;
- Keep the schema simple but realistic for a ToDo-oriented module scaffold;
- Make sure each module can have its own database schema or its own logical database separation, depending on the generated structure;
- Do not assume pre-existing tables;
- Make the SQL readable and ready for initial deployment in local containers.

## Kubernetes and releases requirements
Generate Kubernetes manifests under `releases/` with one folder per module and shared base assets when useful.

Each deployment bundle must include, at minimum:
- `Namespace`;
- `ConfigMap`;
- `Secret`;
- `Deployment`;
- `Service`;
- any required `PersistentVolumeClaim` resources;
- any required `Ingress` resources;
- any additional configuration needed for local Minikube operation.

The manifests must follow these rules:
- Use `apiVersion`, `kind`, and `metadata.name` consistently;
- Include `metadata.namespace` when applicable;
- Use lowercase English names;
- Avoid ambiguous resource names;
- Separate the API, web, dashboard, and database workloads clearly;
- Keep the structure suitable for local Minikube only;
- Do not include cloud-specific annotations or AWS dependencies;
- Use `ConfigMap` for non-sensitive configuration;
- Use `Secret` for sensitive values only;
- Keep images pinned to explicit tags rather than `latest`;
- Keep the manifests coherent with the Dockerfiles and local startup instructions.

## Docker requirements
Generate Dockerfiles for every buildable component:
- FastAPI API containers;
- React frontend containers;
- Astro dashboard container;
- PostgreSQL database support if a custom image is necessary;
- Use multi-stage builds where appropriate;
- Keep images small and production-oriented;
- Use secure defaults where compatible;
- Avoid unnecessary tools inside runtime images.

## Environment variable rules
The project must rely on environment variables to customize each module.

At minimum, the following should be configurable through environment variables:
- module name;
- API base URL;
- database host;
- database port;
- database name;
- database user;
- database password;
- frontend title;
- optional primary and accent colors;
- environment identifier.

These values must be consumed by Kubernetes manifests, local environment files, and application code where applicable.

## Documentation requirements
Create a Markdown file inside `releases/` that explains, in Spanish:
1. The exact sequence to release the project locally starting from `minikube start`;
2. How to build images;
3. How to load or reference images in Minikube;
4. How to apply manifests in the correct order;
5. How to verify pods, services, and ingress routes;
6. How to customize each module using environment variables;
7. How the same codebase changes behavior per module through configuration rather than code duplication.

This document must be practical and sequential. First explain deployment; then explain customization.

## Output expectations
Deliver the generated project in a way that is immediately usable as a repository scaffold.

Prefer the following outcomes:
- clear folder structure;
- minimal but correct source code;
- coherent module separation;
- consistent naming;
- working local configuration;
- maintainable YAML and application files.

## Self-validation requirements
Before delivering the result, validate your own work logically and explicitly check that:
- the repository structure matches the requested layout;
- each module has its own API and web code;
- the dashboard exists and uses Astro;
- Tailwind is present in every frontend;
- environment variables drive module customization;
- PostgreSQL migration or initialization is included;
- Kubernetes manifests are complete and internally consistent;
- Secrets and ConfigMaps are separated correctly;
- Dockerfiles exist for every required component;
- the release guide is in Spanish and follows the requested execution order;
- nothing depends on AWS or other cloud services;
- no command execution or shell compilation was performed.

If any part is ambiguous, resolve it using the smallest reasonable assumption and keep the solution centered on CICOR and local Minikube deployment only.
