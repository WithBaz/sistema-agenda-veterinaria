"""Router para agendamiento y cancelación de citas médicas."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Cita
from app.schemas.cita import CitaCreate, CitaResponse, CitaCancelRequest, CitaCancelResponse
from app.services.agenda_service import agendar_cita, cancelar_cita
from app.services.exceptions import EntidadNoEncontradaError

router = APIRouter(prefix="/citas", tags=["Gestión de Citas Médicas"])

@router.post(
    "/",
    response_model=CitaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agendar una nueva cita médica",
    description=(
        "Aplica las reglas de negocio innegociables: \n"
        "1. Valida que el profesional no tenga citas solapadas.\n"
        "2. Calcula automáticamente el bloque horario a partir de TipoConsulta (20, 30 o 60 min).\n"
        "3. Bloquea el agendamiento si la mascota tiene estado 'fallecida'.\n"
        "4. Valida que el rango esté dentro de la jornada laboral (Lunes a Sábado de 08:00 a 18:00)."
    )
)
def crear_cita(payload: CitaCreate, db: Session = Depends(get_db)):
    nueva_cita = agendar_cita(
        db=db,
        profesional_id=payload.profesional_id,
        mascota_id=payload.mascota_id,
        tipo_consulta_id=payload.tipo_consulta_id,
        fecha_hora_inicio=payload.fecha_hora_inicio,
        motivo=payload.motivo
    )
    return nueva_cita

@router.post(
    "/{cita_id}/cancelar",
    response_model=CitaCancelResponse,
    summary="Cancelar una cita médica (Regla de las 2 horas)",
    description=(
        "Aplica la regla de negocio de cancelación:\n"
        "- Si se solicita con al menos 2 horas de antelación respecto a la hora de inicio, "
        "la cita cambia a estado 'cancelada' y libera el espacio.\n"
        "- Si se solicita con menos de 2 horas de antelación, el sistema rechaza la cancelación "
        "efectiva y registra obligatoriamente la cita como 'inasistencia'."
    )
)
def solicitar_cancelacion_cita(
    cita_id: int,
    payload: CitaCancelRequest = CitaCancelRequest(),
    db: Session = Depends(get_db)
):
    resultado = cancelar_cita(
        db=db,
        cita_id=cita_id,
        fecha_hora_solicitud=payload.fecha_hora_solicitud
    )
    return resultado

@router.get(
    "/{cita_id}",
    response_model=CitaResponse,
    summary="Consultar detalle de una cita específica"
)
def obtener_cita(cita_id: int, db: Session = Depends(get_db)):
    cita = db.query(Cita).filter(Cita.id == cita_id).first()
    if not cita:
        raise EntidadNoEncontradaError(f"No existe ninguna cita con el ID {cita_id}.")
    return cita