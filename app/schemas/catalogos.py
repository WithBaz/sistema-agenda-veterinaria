"""Esquemas Pydantic para entidades de catálogo y soporte."""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

# Propietario
class PropietarioCreate(BaseModel):
    documento_identidad: str = Field(..., max_length=50)
    nombre_completo: str = Field(..., max_length=150)
    telefono: str = Field(..., max_length=30)
    email: Optional[str] = Field(None, max_length=100)
    direccion: Optional[str] = Field(None, max_length=200)

class PropietarioResponse(BaseModel):
    id: int
    documento_identidad: str
    nombre_completo: str
    telefono: str
    email: Optional[str] = None
    direccion: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Mascota
class MascotaCreate(BaseModel):
    propietario_id: int
    nombre: str = Field(..., max_length=100)
    especie: str = Field(..., max_length=50)
    raza: Optional[str] = Field(None, max_length=100)
    fecha_nacimiento: Optional[date] = None
    estado_vital: str = Field("viva", description="'viva' o 'fallecida'")
    notas_alergias: Optional[str] = None

class MascotaResponse(BaseModel):
    id: int
    propietario_id: int
    nombre: str
    especie: str
    raza: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    estado_vital: str
    notas_alergias: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Profesional
class ProfesionalCreate(BaseModel):
    documento_identidad: str = Field(..., max_length=50)
    nombre_completo: str = Field(..., max_length=150)
    especialidad: str = Field(..., max_length=100)
    telefono: str = Field(..., max_length=30)
    email: Optional[str] = Field(None, max_length=100)
    activo: bool = True

class ProfesionalResponse(BaseModel):
    id: int
    documento_identidad: str
    nombre_completo: str
    especialidad: str
    telefono: str
    email: Optional[str] = None
    activo: bool
    model_config = ConfigDict(from_attributes=True)

# TipoConsulta
class TipoConsultaCreate(BaseModel):
    nombre: str = Field(..., max_length=100)
    duracion_minutos: int = Field(..., gt=0, le=480)
    descripcion: Optional[str] = Field(None, max_length=255)
    activo: bool = True

class TipoConsultaResponse(BaseModel):
    id: int
    nombre: str
    duracion_minutos: int
    descripcion: Optional[str] = None
    activo: bool
    model_config = ConfigDict(from_attributes=True)