"""
CICOR ERP - HR API (Recursos Humanos)
Schemas Pydantic para validación de datos del módulo RRHH.

Entidad principal: Employee (Empleados)

Estados posibles:
  ACTIVE   → Empleado activo
  INACTIVE → Empleado inactivo / desvinculado
  ON_LEAVE → Empleado en licencia / permiso
"""

import re
from datetime import date
from enum import StrEnum

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field
from pydantic import field_validator

# ── Enumerados ────────────────────────────────────────────────────────────────

class EmployeeStatus(StrEnum):
    ACTIVE   = "ACTIVE"
    INACTIVE = "INACTIVE"
    ON_LEAVE = "ON_LEAVE"


# ── Schemas de entrada ────────────────────────────────────────────────────────

class EmployeeCreate(BaseModel):
    """Schema para registrar un nuevo empleado."""

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Nombre completo del empleado",
        examples=["Jane Smith"],
    )
    email: EmailStr = Field(
        ...,
        description="Correo electrónico corporativo (debe ser único)",
        examples=["jane.smith@cicor.com"],
    )
    phone: str | None = Field(
        None,
        max_length=20,
        description="Número de teléfono (formato libre)",
        examples=["+573001234567"],
    )
    position: str | None = Field(
        None,
        max_length=255,
        description="Cargo o título del empleado",
        examples=["Senior Developer"],
    )
    department: str | None = Field(
        None,
        max_length=255,
        description="Área o departamento",
        examples=["Engineering"],
    )
    hire_date: date = Field(
        ...,
        description="Fecha de contratación (YYYY-MM-DD)",
    )
    salary: float | None = Field(
        None,
        ge=0,
        description="Salario en la moneda local (>= 0)",
        examples=[120000.00],
    )

    @field_validator("full_name")
    @classmethod
    def name_must_have_two_parts(cls, v: str) -> str:
        """Valida que el nombre tenga al menos nombre y apellido."""
        parts = v.strip().split()
        if len(parts) < 2:
            raise ValueError("El nombre completo debe incluir nombre y apellido")
        return v.strip()

    @field_validator("phone")
    @classmethod
    def phone_format(cls, v: str | None) -> str | None:
        """Acepta formatos internacionales básicos: +57 300 123 4567, etc."""
        if v is None:
            return v
        cleaned = re.sub(r"[\s\-\(\)]", "", v)
        if not re.match(r"^\+?[0-9]{7,15}$", cleaned):
            raise ValueError(
                "Formato de teléfono inválido. Use dígitos, +, espacios o guiones"
            )
        return v

    @field_validator("hire_date")
    @classmethod
    def hire_date_not_future(cls, v: date) -> date:
        """La fecha de contratación no puede ser en el futuro."""
        if v > date.today():
            raise ValueError("La fecha de contratación no puede ser futura")
        return v


class EmployeeUpdate(BaseModel):
    """
    Schema para actualizar un empleado existente.
    Todos los campos son opcionales; solo se modifican los enviados.
    """

    full_name: str | None = Field(
        None,
        min_length=2,
        max_length=255,
        description="Nuevo nombre completo",
    )
    email: EmailStr | None = Field(
        None,
        description="Nuevo email corporativo (debe ser único en la BD)",
    )
    phone: str | None = Field(
        None,
        max_length=20,
        description="Nuevo teléfono",
    )
    position: str | None = Field(
        None,
        max_length=255,
        description="Nuevo cargo",
    )
    department: str | None = Field(
        None,
        max_length=255,
        description="Nuevo departamento",
    )
    hire_date: date | None = Field(
        None,
        description="Nueva fecha de contratación",
    )
    salary: float | None = Field(
        None,
        ge=0,
        description="Nuevo salario (>= 0)",
    )
    status: EmployeeStatus | None = Field(
        None,
        description="Nuevo estado del empleado",
    )

    @field_validator("phone")
    @classmethod
    def phone_format(cls, v: str | None) -> str | None:
        if v is None:
            return v
        cleaned = re.sub(r"[\s\-\(\)]", "", v)
        if not re.match(r"^\+?[0-9]{7,15}$", cleaned):
            raise ValueError("Formato de teléfono inválido")
        return v


# ── Schema de respuesta ───────────────────────────────────────────────────────

class EmployeeResponse(BaseModel):
    """Schema de respuesta para un empleado (lo que retorna la API)."""

    id: int
    full_name: str
    email: str
    phone: str | None
    position: str | None
    department: str | None
    hire_date: date
    salary: float | None
    status: str

    class Config:
        from_attributes = True
