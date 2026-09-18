"""Registro centralizado de modelos relacionales."""
from app.models.base import Base
from app.models.propietario import Propietario
from app.models.mascota import Mascota
from app.models.profesional import Profesional
from app.models.tipo_consulta import TipoConsulta
from app.models.cita import Cita
from app.models.atencion import AtencionRegistrada
from app.models.prescripcion import PrescripcionMedica

__all__ = [
    "Base",
    "Propietario",
    "Mascota",
    "Profesional",
    "TipoConsulta",
    "Cita",
    "AtencionRegistrada",
    "PrescripcionMedica"
]