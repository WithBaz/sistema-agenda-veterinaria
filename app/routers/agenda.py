"""Router para la consulta obligatoria de agenda diaria y cálculo de espacios libres."""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.agenda import AgendaDiariaResponse
from app.services.agenda_service import obtener_agenda_diaria

router = APIRouter(prefix="/agenda", tags=["Agenda y Disponibilidad (Consulta Obligatoria)"])

@router.get(
    "/profesional/{profesional_id}",
    response_model=AgendaDiariaResponse,
    summary="Agenda del día por profesional con espacios libres calculados",
    description=(
        "CONSULTA OBLIGATORIA DEL SISTEMA: Retorna todas las citas programadas de un profesional "
        "para una fecha específica y calcula de forma explícita los intervalos de tiempo libres "
        "disponibles dentro de la jornada laboral de 08:00 a 18:00 (600 minutos)."
    )
)
def consultar_agenda_profesional(
    profesional_id: int,
    fecha: Optional[date] = Query(
        default=None,
        description="Fecha a consultar (formato YYYY-MM-DD). Si se omite, toma la fecha actual."
    ),
    db: Session = Depends(get_db)
):
    if fecha is None:
        fecha = date.today()
    
    return obtener_agenda_diaria(db=db, profesional_id=profesional_id, fecha=fecha)