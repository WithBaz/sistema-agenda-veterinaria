"""Esquemas Pydantic para la consulta obligatoria de agenda diaria."""
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

class CitaAgendaItem(BaseModel):
    """Representación de una cita dentro de la agenda diaria."""
    id: int
    mascota_id: int
    mascota_nombre: str
    especie: str
    propietario_nombre: str
    tipo_consulta_nombre: str
    duracion_minutos: int
    fecha_hora_inicio: datetime
    fecha_hora_fin: datetime
    estado: str
    motivo: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class EspacioLibre(BaseModel):
    """Representación explícita de un intervalo libre para atención médica."""
    inicio: str = Field(..., description="Hora de inicio del bloque libre (HH:MM)")
    fin: str = Field(..., description="Hora de fin del bloque libre (HH:MM)")
    duracion_minutos: int = Field(..., description="Duración total en minutos del espacio libre")

class AgendaDiariaResponse(BaseModel):
    """Respuesta de la consulta obligatoria: Agenda del día con espacios libres visibles."""
    profesional_id: int
    profesional_nombre: str
    especialidad: str
    fecha: str
    jornada_laboral: str = Field(default="08:00 - 18:00", description="Horario de atención establecido")
    citas_programadas: List[CitaAgendaItem]
    espacios_libres: List[EspacioLibre]
    minutos_ocupados: int
    minutos_libres: int
    porcentaje_ocupacion: float