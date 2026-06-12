# ============================================================
# CICOR ERP - Commercial API | models.py
# Descripción: Schemas Pydantic v2 para validación de entrada
#              y serialización de salida del módulo Comercial.
#              Refleja exactamente la tabla `sales` de PostgreSQL
#              y los RF definidos en el spec del proyecto.
# ============================================================

from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel
from pydantic import Field
from pydantic import computed_field
from pydantic import model_validator


# ── Enumeraciones ─────────────────────────────────────────────
class SaleStatus(StrEnum):
    """Estados posibles de una venta (RF1)."""
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    PENDING_INVENTORY = "PENDING_INVENTORY"   # Creada pero sin stock reservado


# ── Schema de entrada: Crear venta ───────────────────────────
class SaleCreate(BaseModel):
    """Payload para POST /api/commercial/sales.
    total_amount se calcula automáticamente: quantity × unit_price."""

    product_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        examples=["Laptop Dell XPS 15"],
    )
    quantity: int = Field(
        ...,
        gt=0,
        description="Cantidad de unidades (debe ser mayor a 0)",
        examples=[5],
    )
    unit_price: Decimal = Field(
        ...,
        gt=0,
        # # #decimal_places=2,
        description="Precio unitario en la moneda local",
        examples=[500.00],
    )
    customer_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        examples=["Acme Corp"],
    )

    @computed_field
    @property
    def total_amount(self) -> Decimal:
        """Calculado automáticamente a partir de quantity × unit_price."""
        return round(Decimal(str(self.quantity)) * self.unit_price, 2)


# ── Schema de entrada: Actualizar venta ──────────────────────
class SaleUpdate(BaseModel):
    """Payload para PUT /api/commercial/sales/{id}.
    Todos los campos son opcionales (actualización parcial)."""

    product_name: str | None = Field(
        None, min_length=1, max_length=255
    )
    quantity: int | None = Field(None, gt=0)
    # # #unit_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    unit_price: Decimal | None = Field(None, gt=0)
    customer_name: str | None = Field(None, min_length=1, max_length=255)
    status: SaleStatus | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "SaleUpdate":
        """Valida que al menos un campo sea enviado en el body."""
        if all(v is None for v in self.model_dump().values()):
            raise ValueError("Se debe enviar al menos un campo para actualizar")
        return self


# ── Schema de salida: Venta completa ─────────────────────────
class SaleResponse(BaseModel):
    """Respuesta de la API para una venta (GET, POST, PUT).
    Corresponde 1:1 con las columnas de la tabla sales."""

    id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    total_amount: Decimal
    customer_name: str
    sale_date: datetime
    status: SaleStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Schema: Payload hacia Inventario (interacción especial) ──
class InventoryReserveRequest(BaseModel):
    """Payload que Comercial envía a POST /api/inventory/reserve
    al crear una venta (RF1 - Interacción con Inventario)."""

    product_name: str
    quantity: int


class InventoryReserveResponse(BaseModel):
    """Respuesta de la API de Inventario al reservar stock."""

    success: bool
    remaining_stock: int
    message: str


# ── Schema: Respuestas genéricas ─────────────────────────────
class HealthResponse(BaseModel):
    """Respuesta de los endpoints /health/*."""

    status: str
    service: str = "cicor-commercial-api"
    db_connected: bool | None = None


class InfoResponse(BaseModel):
    """Respuesta de GET /api/commercial/info."""

    module: str = "Comercial"
    version: str = "1.0.0"
    description: str = "Gestión de ventas y relación con inventario"
    endpoints: list[str] = [
        "GET  /api/commercial/sales",
        "POST /api/commercial/sales",
        "PUT  /api/commercial/sales/{id}",
        "DELETE /api/commercial/sales/{id}",
    ]


class ErrorResponse(BaseModel):
    """Respuesta de error estándar (4xx / 5xx)."""

    detail: str
