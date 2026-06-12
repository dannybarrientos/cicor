# ============================================================
# CICOR ERP - Accounting API | main.py
# Descripción: Punto de entrada FastAPI. Implementa el CRUD
#              completo de Asientos Contables (RF3).
#              Regla contable clave: debit XOR credit en cada
#              asiento (nunca ambos, nunca ninguno).
# Puerto:      8000 (interno) / 8003 (host / Ingress)
# ============================================================

import logging
import os
from contextlib import asynccontextmanager

from database import DatabasePool
from database import check_db_health
from database import get_db_cursor
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Path
from fastapi import status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from models import EntryCreate
from models import EntryResponse
from models import EntryUpdate
from models import ErrorResponse
from models import HealthResponse
from models import InfoResponse
from prometheus_fastapi_instrumentator import Instrumentator
from pythonjsonlogger import jsonlogger

# ── Logging JSON estructurado ─────────────────────────────────
log_handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
    rename_fields={"asctime": "timestamp", "levelname": "level", "name": "service"},
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
log_handler.setFormatter(formatter)
logging.root.handlers = [log_handler]
logging.root.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

logger = logging.getLogger("cicor-accounting-api")


# ── Lifespan ──────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando cicor-accounting-api...")
    DatabasePool.init(retries=5, delay=3)
    yield
    logger.info("Apagando cicor-accounting-api...")
    DatabasePool.close()


# ── Aplicación FastAPI ────────────────────────────────────────
app = FastAPI(
    title="CICOR ERP - Módulo Contabilidad",
    description=(
        "API de registro de asientos contables. "
        "Cada asiento tiene débito XOR crédito (nunca ambos simultáneamente)."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://cicor.local"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)


# ══════════════════════════════════════════════════════════════
# HEALTH CHECK ENDPOINTS
# ══════════════════════════════════════════════════════════════

@app.get("/health/live", response_model=HealthResponse, tags=["Health"])
def health_live():
    """Liveness Probe: verifica que el proceso está vivo."""
    return HealthResponse(status="ok")


@app.get("/health/ready", response_model=HealthResponse, tags=["Health"])
def health_ready():
    """Readiness Probe: verifica que la BD está disponible."""
    if not check_db_health():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Base de datos no disponible",
        )
    return HealthResponse(status="ok", db_connected=True)


@app.get("/health/startup", response_model=HealthResponse, tags=["Health"])
def health_startup():
    """Startup Probe: verifica que la app completó su inicialización."""
    if not check_db_health():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Startup incompleto: BD no disponible",
        )
    return HealthResponse(status="ok", db_connected=True)


# ══════════════════════════════════════════════════════════════
# INFO ENDPOINT
# ══════════════════════════════════════════════════════════════

@app.get("/api/accounting/info", response_model=InfoResponse, tags=["Info"])
def get_info():
    """Información general del módulo Contabilidad."""
    return InfoResponse()


# ══════════════════════════════════════════════════════════════
# CRUD: ASIENTOS CONTABLES
# Tabla: accounting_entries
# Restricción: CHECK (debit IS NOT NULL OR credit IS NOT NULL)
#              AND NOT (debit IS NOT NULL AND credit IS NOT NULL)
# ══════════════════════════════════════════════════════════════

@app.get(
    "/api/accounting/entries",
    response_model=list[EntryResponse],
    tags=["Asientos Contables"],
    summary="Listar todos los asientos contables",
)
def get_entries():
    """GET /api/accounting/entries — Retorna todos los asientos ordenados
    por fecha descendente (más recientes primero)."""
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id, account_code, account_name, debit, credit,
                   description, entry_date, status, created_at, updated_at
            FROM accounting_entries
            ORDER BY entry_date DESC, created_at DESC
            """
        )
        rows = cursor.fetchall()

    logger.info(f"GET /api/accounting/entries → {len(rows)} registros")
    return [EntryResponse(**dict(row)) for row in rows]


@app.post(
    "/api/accounting/entries",
    response_model=EntryResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Asientos Contables"],
    summary="Crear un nuevo asiento contable",
    responses={422: {"model": ErrorResponse}},
)
def create_entry(entry: EntryCreate):
    """POST /api/accounting/entries — Crea un asiento contable.

    La validación debit XOR credit se aplica en dos capas:
      1. Schema Pydantic (modelo EntryCreate) — antes de llegar a la BD.
      2. CHECK constraint en PostgreSQL — segunda línea de defensa.
    """
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO accounting_entries
                (account_code, account_name, debit, credit,
                 description, entry_date)
            VALUES
                (%(account_code)s, %(account_name)s, %(debit)s, %(credit)s,
                 %(description)s, %(entry_date)s)
            RETURNING id, account_code, account_name, debit, credit,
                      description, entry_date, status, created_at, updated_at
            """,
            {
                "account_code": entry.account_code,
                "account_name": entry.account_name,
                "debit": str(entry.debit) if entry.debit is not None else None,
                "credit": str(entry.credit) if entry.credit is not None else None,
                "description": entry.description,
                "entry_date": entry.entry_date.isoformat(),
            },
        )
        new_entry = cursor.fetchone()

    side = "DEBIT" if new_entry["debit"] else "CREDIT"
    amount = new_entry["debit"] or new_entry["credit"]
    logger.info(
        f"Asiento creado id={new_entry['id']} "
        f"account={entry.account_code} "
        f"side={side} amount={amount}"
    )
    return EntryResponse(**dict(new_entry))


@app.put(
    "/api/accounting/entries/{entry_id}",
    response_model=EntryResponse,
    tags=["Asientos Contables"],
    summary="Actualizar un asiento contable",
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def update_entry(
    entry_id: int = Path(..., gt=0, description="ID del asiento contable"),
    entry: EntryUpdate = ...,
):
    """PUT /api/accounting/entries/{id} — Actualización parcial de un asiento.

    Restricciones aplicadas:
      - No se puede actualizar un asiento con status POSTED o REVERSED
        directamente (debe reversarse con un asiento contrario).
      - Si se envía debit, se anula credit automáticamente (y viceversa)
        para mantener la restricción XOR.
    """
    # Verificar que el asiento existe y obtener su status actual
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT id, status FROM accounting_entries WHERE id = %(entry_id)s",
            {"entry_id": entry_id},
        )
        current = cursor.fetchone()

    if not current:
        raise HTTPException(
            status_code=404,
            detail=f"Asiento contable {entry_id} no encontrado",
        )

    # No permitir editar asientos ya publicados o revertidos
    if current["status"] in ("POSTED", "REVERSED"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"El asiento {entry_id} tiene status '{current['status']}' "
                f"y no puede ser modificado. Use un asiento de reversión."
            ),
        )

    # Construir SET clause dinámicamente con campos no nulos
    updates = {k: v for k, v in entry.model_dump().items() if v is not None}

    # Si se actualiza debit → limpiar credit en la BD (y viceversa)
    if "debit" in updates:
        updates["credit"] = None
    elif "credit" in updates:
        updates["debit"] = None

    # Convertir Decimal a str para psycopg2
    for field in ("debit", "credit", "unit_price"):
        if field in updates and updates[field] is not None:
            updates[field] = str(updates[field])

    # Convertir date a isoformat
    if "entry_date" in updates and updates["entry_date"] is not None:
        updates["entry_date"] = updates["entry_date"].isoformat()

    set_clause = ", ".join([f"{col} = %({col})s" for col in updates.keys()])
    set_clause += ", updated_at = NOW()"
    updates["entry_id"] = entry_id

    with get_db_cursor() as cursor:
        cursor.execute(
            f"""
            UPDATE accounting_entries
            SET {set_clause}
            WHERE id = %(entry_id)s
            RETURNING id, account_code, account_name, debit, credit,
                      description, entry_date, status, created_at, updated_at
            """,
            updates,
        )
        updated = cursor.fetchone()

    logger.info(f"Asiento actualizado id={entry_id}")
    return EntryResponse(**dict(updated))


@app.delete(
    "/api/accounting/entries/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Asientos Contables"],
    summary="Eliminar un asiento contable",
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
def delete_entry(
    entry_id: int = Path(..., gt=0, description="ID del asiento contable"),
):
    """DELETE /api/accounting/entries/{id} — Elimina un asiento.

    Solo se pueden eliminar asientos en status DRAFT.
    Los asientos POSTED o REVERSED deben reversarse contablemente,
    no eliminarse.
    """
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT id, status FROM accounting_entries WHERE id = %(entry_id)s",
            {"entry_id": entry_id},
        )
        current = cursor.fetchone()

    if not current:
        raise HTTPException(
            status_code=404,
            detail=f"Asiento contable {entry_id} no encontrado",
        )

    if current["status"] in ("POSTED", "REVERSED"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"El asiento {entry_id} tiene status '{current['status']}' "
                f"y no puede eliminarse. Solo los asientos DRAFT son eliminables."
            ),
        )

    with get_db_cursor() as cursor:
        cursor.execute(
            "DELETE FROM accounting_entries WHERE id = %(entry_id)s RETURNING id",
            {"entry_id": entry_id},
        )

    logger.info(f"Asiento eliminado id={entry_id}")
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)


# ── Handler global de errores no controlados ─────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Error no controlado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Error interno del servidor"},
    )
