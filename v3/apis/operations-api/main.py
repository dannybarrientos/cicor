"""
CICOR ERP - Operations API
Módulo Operaciones [O - Naranja #F97316]

Gestión de procesos operacionales con CRUD completo.
Puerto interno: 8004 (mapeado desde el contenedor en :8000)

Endpoints activos:
  GET  /health/live            → Liveness probe
  GET  /health/ready           → Readiness probe
  GET  /health/startup         → Startup probe
  GET  /api/operations/info    → Info del módulo
  GET  /api/operations/processes        → Listar procesos
  POST /api/operations/processes        → Crear proceso
  PUT  /api/operations/processes/{id}   → Actualizar proceso
  DELETE /api/operations/processes/{id} → Eliminar proceso
"""

import os
import logging
from datetime import datetime
from typing import List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from pythonjsonlogger import jsonlogger

from database import get_db, check_db_connection
from models import ProcessCreate, ProcessUpdate, ProcessStatus


# ── Logging JSON estructurado ──────────────────────────────────────────────────
_log_handler = logging.StreamHandler()
_log_handler.setFormatter(
    jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={
            "asctime": "timestamp",
            "levelname": "level",
            "name": "service",
        },
    )
)
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    handlers=[_log_handler],
)
logger = logging.getLogger("cicor-operations-api")


# ── SQL de inicialización de tabla ────────────────────────────────────────────
_CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS processes (
        id                 SERIAL PRIMARY KEY,
        process_name       VARCHAR(255) NOT NULL,
        description        TEXT,
        owner              VARCHAR(255),
        status             VARCHAR(50)  NOT NULL DEFAULT 'PLANNING',
        start_date         DATE         NOT NULL,
        expected_end_date  DATE,
        actual_end_date    DATE,
        created_at         TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at         TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
"""


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa la tabla al arrancar y loggea el shutdown."""
    logger.info(
        "Iniciando CICOR Operations API",
        # # #extra={"event": "startup", "module": "operations"},
        extra={"event": "startup", "service_module": "operations"},
    )
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(_CREATE_TABLE_SQL)
    logger.info("Tabla 'processes' verificada/creada", extra={"event": "db_init"})

    yield  # ← la aplicación corre aquí

    logger.info(
        "Deteniendo CICOR Operations API",
        # # #extra={"event": "shutdown", "module": "operations"},
        extra={"event": "shutdown", "service_module": "operations"},
    )


# ── Aplicación FastAPI ─────────────────────────────────────────────────────────
app = FastAPI(
    title="CICOR Operations API",
    description="Módulo Operaciones - Gestión de Procesos Operacionales",
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
    return {"status": "alive", "service": "operations-api"}


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
    return {"status": "ready", "service": "operations-api"}


@app.get(
    "/health/startup",
    tags=["health"],
    summary="Startup probe",
    description="Kubernetes Startup: verifica que el arranque completó.",
)
async def startup_probe():
    return {"status": "started", "service": "operations-api"}


# ── Info del módulo ────────────────────────────────────────────────────────────

@app.get(
    "/api/operations/info",
    tags=["info"],
    summary="Información del módulo Operaciones",
)
async def module_info():
    return {
        "module": "Operaciones",
        "color": "#F97316",
        "version": "1.0.0",
        "description": "Gestión de procesos operacionales",
        "endpoints": ["/api/operations/processes"],
        "status": "active",
        "crud_activo": ["Procesos"],
        "crud_deshabilitado": [
            "Asignar Tareas",
            "Registrar Avance",
            "Reportes de Desempeño",
            "Notificaciones de Deadline",
        ],
    }


# ── CRUD Procesos ──────────────────────────────────────────────────────────────

@app.get(
    "/api/operations/processes",
    response_model=List[dict],
    tags=["processes"],
    summary="Listar todos los procesos",
)
async def get_processes():
    """Retorna todos los procesos ordenados por fecha de creación (más reciente primero)."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM processes ORDER BY created_at DESC"
            )
            cols = [desc[0] for desc in cur.description]
            rows = [dict(zip(cols, row)) for row in cur.fetchall()]

    logger.info(
        f"Listados {len(rows)} procesos",
        extra={"event": "list_processes", "count": len(rows)},
    )
    return rows


@app.post(
    "/api/operations/processes",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    tags=["processes"],
    summary="Crear un nuevo proceso",
)
async def create_process(process: ProcessCreate):
    """
    Crea un nuevo proceso operacional.

    - **process_name**: Nombre descriptivo del proceso (requerido).
    - **owner**: Responsable del proceso.
    - **start_date**: Fecha de inicio (YYYY-MM-DD, requerida).
    - **expected_end_date**: Fecha esperada de fin (debe ser posterior a start_date).
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO processes
                    (process_name, description, owner, start_date, expected_end_date)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    process.process_name,
                    process.description,
                    process.owner,
                    process.start_date,
                    process.expected_end_date,
                ),
            )
            cols = [desc[0] for desc in cur.description]
            row = dict(zip(cols, cur.fetchone()))

    logger.info(
        f"Proceso creado: id={row['id']}",
        extra={"event": "create_process", "process_id": row["id"], "name": row["process_name"]},
    )
    return row


@app.put(
    "/api/operations/processes/{process_id}",
    response_model=dict,
    tags=["processes"],
    summary="Actualizar un proceso existente",
)
async def update_process(process_id: int, process: ProcessUpdate):
    """
    Actualiza los campos indicados de un proceso.
    Solo se modifican los campos que se envíen en el body.

    Si se envía `actual_end_date`, el `status` debe ser `COMPLETED`.
    """
    updates = {k: v for k, v in process.model_dump().items() if v is not None}

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron campos para actualizar",
        )

    # Auto-completar actual_end_date si status pasa a COMPLETED
    if updates.get("status") == ProcessStatus.COMPLETED and "actual_end_date" not in updates:
        updates["actual_end_date"] = datetime.utcnow().date()

    updates["updated_at"] = datetime.utcnow()

    set_clause = ", ".join([f"{col} = %s" for col in updates])
    values = list(updates.values()) + [process_id]

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE processes SET {set_clause} WHERE id = %s RETURNING *",
                values,
            )
            if cur.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Proceso con id={process_id} no encontrado",
                )
            cols = [desc[0] for desc in cur.description]
            row = dict(zip(cols, cur.fetchone()))

    logger.info(
        f"Proceso actualizado: id={process_id}",
        extra={
            "event": "update_process",
            "process_id": process_id,
            "fields_updated": list(updates.keys()),
        },
    )
    return row


@app.delete(
    "/api/operations/processes/{process_id}",
    tags=["processes"],
    summary="Eliminar un proceso",
)
async def delete_process(process_id: int):
    """Elimina permanentemente un proceso por su ID."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM processes WHERE id = %s RETURNING id",
                (process_id,),
            )
            if cur.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Proceso con id={process_id} no encontrado",
                )

    logger.info(
        f"Proceso eliminado: id={process_id}",
        extra={"event": "delete_process", "process_id": process_id},
    )
    return {"message": f"Proceso {process_id} eliminado exitosamente"}
