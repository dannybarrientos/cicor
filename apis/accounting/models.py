# ============================================================
# CICOR ERP - Accounting API | models.py
# Descripción: Schemas Pydantic v2 para validación de entrada
#              y serialización de salida del módulo Contabilidad.
#              Refleja la tabla `accounting_entries` con la
#              restricción contable: debit XOR credit (nunca ambos,
#              nunca ninguno) — replica el CHECK constraint de la BD.
# ============================================================

from datetime import date
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel
from pydantic import Field
from pydantic import model_validator


# ── Enumeraciones ─────────────────────────────────────────────
class EntryStatus(StrEnum):
    """Estados del asiento contable (RF3)."""
    DRAFT = "DRAFT"           # Borrador, aún editable
    POSTED = "POSTED"         # Publicado, contabilizado en el período
    REVERSED = "REVERSED"     # Revertido mediante asiento contrario


# ── Schema de entrada: Crear asiento ─────────────────────────
class EntryCreate(BaseModel):
    """Payload para POST /api/accounting/entries.

    Regla de negocio contable:
      - Se debe indicar EXACTAMENTE uno de los dos: debit o credit.
      - No pueden ser ambos nulos ni estar ambos presentes.
      - Refleja el CHECK constraint de la tabla accounting_entries.
    """

    account_code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Código de cuenta contable (ej: 1100, 4000)",
        examples=["1100"],
    )
    account_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Nombre de la cuenta contable",
        examples=["Caja y Bancos"],
    )
    debit: Decimal | None = Field(
        None,
        gt=0,
        # # #decimal_places=2,
        description="Monto al débito. Exclusivo con 'credit'.",
        examples=[1500.00],
    )
    credit: Decimal | None = Field(
        None,
        gt=0,
        # # #decimal_places=2,
        description="Monto al crédito. Exclusivo con 'debit'.",
        examples=[None],
    )
    description: str | None = Field(
        None,
        description="Descripción o concepto del asiento",
        examples=["Cobro de factura #001 al cliente Acme Corp"],
    )
    entry_date: date = Field(
        ...,
        description="Fecha contable del asiento (YYYY-MM-DD)",
        examples=["2025-06-01"],
    )

    @model_validator(mode="after")
    def validate_debit_xor_credit(self) -> "EntryCreate":
        """Valida que debit y credit sean mutuamente excluyentes
        (exactamente uno de los dos debe estar presente)."""
        has_debit = self.debit is not None
        has_credit = self.credit is not None

        if has_debit and has_credit:
            raise ValueError(
                "Un asiento no puede tener débito Y crédito simultáneamente. "
                "Indique solo uno de los dos."
            )
        if not has_debit and not has_credit:
            raise ValueError(
                "Debe indicar exactamente uno: 'debit' o 'credit'. Ninguno fue enviado."
            )
        return self


# ── Schema de entrada: Actualizar asiento ────────────────────
class EntryUpdate(BaseModel):
    """Payload para PUT /api/accounting/entries/{id}.
    Todos los campos son opcionales, pero si se envían debit/credit
    se mantiene la restricción XOR."""

    account_code: str | None = Field(None, min_length=1, max_length=50)
    account_name: str | None = Field(None, min_length=1, max_length=255)
    # # #debit: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    debit: Decimal | None = Field(None, gt=0)
    credit: Decimal | None = Field(None, gt=0)
    # # #credit: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    description: str | None = None
    entry_date: date | None = None
    status: EntryStatus | None = None

    @model_validator(mode="after")
    def validate_update_constraints(self) -> "EntryUpdate":
        """Valida que si se envían ambos (debit y credit), sean mutuamente
        excluyentes, y que al menos un campo sea diferente de None."""
        if all(v is None for v in self.model_dump().values()):
            raise ValueError("Se debe enviar al menos un campo para actualizar")

        if self.debit is not None and self.credit is not None:
            raise ValueError(
                "Un asiento no puede tener débito Y crédito simultáneamente."
            )
        return self


# ── Schema de salida: Asiento completo ───────────────────────
class EntryResponse(BaseModel):
    """Respuesta de la API para un asiento contable.
    Corresponde 1:1 con las columnas de la tabla accounting_entries."""

    id: int
    account_code: str
    account_name: str
    debit: Decimal | None
    credit: Decimal | None
    description: str | None
    entry_date: date
    status: EntryStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Schemas: Respuestas genéricas ─────────────────────────────
class HealthResponse(BaseModel):
    status: str
    service: str = "cicor-accounting-api"
    db_connected: bool | None = None


class InfoResponse(BaseModel):
    module: str = "Contabilidad"
    version: str = "1.0.0"
    description: str = (
        "Registro de asientos contables. "
        "Regla: cada asiento tiene débito XOR crédito (nunca ambos)."
    )
    endpoints: list[str] = [
        "GET    /api/accounting/entries",
        "POST   /api/accounting/entries",
        "PUT    /api/accounting/entries/{id}",
        "DELETE /api/accounting/entries/{id}",
    ]


class ErrorResponse(BaseModel):
    detail: str
