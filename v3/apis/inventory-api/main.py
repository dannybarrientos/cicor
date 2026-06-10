# ============================================================
# CICOR ERP - Inventory API | main.py
# Descripción: Punto de entrada FastAPI. Implementa el CRUD
#              completo de Productos (RF2) y el endpoint especial
#              POST /api/inventory/reserve, invocado por el
#              módulo Comercial al crear una venta.
# Puerto:      8000 (interno) / 8002 (host / Ingress)
# ============================================================

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Path, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from pythonjsonlogger import jsonlogger

from database import DatabasePool, check_db_health, get_db_cursor
from models import (
    ErrorResponse,
    HealthResponse,
    InfoResponse,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    ReserveRequest,
    ReserveResponse,
)

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

logger = logging.getLogger("cicor-inventory-api")


# ── Lifespan: arranque y apagado de la app ───────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa el pool de BD al arrancar y lo cierra al apagar."""
    logger.info("Iniciando cicor-inventory-api...")
    DatabasePool.init(retries=5, delay=3)
    yield
    logger.info("Apagando cicor-inventory-api...")
    DatabasePool.close()


# ── Aplicación FastAPI ────────────────────────────────────────
app = FastAPI(
    title="CICOR ERP - Módulo Inventario",
    description=(
        "API de gestión de productos y stock. "
        "Expone POST /api/inventory/reserve para el módulo Comercial."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://cicor.local"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Prometheus ────────────────────────────────────────────────
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

@app.get("/api/inventory/info", response_model=InfoResponse, tags=["Info"])
def get_info():
    """Información general del módulo Inventario."""
    return InfoResponse()


# ══════════════════════════════════════════════════════════════
# CRUD: PRODUCTOS
# ══════════════════════════════════════════════════════════════

@app.get(
    "/api/inventory/products",
    response_model=list[ProductResponse],
    tags=["Productos"],
    summary="Listar todos los productos",
)
def get_products():
    """GET /api/inventory/products — Retorna la lista completa de productos."""
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id, name, sku, description, category,
                   stock_quantity, reorder_level, unit_price,
                   created_at, updated_at
            FROM products
            ORDER BY name ASC
            """
        )
        rows = cursor.fetchall()

    logger.info(f"GET /api/inventory/products → {len(rows)} registros")
    return [ProductResponse(**dict(row)) for row in rows]


@app.post(
    "/api/inventory/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Productos"],
    summary="Crear un nuevo producto",
    responses={409: {"model": ErrorResponse}},
)
def create_product(product: ProductCreate):
    """POST /api/inventory/products — Crea un producto con SKU único."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO products
                    (name, sku, description, category,
                     stock_quantity, reorder_level, unit_price)
                VALUES
                    (%(name)s, %(sku)s, %(description)s, %(category)s,
                     %(stock_quantity)s, %(reorder_level)s, %(unit_price)s)
                RETURNING id, name, sku, description, category,
                          stock_quantity, reorder_level, unit_price,
                          created_at, updated_at
                """,
                {
                    "name": product.name,
                    "sku": product.sku,
                    "description": product.description,
                    "category": product.category,
                    "stock_quantity": product.stock_quantity,
                    "reorder_level": product.reorder_level,
                    "unit_price": str(product.unit_price),
                },
            )
            new_product = cursor.fetchone()
    except Exception as exc:
        # SKU duplicado (UNIQUE constraint) → 409 Conflict
        if "unique" in str(exc).lower() or "duplicate" in str(exc).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un producto con SKU '{product.sku}'",
            )
        raise

    logger.info(f"Producto creado id={new_product['id']} sku={product.sku}")
    return ProductResponse(**dict(new_product))


@app.put(
    "/api/inventory/products/{product_id}",
    response_model=ProductResponse,
    tags=["Productos"],
    summary="Actualizar un producto existente",
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
def update_product(
    product_id: int = Path(..., gt=0, description="ID del producto"),
    product: ProductUpdate = ...,
):
    """PUT /api/inventory/products/{id} — Actualización parcial de un producto."""
    updates = {k: v for k, v in product.model_dump().items() if v is not None}
    set_clause = ", ".join([f"{col} = %({col})s" for col in updates.keys()])
    set_clause += ", updated_at = NOW()"
    updates["product_id"] = product_id

    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                f"""
                UPDATE products
                SET {set_clause}
                WHERE id = %(product_id)s
                RETURNING id, name, sku, description, category,
                          stock_quantity, reorder_level, unit_price,
                          created_at, updated_at
                """,
                updates,
            )
            updated = cursor.fetchone()
    except Exception as exc:
        if "unique" in str(exc).lower() or "duplicate" in str(exc).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El SKU ya pertenece a otro producto",
            )
        raise

    if not updated:
        raise HTTPException(
            status_code=404,
            detail=f"Producto {product_id} no encontrado",
        )

    logger.info(f"Producto actualizado id={product_id}")
    return ProductResponse(**dict(updated))


@app.delete(
    "/api/inventory/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Productos"],
    summary="Eliminar un producto",
    responses={404: {"model": ErrorResponse}},
)
def delete_product(
    product_id: int = Path(..., gt=0, description="ID del producto"),
):
    """DELETE /api/inventory/products/{id} — Elimina permanentemente un producto."""
    with get_db_cursor() as cursor:
        cursor.execute(
            "DELETE FROM products WHERE id = %(product_id)s RETURNING id",
            {"product_id": product_id},
        )
        deleted = cursor.fetchone()

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Producto {product_id} no encontrado",
        )

    logger.info(f"Producto eliminado id={product_id}")
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)


# ══════════════════════════════════════════════════════════════
# ENDPOINT ESPECIAL: RESERVA DE STOCK
# Llamado internamente por la API Comercial al crear una venta.
# NetworkPolicy: solo acepta requests desde cicor-commercial.
# ══════════════════════════════════════════════════════════════

@app.post(
    "/api/inventory/reserve",
    response_model=ReserveResponse,
    tags=["Reserva"],
    summary="Reservar stock (llamado por módulo Comercial)",
    description=(
        "Reduce temporalmente el stock del producto indicado. "
        "Si no hay stock suficiente devuelve success=false sin modificar la BD. "
        "Este endpoint es consumido exclusivamente por cicor-commercial-api."
    ),
)
def reserve_stock(reserve: ReserveRequest):
    """POST /api/inventory/reserve

    Flujo:
    1. Buscar el producto por nombre (match exacto, case-insensitive).
    2. Verificar stock_quantity >= quantity solicitada.
    3. Si hay stock: descontar y devolver success=True + remaining_stock.
    4. Si no hay stock: devolver success=False + stock actual sin modificar BD.
    5. Si el producto no existe: devolver success=False con mensaje claro.
    """
    with get_db_cursor() as cursor:
        # Paso 1: buscar producto por nombre
        cursor.execute(
            """
            SELECT id, name, stock_quantity
            FROM products
            WHERE LOWER(name) = LOWER(%(product_name)s)
            LIMIT 1
            """,
            {"product_name": reserve.product_name},
        )
        product = cursor.fetchone()

        # Producto no encontrado
        if not product:
            logger.warning(
                f"RESERVE: producto no encontrado → '{reserve.product_name}'"
            )
            return ReserveResponse(
                success=False,
                remaining_stock=0,
                message=f"Producto '{reserve.product_name}' no encontrado en inventario",
            )

        current_stock = product["stock_quantity"]

        # Paso 2: verificar stock suficiente
        if current_stock < reserve.quantity:
            logger.warning(
                f"RESERVE: stock insuficiente → "
                f"product_id={product['id']} "
                f"disponible={current_stock} solicitado={reserve.quantity}"
            )
            return ReserveResponse(
                success=False,
                remaining_stock=current_stock,
                message=(
                    f"Stock insuficiente para '{reserve.product_name}'. "
                    f"Disponible: {current_stock}, solicitado: {reserve.quantity}"
                ),
            )

        # Paso 3: descontar stock
        new_stock = current_stock - reserve.quantity
        cursor.execute(
            """
            UPDATE products
            SET stock_quantity = %(new_stock)s,
                updated_at = NOW()
            WHERE id = %(product_id)s
            """,
            {"new_stock": new_stock, "product_id": product["id"]},
        )

    logger.info(
        f"RESERVE: stock reservado → "
        f"product_id={product['id']} "
        f"cantidad={reserve.quantity} "
        f"stock_restante={new_stock}"
    )
    return ReserveResponse(
        success=True,
        remaining_stock=new_stock,
        message=f"Stock reservado exitosamente. Restante: {new_stock} unidades",
    )


# ── Handler global de errores no controlados ─────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Error no controlado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Error interno del servidor"},
    )
