"""
CICOR ERP - HR API (Recursos Humanos)
Módulo RRHH [R - Púrpura #A855F7]

Gestión de empleados con CRUD completo.
Puerto interno: 8005 (mapeado desde el contenedor en :8000)

Endpoints activos:
  GET    /health/live                 → Liveness probe
  GET    /health/ready                → Readiness probe
  GET    /health/startup              → Startup probe
  GET    /api/hr/info                 → Info del módulo
  GET    /api/hr/employees            → Listar empleados
  POST   /api/hr/employees            → Registrar empleado
  PUT    /api/hr/employees/{id}       → Actualizar empleado
  DELETE /api/hr/employees/{id}       → Eliminar empleado

CRUD deshabilitado (futuro):
  - Asignar Cargos
  - Registrar Asistencia
  - Calcular Nómina
  - Gestionar Permisos
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

from database import check_db_connection
from database import get_db
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Query
from fastapi import status
from fastapi.middleware.cors import CORSMiddleware
from models import EmployeeCreate
from models import EmployeeStatus
from models import EmployeeUpdate
from prometheus_fastapi_instrumentator import Instrumentator
from pythonjsonlogger import jsonlogger

# ── Logging JSON estructurado ──────────────────────────────────────────────────
_log_handler = logging.StreamHandler()
_log_handler.setFormatter(
    jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={
            "asctime":   "timestamp",
            "levelname": "level",
            "name":      "service",
        },
    )
)
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    handlers=[_log_handler],
)
logger = logging.getLogger("cicor-hr-api")


# ── SQL de inicialización de tabla ────────────────────────────────────────────
_CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS employees (
        id          SERIAL       PRIMARY KEY,
        full_name   VARCHAR(255) NOT NULL,
        email       VARCHAR(255) NOT NULL UNIQUE,
        phone       VARCHAR(20),
        position    VARCHAR(255),
        department  VARCHAR(255),
        hire_date   DATE         NOT NULL,
        salary      NUMERIC(10,2),
        status      VARCHAR(50)  NOT NULL DEFAULT 'ACTIVE',
        created_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
"""


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Crea la tabla al arrancar si no existe; loggea el shutdown."""
    logger.info(
        "Iniciando CICOR HR API",
        # # #extra={"event": "startup", "module": "hr"},
        extra={"event": "startup", "service_module": "hr"},
    )
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(_CREATE_TABLE_SQL)
    logger.info(
        "Tabla 'employees' verificada/creada",
        extra={"event": "db_init"},
    )

    yield  # ← la aplicación corre aquí

    logger.info(
        "Deteniendo CICOR HR API",
        # # #extra={"event": "shutdown", "module": "hr"},
        extra={"event": "shutdown", "service_module": "hr"},
    )


# ── Aplicación FastAPI ─────────────────────────────────────────────────────────
app = FastAPI(
    title="CICOR HR API",
    description="Módulo Recursos Humanos - Gestión de Empleados",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Expone métricas en GET /metrics para Prometheus
Instrumentator().instrument(app).expose(app)


# ── Health Checks ──────────────────────────────────────────────────────────────

@app.get(
    "/health/live",
    tags=["health"],
    summary="Liveness probe",
    description="Kubernetes Liveness: verifica que el proceso está vivo.",
)
async def liveness():
    return {"status": "alive", "service": "hr-api"}


@app.get(
    "/health/ready",
    tags=["health"],
    summary="Readiness probe",
    description="Kubernetes Readiness: verifica que la BD está accesible.",
)
async def readiness():
    if not check_db_connection():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Base de datos no disponible",
        )
    return {"status": "ready", "service": "hr-api"}


@app.get(
    "/health/startup",
    tags=["health"],
    summary="Startup probe",
    description="Kubernetes Startup: verifica que el arranque completó.",
)
async def startup_probe():
    return {"status": "started", "service": "hr-api"}


# ── Info del módulo ────────────────────────────────────────────────────────────

@app.get(
    "/api/hr/info",
    tags=["info"],
    summary="Información del módulo RRHH",
)
async def module_info():
    return {
        "module": "Recursos Humanos",
        "color": "#A855F7",
        "version": "1.0.0",
        "description": "Gestión de empleados y nómina",
        "endpoints": ["/api/hr/employees"],
        "status": "active",
        "crud_activo": ["Empleados"],
        "crud_deshabilitado": [
            "Asignar Cargos",
            "Registrar Asistencia",
            "Calcular Nómina",
            "Gestionar Permisos",
        ],
    }


# ── CRUD Empleados ─────────────────────────────────────────────────────────────

@app.get(
    "/api/hr/employees",
    response_model=list[dict],
    tags=["employees"],
    summary="Listar empleados",
    description="Retorna todos los empleados. Se puede filtrar por departamento o estado.",
)
async def get_employees(
    department: str = Query(None, description="Filtrar por departamento"),
    status_filter: EmployeeStatus = Query(None, alias="status", description="Filtrar por estado"),
):
    """
    Soporta filtros opcionales por query params:
    - `department` → filtra por departamento exacto.
    - `status`     → filtra por estado (ACTIVE, INACTIVE, ON_LEAVE).
    """
    base_query = "SELECT * FROM employees"
    conditions = []
    params = []

    if department:
        conditions.append("department = %s")
        params.append(department)
    if status_filter:
        conditions.append("status = %s")
        params.append(status_filter.value)

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    base_query += " ORDER BY created_at DESC"

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(base_query, params)
            cols = [desc[0] for desc in cur.description]
            rows = [dict(zip(cols, row)) for row in cur.fetchall()]

    logger.info(
        f"Listados {len(rows)} empleados",
        extra={
            "event":      "list_employees",
            "count":      len(rows),
            "department": department,
            "status":     status_filter,
        },
    )
    return rows


@app.post(
    "/api/hr/employees",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    tags=["employees"],
    summary="Registrar un nuevo empleado",
)
async def create_employee(employee: EmployeeCreate):
    """
    Registra un nuevo empleado en el sistema.

    - **full_name**: Nombre y apellido (mínimo dos palabras).
    - **email**: Email único; se rechaza si ya existe en la BD.
    - **hire_date**: No puede ser fecha futura.
    - **salary**: Valor >= 0 (opcional).
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    INSERT INTO employees
                        (full_name, email, phone, position, department, hire_date, salary)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                    """,
                    (
                        employee.full_name,
                        str(employee.email),
                        employee.phone,
                        employee.position,
                        employee.department,
                        employee.hire_date,
                        employee.salary,
                    ),
                )
                cols = [desc[0] for desc in cur.description]
                row = dict(zip(cols, cur.fetchone()))

            except Exception as exc:
                # Email duplicado (unique constraint)
                if "unique" in str(exc).lower() or "duplicate" in str(exc).lower():
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"El email '{employee.email}' ya está registrado",
                    )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error interno al crear el empleado: {str(exc)}",
                )

    logger.info(
        f"Empleado creado: id={row['id']}",
        extra={
            "event":      "create_employee",
            "employee_id": row["id"],
            "email":      row["email"],
            "department": row["department"],
        },
    )
    return row


@app.put(
    "/api/hr/employees/{employee_id}",
    response_model=dict,
    tags=["employees"],
    summary="Actualizar un empleado",
)
async def update_employee(employee_id: int, employee: EmployeeUpdate):
    """
    Actualiza los campos indicados de un empleado existente.
    Solo se modifican los campos enviados en el body (PATCH semántico).

    Casos de uso comunes:
    - Cambiar de departamento: `{ "department": "Finance" }`
    - Dar de baja: `{ "status": "INACTIVE" }`
    - Registrar licencia: `{ "status": "ON_LEAVE" }`
    - Ajuste salarial: `{ "salary": 85000.00 }`
    """
    updates = {k: v for k, v in employee.model_dump().items() if v is not None}

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron campos para actualizar",
        )

    # Convertir EmailStr a string plano para psycopg2
    if "email" in updates:
        updates["email"] = str(updates["email"])

    # Convertir enum a su valor string
    if "status" in updates and isinstance(updates["status"], EmployeeStatus):
        updates["status"] = updates["status"].value

    updates["updated_at"] = datetime.utcnow()

    set_clause = ", ".join([f"{col} = %s" for col in updates])
    values = list(updates.values()) + [employee_id]

    with get_db() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    f"UPDATE employees SET {set_clause} WHERE id = %s RETURNING *",
                    values,
                )
                if cur.rowcount == 0:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Empleado con id={employee_id} no encontrado",
                    )
                cols = [desc[0] for desc in cur.description]
                row = dict(zip(cols, cur.fetchone()))

            except HTTPException:
                raise
            except Exception as exc:
                if "unique" in str(exc).lower() or "duplicate" in str(exc).lower():
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="El email ya está en uso por otro empleado",
                    )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error al actualizar el empleado: {str(exc)}",
                )

    logger.info(
        f"Empleado actualizado: id={employee_id}",
        extra={
            "event":         "update_employee",
            "employee_id":   employee_id,
            "fields_updated": list(updates.keys()),
        },
    )
    return row


@app.delete(
    "/api/hr/employees/{employee_id}",
    tags=["employees"],
    summary="Eliminar un empleado",
)
async def delete_employee(employee_id: int):
    """
    Elimina permanentemente un empleado por su ID.

    Nota: En producción se recomienda usar `status=INACTIVE`
    en lugar de eliminar, para conservar la trazabilidad.
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM employees WHERE id = %s RETURNING id, full_name",
                (employee_id,),
            )
            if cur.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Empleado con id={employee_id} no encontrado",
                )
            deleted = cur.fetchone()

    logger.info(
        f"Empleado eliminado: id={employee_id}",
        extra={
            "event":       "delete_employee",
            "employee_id": employee_id,
            "full_name":   deleted[1] if deleted else None,
        },
    )
    return {"message": f"Empleado {employee_id} eliminado exitosamente"}
