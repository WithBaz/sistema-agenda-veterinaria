"""Esquemas Pydantic para atención registrada y prescripciones médicas."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

class PrescripcionCreate(BaseModel):
    """Datos para formular un medicamento."""
    medicamento: str = Field(..., min_length=2, max_length=150)
    dosis: str = Field(..., min_length=2, max_length=100)
    duracion_dias: int = Field(..., ge=1, le=365)
    indicaciones: Optional[str] = Field(None, max_length=500)

class PrescripcionResponse(BaseModel):
    """Detalle de una prescripción médica."""
    id: int
    atencion_id: int
    medicamento: str
    dosis: str
    duracion_dias: int
    indicaciones: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class AtencionCreate(BaseModel):
    """Datos requeridos para el cierre clínico de una cita."""
    cita_id: int
    peso_kg: Optional[float] = Field(None, ge=0.1, le=200.0)
    temperatura: Optional[float] = Field(None, ge=30.0, le=45.0)
    diagnostico: str = Field(..., min_length=5, description="Diagnóstico clínico del veterinario")
    notas_evolucion: Optional[str] = Field(None, max_length=1000)
    prescripciones: List[PrescripcionCreate] = Field(default_factory=list)

class AtencionResponse(BaseModel):
    """Detalle completo del registro de atención médica."""
    id: int
    cita_id: int
    fecha_registro: datetime
    peso_kg: Optional[float] = None
    temperatura: Optional[float] = None
    diagnostico: str
    notas_evolucion: Optional[str] = None
    prescripciones: List[PrescripcionResponse] = []

    model_config = ConfigDict(from_attributes=True)

class HistorialClinicoMascotaResponse(BaseModel):
    """Historial clínico íntegro de la mascota (accesible incluso si está fallecida)."""
    mascota_id: int
    nombre: str
    especie: str
    raza: Optional[str] = None
    estado_vital: str
    propietario_nombre: str
    total_atenciones: int
    atenciones: List[AtencionResponse]