"""
CICOR ERP - Operations API
Schemas Pydantic para validación de datos del módulo Operaciones.

Entidad principal: Process (Procesos Operacionales)
"""

from datetime import date
from enum import StrEnum

from pydantic import BaseModel
from pydantic import Field
from pydantic import model_validator

# ── Enumerados ────────────────────────────────────────────────────────────────

class ProcessStatus(StrEnum):
    PLANNING    = "PLANNING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED   = "COMPLETED"
    ON_HOLD     = "ON_HOLD"


# ── Schemas de entrada ────────────────────────────────────────────────────────

class ProcessCreate(BaseModel):
    """Schema para crear un nuevo proceso operacional."""

    process_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Nombre del proceso",
        examples=["Cadena de Suministro Q1"],
    )
    description: str | None = Field(
        None,
        description="Descripción detallada del proceso",
    )
    owner: str | None = Field(
        None,
        max_length=255,
        description="Responsable del proceso",
        examples=["Juan Gerente"],
    )
    start_date: date = Field(
        ...,
        description="Fecha de inicio del proceso (YYYY-MM-DD)",
    )
    expected_end_date: date | None = Field(
        None,
        description="Fecha esperada de finalización (YYYY-MM-DD)",
    )

    @model_validator(mode="after")
    def validate_dates(self) -> "ProcessCreate":
        """Verifica que expected_end_date sea posterior a start_date."""
        if self.expected_end_date and self.expected_end_date < self.start_date:
            raise ValueError(
                "La fecha de fin esperada no puede ser anterior a la fecha de inicio"
            )
        return self


class ProcessUpdate(BaseModel):
    """Schema para actualizar un proceso existente (todos los campos opcionales)."""

    process_name: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="Nuevo nombre del proceso",
    )
    description: str | None = Field(
        None,
        description="Nueva descripción",
    )
    owner: str | None = Field(
        None,
        max_length=255,
        description="Nuevo responsable",
    )
    status: ProcessStatus | None = Field(
        None,
        description="Nuevo estado del proceso",
    )
    start_date: date | None = Field(
        None,
        description="Nueva fecha de inicio",
    )
    expected_end_date: date | None = Field(
        None,
        description="Nueva fecha esperada de finalización",
    )
    actual_end_date: date | None = Field(
        None,
        description="Fecha real de finalización (solo cuando status=COMPLETED)",
    )

    @model_validator(mode="after")
    def validate_actual_end_date(self) -> "ProcessUpdate":
        """Si se provee actual_end_date, el status debe ser COMPLETED."""
        if self.actual_end_date and self.status not in (None, ProcessStatus.COMPLETED):
            raise ValueError(
                "actual_end_date solo aplica cuando status es COMPLETED"
            )
        return self


# ── Schema de respuesta ───────────────────────────────────────────────────────

class ProcessResponse(BaseModel):
    """Schema de respuesta para un proceso (lo que retorna la API)."""

    id: int
    process_name: str
    description: str | None
    owner: str | None
    status: str
    start_date: date
    expected_end_date: date | None
    actual_end_date: date | None

    class Config:
        from_attributes = True
