"""Módulos de servicios y reglas de negocio del sistema."""
from app.services.agenda_service import agendar_cita, cancelar_cita, obtener_agenda_diaria
from app.services.atencion_service import registrar_atencion_medica, obtener_historial_clinico_mascota
from app.services.exceptions import (
    ReglaNegocioError,
    CruceHorarioError,
    MascotaFallecidaError,
    FueraDeJornadaError,
    EntidadNoEncontradaError
)

__all__ = [
    "agendar_cita",
    "cancelar_cita",
    "obtener_agenda_diaria",
    "registrar_atencion_medica",
    "obtener_historial_clinico_mascota",
    "ReglaNegocioError",
    "CruceHorarioError",
    "MascotaFallecidaError",
    "FueraDeJornadaError",
    "EntidadNoEncontradaError"
]