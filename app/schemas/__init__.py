"""Esquemas Pydantic centralizados."""
from app.schemas.cita import CitaCreate, CitaCancelRequest, CitaResponse, CitaCancelResponse
from app.schemas.agenda import AgendaDiariaResponse, EspacioLibre, CitaAgendaItem
from app.schemas.atencion import (
    PrescripcionCreate,
    PrescripcionResponse,
    AtencionCreate,
    AtencionResponse,
    HistorialClinicoMascotaResponse
)

__all__ = [
    "CitaCreate",
    "CitaCancelRequest",
    "CitaResponse",
    "CitaCancelResponse",
    "AgendaDiariaResponse",
    "EspacioLibre",
    "CitaAgendaItem",
    "PrescripcionCreate",
    "PrescripcionResponse",
    "AtencionCreate",
    "AtencionResponse",
    "HistorialClinicoMascotaResponse"
]