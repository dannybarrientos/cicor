# ============================================================
# CICOR ERP - Commercial API | main.py
# Descripción: Punto de entrada FastAPI. Implementa el CRUD
#              completo de Ventas (RF1) y la interacción
#              especial con el módulo de Inventario.
# Puerto:      8000 (interno) / 8001 (host / Ingress)
# ============================================================

import logging
import os
from contextlib import asynccontextmanager

import httpx
from database import DatabasePool
from database import check_db_health
from database import get_db_cursor
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Path
from fastapi import status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from models import ErrorResponse
from models import HealthResponse
from models import InfoResponse
from models import InventoryReserveRequest
from models import SaleCreate
from models import SaleResponse
from models import SaleUpdate
from prometheus_fastapi_instrumentator import Instrumentator
from pythonjsonlogger import jsonlogger

# ── Logging JSON estructurado ─────────────────────────────────
# Formato: {"timestamp": "...", "level": "...", "service": "...", "message": "..."}
log_handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
    rename_fields={"asctime": "timestamp", "levelname": "level", "name": "service"},
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
log_handler.setFormatter(formatter)
logging.root.handlers = [log_handler]
logging.root.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

logger = logging.getLogger("cicor-commercial-api")

# URL interna de la API de Inventario (inyectada via env var)
INVENTORY_API_URL = os.getenv("INVENTORY_API_URL", "http://inventory-api:8000")


# ── Lifespan: arranque y apagado de la app ───────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa el pool de BD al arrancar y lo cierra al apagar."""
    logger.info("Iniciando cicor-commercial-api...")
    DatabasePool.init(retries=5, delay=3)
    yield
    logger.info("Apagando cicor-commercial-api...")
    DatabasePool.close()


# ── Aplicación FastAPI ────────────────────────────────────────
app = FastAPI(
    title="CICOR ERP - Módulo Comercial",
    description="API de gestión de ventas con interacción al módulo de Inventario.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS (para desarrollo local con docker-compose) ───────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://cicor.local"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Prometheus: expone /metrics automáticamente ───────────────
Instrumentator().instrument(app).expose(app)


# ══════════════════════════════════════════════════════════════
# HEALTH CHECK ENDPOINTS
# Alineados con los probes de Kubernetes (spec sección 1.9)
# ══════════════════════════════════════════════════════════════

@app.get("/health/live", response_model=HealthResponse, tags=["Health"])
def health_live():
    """Liveness Probe: verifica que el proceso está vivo."""
    return HealthResponse(status="ok")


@app.get("/health/ready", response_model=HealthResponse, tags=["Health"])
def health_ready():
    """Readiness Probe: verifica que la BD está disponible."""
    db_ok = check_db_health()
    if not db_ok:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Base de datos no disponible",
        )
    return HealthResponse(status="ok", db_connected=True)


@app.get("/health/startup", response_model=HealthResponse, tags=["Health"])
def health_startup():
    """Startup Probe: verifica que la app completó su inicialización."""
    db_ok = check_db_health()
    if not db_ok:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Startup incompleto: BD no disponible",
        )
    return HealthResponse(status="ok", db_connected=True)


# ══════════════════════════════════════════════════════════════
# INFO ENDPOINT
# ══════════════════════════════════════════════════════════════

@app.get("/api/commercial/info", response_model=InfoResponse, tags=["Info"])
def get_info():
    """Información general del módulo Comercial."""
    return InfoResponse()


# ══════════════════════════════════════════════════════════════
# CRUD: VENTAS
# ══════════════════════════════════════════════════════════════

@app.get(
    "/api/commercial/sales",
    response_model=list[SaleResponse],
    tags=["Ventas"],
    summary="Listar todas las ventas",
)
def get_sales():
    """GET /api/commercial/sales — Retorna la lista completa de ventas."""
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id, product_name, quantity, unit_price, total_amount,
                   customer_name, sale_date, status, created_at, updated_at
            FROM sales
            ORDER BY sale_date DESC
            """
        )
        rows = cursor.fetchall()

    logger.info(f"GET /api/commercial/sales → {len(rows)} registros")
    return [SaleResponse(**dict(row)) for row in rows]


@app.post(
    "/api/commercial/sales",
    response_model=SaleResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Ventas"],
    summary="Crear una nueva venta",
    responses={503: {"model": ErrorResponse}},
)
async def create_sale(sale: SaleCreate):
    """POST /api/commercial/sales — Crea una venta y reserva stock en Inventario.

    Flujo (RF1 - Interacción con Inventario):
    1. Insertar la venta en BD con status PENDING.
    2. Llamar a POST /api/inventory/reserve.
    3. Si Inventario responde OK → status = CONFIRMED.
    4. Si Inventario falla → status = PENDING_INVENTORY (venta igual se crea).
    """
    # ── Paso 1: determinar status inicial según respuesta de Inventario ──
    final_status = "PENDING"
    inventory_ok = False

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            reserve_payload = InventoryReserveRequest(
                product_name=sale.product_name,
                quantity=sale.quantity,
            )
            response = await client.post(
                f"{INVENTORY_API_URL}/api/inventory/reserve",
                json=reserve_payload.model_dump(),
            )
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    final_status = "CONFIRMED"
                    inventory_ok = True
                else:
                    final_status = "PENDING_INVENTORY"
            else:
                final_status = "PENDING_INVENTORY"
    except httpx.RequestError as exc:
        logger.warning(f"Inventario no disponible al crear venta: {exc}")
        final_status = "PENDING_INVENTORY"

    logger.info(
        f"Reserva Inventario → ok={inventory_ok}, status asignado={final_status}"
    )

    # ── Paso 2: insertar la venta en BD ──────────────────────────────────
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO sales
                (product_name, quantity, unit_price, total_amount, customer_name, status)
            VALUES
                (%(product_name)s, %(quantity)s, %(unit_price)s,
                 %(total_amount)s, %(customer_name)s, %(status)s)
            RETURNING id, product_name, quantity, unit_price, total_amount,
                      customer_name, sale_date, status, created_at, updated_at
            """,
            {
                "product_name": sale.product_name,
                "quantity": sale.quantity,
                "unit_price": str(sale.unit_price),
                "total_amount": str(sale.total_amount),
                "customer_name": sale.customer_name,
                "status": final_status,
            },
        )
        new_sale = cursor.fetchone()

    logger.info(f"Venta creada id={new_sale['id']} status={final_status}")
    return SaleResponse(**dict(new_sale))


@app.put(
    "/api/commercial/sales/{sale_id}",
    response_model=SaleResponse,
    tags=["Ventas"],
    summary="Actualizar una venta existente",
    responses={404: {"model": ErrorResponse}},
)
def update_sale(
    sale_id: int = Path(..., gt=0, description="ID de la venta"),
    sale: SaleUpdate = ...,
):
    """PUT /api/commercial/sales/{id} — Actualización parcial de una venta."""
    # Construir dinámicamente solo los campos enviados
    updates = {k: v for k, v in sale.model_dump().items() if v is not None}
    set_clause = ", ".join(
        [f"{col} = %({col})s" for col in updates.keys()]
    )
    set_clause += ", updated_at = NOW()"
    updates["sale_id"] = sale_id

    # Recalcular total_amount si cambian quantity o unit_price
    if "quantity" in updates or "unit_price" in updates:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT quantity, unit_price FROM sales WHERE id = %(sale_id)s",
                {"sale_id": sale_id},
            )
            current = cursor.fetchone()
        if not current:
            raise HTTPException(status_code=404, detail=f"Venta {sale_id} no encontrada")
        qty = updates.get("quantity", current["quantity"])
        price = updates.get("unit_price", current["unit_price"])
        updates["total_amount"] = round(float(qty) * float(price), 2)
        set_clause += ", total_amount = %(total_amount)s"

    with get_db_cursor() as cursor:
        cursor.execute(
            f"""
            UPDATE sales
            SET {set_clause}
            WHERE id = %(sale_id)s
            RETURNING id, product_name, quantity, unit_price, total_amount,
                      customer_name, sale_date, status, created_at, updated_at
            """,
            updates,
        )
        updated = cursor.fetchone()

    if not updated:
        raise HTTPException(status_code=404, detail=f"Venta {sale_id} no encontrada")

    logger.info(f"Venta actualizada id={sale_id}")
    return SaleResponse(**dict(updated))


@app.delete(
    "/api/commercial/sales/{sale_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Ventas"],
    summary="Eliminar una venta",
    responses={404: {"model": ErrorResponse}},
)
def delete_sale(
    sale_id: int = Path(..., gt=0, description="ID de la venta"),
):
    """DELETE /api/commercial/sales/{id} — Elimina permanentemente una venta."""
    with get_db_cursor() as cursor:
        cursor.execute(
            "DELETE FROM sales WHERE id = %(sale_id)s RETURNING id",
            {"sale_id": sale_id},
        )
        deleted = cursor.fetchone()

    if not deleted:
        raise HTTPException(status_code=404, detail=f"Venta {sale_id} no encontrada")

    logger.info(f"Venta eliminada id={sale_id}")
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)


# ── Handler global de errores no controlados ─────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Error no controlado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Error interno del servidor"},
    )
