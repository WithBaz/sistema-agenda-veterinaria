"""Router para atención clínica registrada, prescripciones médicas e historial."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.atencion import (
    AtencionCreate,
    AtencionResponse,
    HistorialClinicoMascotaResponse
)
from app.services.atencion_service import (
    registrar_atencion_medica,
    obtener_historial_clinico_mascota
)

router = APIRouter(prefix="/atenciones", tags=["Atención Clínica e Historial Médico"])

@router.post(
    "/",
    response_model=AtencionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar cierre médico de una cita y generar prescripciones farmacológicas",
    description=(
        "Registra los hallazgos clínicos, diagnóstico y medicamentos recetados tras una cita. "
        "La cita pasa automáticamente a estado 'completada' y la información se consolida en el historial."
    )
)
def crear_atencion(payload: AtencionCreate, db: Session = Depends(get_db)):
    prescripciones_dict = [p.model_dump() for p in payload.prescripciones]
    atencion = registrar_atencion_medica(
        db=db,
        cita_id=payload.cita_id,
        diagnostico=payload.diagnostico,
        peso_kg=payload.peso_kg,
        temperatura=payload.temperatura,
        notas_evolucion=payload.notas_evolucion,
        prescripciones=prescripciones_dict
    )
    return atencion

@router.get(
    "/mascota/{mascota_id}/historial",
    response_model=HistorialClinicoMascotaResponse,
    summary="Consultar historial clínico integral de una mascota",
    description=(
        "REGLA DE NEGOCIO: Retorna el historial médico retrospectivo, citas pasadas, diagnósticos "
        "y tratamientos de una mascota. Si la mascota tiene estado 'fallecida', su historial continúa "
        "siendo 100% consultable."
    )
)
def consultar_historial(mascota_id: int, db: Session = Depends(get_db)):
    return obtener_historial_clinico_mascota(db=db, mascota_id=mascota_id)