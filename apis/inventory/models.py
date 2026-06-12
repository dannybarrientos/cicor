# ============================================================
# CICOR ERP - Inventory API | models.py
# Descripción: Schemas Pydantic v2 para validación de entrada
#              y serialización de salida del módulo Inventario.
#              Refleja la tabla `products` de PostgreSQL y el
#              endpoint especial POST /api/inventory/reserve.
# ============================================================

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, model_validator


# ── Schema de entrada: Crear producto ────────────────────────
class ProductCreate(BaseModel):
    """Payload para POST /api/inventory/products."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        examples=["Laptop Dell XPS 15"],
    )
    sku: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Código único de producto (SKU)",
        examples=["LAP-DELL-XPS15-001"],
    )
    description: Optional[str] = Field(
        None,
        description="Descripción detallada del producto",
        examples=["Laptop de alto rendimiento con procesador Intel Core i9"],
    )
    category: Optional[str] = Field(
        None,
        max_length=100,
        examples=["Electrónica"],
    )
    stock_quantity: int = Field(
        default=0,
        ge=0,
        description="Cantidad inicial en stock",
        examples=[50],
    )
    reorder_level: int = Field(
        default=10,
        ge=0,
        description="Nivel mínimo de stock para reorden",
        examples=[10],
    )
    unit_price: Decimal = Field(
        ...,
        gt=0,
        # # #decimal_places=2,
        description="Precio unitario del producto",
        examples=[1299.99],
    )


# ── Schema de entrada: Actualizar producto ───────────────────
class ProductUpdate(BaseModel):
    """Payload para PUT /api/inventory/products/{id}.
    Todos los campos son opcionales (actualización parcial)."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    stock_quantity: Optional[int] = Field(None, ge=0)
    reorder_level: Optional[int] = Field(None, ge=0)
    # # #unit_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    unit_price: Optional[Decimal] = Field(None, gt=0)

    @model_validator(mode="after")
    def at_least_one_field(self) -> "ProductUpdate":
        """Valida que al menos un campo sea enviado en el body."""
        if all(v is None for v in self.model_dump().values()):
            raise ValueError("Se debe enviar al menos un campo para actualizar")
        return self


# ── Schema de salida: Producto completo ──────────────────────
class ProductResponse(BaseModel):
    """Respuesta de la API para un producto (GET, POST, PUT).
    Corresponde 1:1 con las columnas de la tabla products."""

    id: int
    name: str
    sku: str
    description: Optional[str]
    category: Optional[str]
    stock_quantity: int
    reorder_level: int
    unit_price: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Schema: Endpoint especial /reserve ───────────────────────
class ReserveRequest(BaseModel):
    """Payload recibido desde el módulo Comercial.
    POST /api/inventory/reserve — Reduce stock temporalmente."""

    product_name: str = Field(
        ...,
        min_length=1,
        description="Nombre del producto a reservar (debe coincidir con products.name)",
        examples=["Laptop Dell XPS 15"],
    )
    quantity: int = Field(
        ...,
        gt=0,
        description="Cantidad a reservar/descontar del stock",
        examples=[5],
    )


class ReserveResponse(BaseModel):
    """Respuesta del endpoint POST /api/inventory/reserve.
    Consumida por la API Comercial para determinar el status de la venta."""

    success: bool = Field(
        ...,
        description="True si el stock fue reservado exitosamente",
    )
    remaining_stock: int = Field(
        ...,
        description="Stock restante después de la reserva (o stock actual si falló)",
    )
    message: str = Field(
        ...,
        description="Descripción del resultado de la operación",
    )


# ── Schemas: Respuestas genéricas ─────────────────────────────
class HealthResponse(BaseModel):
    """Respuesta de los endpoints /health/*."""

    status: str
    service: str = "cicor-inventory-api"
    db_connected: Optional[bool] = None


class InfoResponse(BaseModel):
    """Respuesta de GET /api/inventory/info."""

    module: str = "Inventario"
    version: str = "1.0.0"
    description: str = "Gestión de productos y stock. Recibe reservas del módulo Comercial."
    endpoints: list[str] = [
        "GET    /api/inventory/products",
        "POST   /api/inventory/products",
        "PUT    /api/inventory/products/{id}",
        "DELETE /api/inventory/products/{id}",
        "POST   /api/inventory/reserve  [llamado por Comercial]",
    ]


class ErrorResponse(BaseModel):
    """Respuesta de error estándar (4xx / 5xx)."""

    detail: str
