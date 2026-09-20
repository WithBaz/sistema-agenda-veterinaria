"""Esquemas Pydantic para la gestión de citas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class CitaCreate(BaseModel):
    """Payload para agendar una nueva cita."""
    profesional_id: int = Field(..., description="ID del profesional veterinario asignado")
    mascota_id: int = Field(..., description="ID de la mascota paciente")
    tipo_consulta_id: int = Field(..., description="ID del tipo de consulta (determina la duración)")
    fecha_hora_inicio: datetime = Field(..., description="Fecha y hora de inicio de la cita")
    motivo: Optional[str] = Field(None, max_length=500, description="Motivo de la consulta")

class CitaCancelRequest(BaseModel):
    """Payload opcional para simular el momento de la solicitud de cancelación."""
    fecha_hora_solicitud: Optional[datetime] = Field(
        None,
        description="Fecha y hora en que se solicita la cancelación. Si es None, se toma el tiempo actual."
    )

class CitaResponse(BaseModel):
    """Respuesta con el detalle estructurado de una cita."""
    id: int
    profesional_id: int
    mascota_id: int
    tipo_consulta_id: int
    fecha_hora_inicio: datetime
    fecha_hora_fin: datetime
    estado: str
    motivo: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CitaCancelResponse(BaseModel):
    """Resultado del proceso de cancelación de cita según la regla de las 2 horas."""
    cita_id: int
    estado_anterior: str
    nuevo_estado: str
    mensaje: str
    horas_anticipacion: float